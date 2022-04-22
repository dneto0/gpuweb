#!/usr/bin/env python3
#
# Copyright 2022 Google LLC
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of works must retain the original copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the original
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#
# 3. Neither the name of the W3C nor the names of its contributors
# may be used to endorse or promote products derived from this work
# without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


"""
Represent and process a grammar:
- Canonicalize
- Compute First and Follow sets
- Compute LL(1) parser table and associated conflicts
- TODO: Determine lookahead required for an LALR(1) parser
- TODO: Verify the language is LALR(1) with context-sensitive lookahead
"""

import json
import functools

EPSILON = u"\u03b5"
MIDDLE_DOT = u"\u00b7"
# The name of the nonterminal for the entire language
LANGUAGE = "language"

# Definitions:
#
#  Token: A non-empty sequence of code points. Parsing considers tokens to
#    be indivisibl.
#
#  Empty: A unique object representing the empty string. Sometimes shown as
#    epsilon.
#
#  EndOfText: A unique object representing the end of input. No more text may
#    appear after it.
#
#  Fixed: A Token with fixed spelling.
#
#  Pattern: A Token matching a particular regular expression.
#    We always assume patterns never map to the empty string.
#
#  Terminal: One of: Token, EndOfText
#
#  Nonterminal: A grammar object which can expand to phrases, as defined by
#    production rules.
#
#  Symbol: A name for a Terminal or Nonterminal.
#
#  Choice: A Rule which matches when any of several children matches
#
#  Seq (Sequence): A Rule which matches when all children are matched, one after
#    another
#
#  Repeat1: A Rule which matches when its child matches one or more times.
#
#  ContainerRule: One of Choice, Seq, or Repeat1
#
#  Production: An expression of Choice, Sequence, Repeat1 expressions over
#    Terminals, Nonterminals, and Empty.  In these expressions, a Nonterminal is
#    represented by a Symbol for its name.
#
#  Flat: A Production is "Flat" if it is one of:
#      - a Terminal
#      - a Symbol
#      - Empty
#      - a Sequence over Terminals and Symbols
#
#  GrammarDict: a dictionary mapping over Python strings mapping:
#    A Terminal name to its definition.
#    A Nonterminal name to its Productions.
#
#  Grammar:
#    A Python object of class Grammar, including members:
#      .rules: a GrammarDict
#      .empty: the unique Empty object
#      .end_of_text: the unique EndOfText object
#      .start_symbol: the Python string name of the start symbol
#
#  Canonical Form: a GrammarDict where the Productions for Nonterminals are:
#    A Choice over Flat Productions
#
#  Phrase: A sequence of Terminals and Nonterminals, or a single Empty
#    It might have length 0, i.e. no objects at all.
#
#  Sentence: A sequence of Tokens. (Each Sentence is a Phrase.)
#
#  Language: The set of Sentences which may be derived from the start
#    symbol of a Grammar.
#
#  First(X):  Where X is a Phrase, First(X) is the set over Terminals or Empty that
#    begin the Phrases that may be derived from X.

class Rule:
    def __init__(self):
        self.name = self.__class__.__name__
        self.first = set()
        self.follow = set()
        self.known_to_derive_empty = False

    def is_empty(self):
        return isinstance(self, Empty)

    def is_terminal(self):
        return isinstance(self, (EndOfText, Token))

    def is_nonterminal(self):
        return isinstance(self, ContainerRule)

    def is_symbol(self):
        return isinstance(self, Symbol)

    def derives_empty(self):
        """Returns True if this object is known to generate the empty string"""
        if self.known_to_derive_empty:
            return True
        for item in self.first:
            if item.is_empty():
                self.known_to_derive_empty = True
                return True
        return False

    def _class_less(self,other):
        rank = { Choice: 1, Seq: 2, Repeat1: 3, Symbol: 5, Fixed: 10, Pattern: 20, Empty: 100, EndOfText: 1000 }
        return rank[self.__class__] < rank[other.__class__]


    # Runs a given function 'fn' on this node and its descendants.
    # The fn(self,True) is called on entry and fn(self,False) on exit.
    def traverse(self,fn):
        fn(self,True)
        if "children" in dir(self):
            for c in self.children:
                c.traverse(fn)
        fn(self,False)

    def __str__(self):
        parts = []
        def f(parts,obj,on_entry):
            if "content" in dir(obj):
                if on_entry:
                    if isinstance(obj, Symbol):
                        parts.append(obj.content)
                    elif isinstance(obj, Fixed):
                        parts.append("'{}'".format(obj.content))
                    elif isinstance(obj, Pattern):
                        parts.append("/{}/".format(obj.content))
                    elif obj.is_empty():
                        parts.append(EPSILON)
                    elif isinstance(obj, EndOfText):
                        parts.append(obj.name)
                    else:
                        parts.extend(["(",obj.name, str(obj.content),")"])
            else:
                if on_entry:
                    parts.extend(["(",obj.name])
                else:
                    parts.append(")")
        self.traverse(lambda obj, on_entry: f(parts,obj,on_entry))
        return " ".join(parts)

@functools.total_ordering
class ContainerRule(Rule):
    """A ContainerRule is a rule with children"""
    def __init__(self,children):
        super().__init__()
        self.children = children

    def ordered(self):
        return self.ordered_children if ('ordered_children' in dir(self)) else self.children

    def __eq__(self,other):
        if not isinstance(other, self.__class__):
            return False
        if len(self.children) is not len(other.children):
            return False
        ours = self.ordered()
        theirs = other.ordered()
        return all([(ours[i] == theirs[i]) for i in range(len(ours))])

    def __lt__(self,other):
        # Order by class
        if self._class_less(other):
            return True
        if other._class_less(self):
            return False
        ours = self.ordered()
        theirs = other.ordered()
        for i in range(min(len(ours), len(theirs))):
            if ours[i] < theirs[i]:
                return True
            if theirs[i] < ours[i]:
                return False
        return len(ours) < len(theirs)

    def __hash__(self):
        return str(self).__hash__()

    # Emulate an indexable sequence by adding certain standard methods:
    def __len__(self):
        return self.children.__len__()

    def __length_hint__(self):
        return self.children.__length_hint__()

    def __getitem__(self,key):
        return self.children.__getitem__(key)

    def __setitem__(self,key,value):
        self.children.__setitem__(key,value)

    def __delitem__(self,key):
        self.children.__setitem__(key)

    def __missing__(self,key):
        return self.children.__missing__(key)

    def __iter__(self):
        return self.children.__iter__()

    def __contains__(self,item):
        return self.children.__contains__(item)

@functools.total_ordering
class LeafRule(Rule):
    """A LeafRule is a rule without children"""
    def __init__(self,content):
        super().__init__()
        self.content = content

    def __eq__(self,other):
        return isinstance(other, self.__class__) and (self.content == other.content)

    def __hash__(self):
        return str(self).__hash__()

    def __lt__(self,other):
        # Order by class
        if self._class_less(other):
            return True
        if other._class_less(self):
            return False
        if self.content is None:
            return other.content is not None
        if other.content is None:
            return True
        return self.content < other.content

class Token(LeafRule):
    """A Token represents a non-empty contiguous sequence of code points"""
    def __init__(self,content):
        super().__init__(content)

class Choice(ContainerRule):
    def __init__(self,children):
        super().__init__(children)
        # Order does not matter among the children. 
        # Store them in order so we can more quickly test for equality
        # and less-than.
        self.ordered_children = sorted(self.children)

class Seq(ContainerRule):
    def __init__(self,children):
        super().__init__(children)

class Repeat1(ContainerRule):
    def __init__(self,children):
        super().__init__(children)
        if len(children) != 1:
            raise RuntimeError("Repeat1 must have exactly one child: {}".format(str(children)))

class Symbol(LeafRule):
    def __init__(self,content):
        super().__init__(content)

class Fixed(Token):
    def __init__(self,content):
        super().__init__(content)

class Pattern(Token):
    def __init__(self,content):
        super().__init__(content)

class Empty(LeafRule):
    def __init__(self):
        super().__init__(None)

class EndOfText(LeafRule):
    def __init__(self):
        super().__init__(None)

class Action:
    """
    A parser action
    """
    def __init(self):
        pass

class Reduce(Action):
    """
    A Reduce parser action
    Reduce('lhs',rhs) replaces the sequence of symbols in the RHS with
    the non-terminal named 'lhs'.

    Args:
      non_terminal: the name of the non_terminal being reduced
      rhs: a Rule: either a terminal, or a Seq of terminals and symbols
    """
    def __init__(self,non_terminal,rhs):
        # The name of the non-terminal, as a Python string
        self.non_terminal = non_terminal
        self.rhs = rhs

    def __str__(self):
        return "{} -> {}".format(self.non_terminal, str(self.rhs))


@functools.total_ordering
class Item():
    """
    An SLR Item is a non-terminal name, and a Flat Production with a
    single position marker.

    If there are N objects in the production, the marked position
    is an integer between 0 and N inclusive, indicating the number
    of objects that precede the marked position.
    """
    def __init__(self,lhs,rule,position):
        """
        Args:
            lhs: the name of the nonterminal, as a Python string or a Symbol
            rule: the Flat Production
            position: Index of the position, where 0 is to the left
              of the first item in the choice
        """
        self.lhs = lhs if isinstance(lhs,Symbol) else Symbol(lhs)
        self.rule = rule

        # self.items is the sub-objects, as a list
        if rule.is_terminal():
            self.items = [rule]
        elif rule.is_symbol():
            self.items = [rule]
        elif rule.is_empty():
            self.items = []
        elif isinstance(rule, Seq):
            self.items = [i for i in rule]
        else:
            raise RuntimeError("invalid item object: {}".format(str(rule)))

        self.position = position
        if (self.position < 0) or (self.position > len(self.items)):
            raise RuntimeError("invalid position {} for production: {}".format(position, str(rule)))

    def __str__(self):
        parts = ["{} ->".format(self.lhs)]
        parts.extend([str(i) for i in self.items])
        parts.insert(1 + self.position, MIDDLE_DOT)
        return " ".join(parts)

    def __eq__(self,other):
        return (self.lhs == other.lhs) and (self.rule == other.rule) and (self.position == other.position)

    def __hash__(self):
        return str(self).__hash__()

    def __lt__(self,other):
        if self.lhs < other.lhs:
            return True
        if other.lhs < self.lhs:
            return False
        if self.rule < other.rule:
            return True
        if other.rule < self.rule:
            return False
        if self.position < other.position:
            return True
        if other.position < self.position:
            return False
        return False

    def is_kernel(self):
        # A kernel item either:
        # - has the dot not at the left end, or:
        # - is the production representing the entire language:
        #   LANGUAGE => Seq( Grammar.start_symbol, EndOfText )
        return (self.position > 0) or (self.lhs.content == LANGUAGE)


def json_hook(grammar,memo,tokens_only,dct):
    """
    Translates a JSON dictionary into a corresponding grammar node, based on
    the 'type' entry.
    Returns 'dct' itself when 'dct' has no type entry or has an unrecognized
    type entry.

    Args:
      grammar: The grammar in which this node is created.
      memo: A memoization dictionary of previously created nodes.
        It's a dictionary mapping the Python string name of a node to
        the previously created node, if any.
      tokens_only: if true, only resolve tokens
      dct: A JSON dictionary

    Returns: A grammar node if recognized, otherwise 'dct' itself.
    """

    def memoize(memo,name,node):
        if name in memo:
            return memo[name]
        memo[name] = node
        return node

    result = dct
    if "type" in dct:
        if  dct["type"] == "TOKEN":
            # Return the content itself. Don't wrap it.
            result = dct["content"]
        elif  dct["type"] == "STRING":
            result = memoize(memo,dct["value"],Fixed(dct["value"]))
        elif  dct["type"] == "PATTERN":
            result = memoize(memo,dct["value"],Pattern(dct["value"]))
        elif not tokens_only:
            if  dct["type"] == "BLANK":
                result = grammar.empty
            elif  dct["type"] == "CHOICE":
                result = Choice(dct["members"])
            elif  dct["type"] == "SEQ":
                result = Seq(dct["members"])
            elif  dct["type"] == "REPEAT1":
                result = Repeat1([dct["content"]])
            elif  dct["type"] == "SYMBOL":
                result = memoize(memo,dct["name"],Symbol(dct["name"]))
    return result

def canonicalize_grammar(rules,empty):
    """
    Computes the Canonical Form of a GrammarDict

    Args:
        rules: A dictionary mapping rule names to Rule objects
        empty: the unique Empty object to use

    Returns:
        A GrammarDict matching the same language, but in Canonical Form.
    """

    # First ensure right-hand sides of containers are Choice nodes.
    result = {}
    for key, value in rules.items():
        if isinstance(value,ContainerRule):
            if isinstance(value,Choice):
                # Choice nodes are unchanged
                result[key] = value
            else:
                result[key] = Choice([value])
        else:
            result[key] = value

    # Now iteratively simplify rules.
    # Replace a complex sub-component with a new rule.
    # Repeat until settling.
    keep_going = True
    while keep_going:
        keep_going = False
        rules = dict(result)

        for key, value in rules.items():
            if isinstance(value,LeafRule):
                result[key] = value
            else:
                # The value is a Choice
                made_a_new_one = False
                parts = []
                def add_rule(key,*values):
                    """
                    Records a new rule with the given key and value.

                    Args:
                        key: A Symbol whose name is the key into the result
                            dictionary
                        values: A list of alternatives

                    Returns: The key's Symbol
                    """
                    rhs = Choice(list(values))
                    result[key.content] = rhs
                    return key
                for i in range(len(value)):
                    item = value[i]
                    item_key = Symbol("{}/{}".format(key,str(i)))
                    if isinstance(item,LeafRule):
                        parts.append(item)
                    elif isinstance(item,Repeat1):
                        #   value[i] -> X+
                        # becomes
                        #   value[i] -> value.i
                        #   value.i -> X value.i
                        #   value.i -> epsilon
                        x = item[0]
                        parts.append(add_rule(item_key,
                                              Seq([x,item_key]),
                                              empty))
                        made_a_new_one = True
                    elif isinstance(item,Choice):
                        # Sub-Choices expand in place.
                        parts.extend(item)
                        made_a_new_one = True
                    elif isinstance(item,Seq):
                        # Expand non-leaf elements
                        made_a_new_seq_part = False
                        seq_parts = []
                        for j in range(len(item)):
                            seq_item = item[j]
                            seq_item_key = Symbol(
                                    "{}/{}.{}".format(key,str(i),str(j)))
                            if isinstance(seq_item,LeafRule):
                                seq_parts.append(seq_item)
                            else:
                                seq_parts.append(
                                        add_rule(seq_item_key,seq_item))
                                made_a_new_seq_part = True
                        if made_a_new_seq_part:
                            parts.append(Seq(seq_parts))
                            made_a_new_one = True
                if made_a_new_one:
                    rhs = Choice(parts)
                    result[key] = rhs
                    keep_going = True
                else:
                    result[key] = value

    return result


def compute_first_sets(grammar,rules):
    """
    Computes the First set for each node in the grammar.
    Populates the `first` attribute of each node.

    Args:
        rules: a GrammarDict in Canonical Form
    """

    names_of_non_terminals = []
    grammar.end_of_text.first = set({grammar.end_of_text})
    grammar.empty.first = set({grammar.empty})
    for key, rule in rules.items():
        if rule.is_terminal() or rule.is_empty():
            # If X is a terminal, then First(X) is {X}
            rule.first = set({rule})
        elif rule.is_symbol():
            pass
        else:
            # rule is a Choice node
            for rhs in rule:
                # If X -> empty is a production, then add Empty
                if rhs.is_empty():
                    rule.first = set({rhs})
            names_of_non_terminals.append(key)

    def lookup(rule):
        return rules[rule.content] if isinstance(rule,Symbol) else rule

    def dynamic_first(rule,depth):
        """
        Returns the currently computed approximation to the First set for a
        rule.

        The rule is from a Canonical grammar, so a non-terminal can be as
        complex as a Choice over Sequences over symbols that may reference
        other non-terminals.  Gather updated First set info for at most
        those first two levels, and use a previous-computed approximation for
        the nonterminals at that second level.

        Args:
            rule: the Rule in question
            depth: recursion depth

        Returns:
            A new approximation to the First set for the given rule.
        """

        if rule.is_symbol():
            return rules[rule.content].first
        if rule.is_empty():
            return rule.first
        if rule.is_terminal():
            return rule.first
        if isinstance(rule,Choice):
            result = rule.first
            #for item in [lookup(i) for i in rule]:
            for item in rule:
                result = result.union(dynamic_first(item,depth+1))
            return result
        if isinstance(rule,Seq):
            result = rule.first

            # Only recurse 2 levels deep
            if depth < 2:
                items = [lookup(item) for item in rule]
            else:
                items = rule
            # Add the first sets for Yi if all the earlier items can derive
            # empty.  But don't add empty itself from this prefix.
            for item in items:
                from_first = dynamic_first(item,depth+1)
                from_first = without_empty(from_first)
                result = result.union(from_first)
                if not item.derives_empty():
                    # Not known to derive empty. Stop here.
                    break
            # If all the items derive empty, then add Empty to the first set.
            if all([lookup(item).derives_empty() for item in rule]):
                result = result.union({grammar.empty})
            return result
        raise RuntimeError("trying to dynamically compute the First set of: "
                + str(rule))

    # Repeat until settling.
    keep_going = True
    while keep_going:
        keep_going = False
        for key in names_of_non_terminals:
            rule = rules[key]
            # Accumulate First items from right-hand sides
            new_items = dynamic_first(rule,0) - rule.first
            if len(new_items) > 0:
                rule.first = rule.first.union(new_items)
                keep_going = True


def without_empty(s):
    """
    Returns a copy of set s without Empty
    """
    result = set()
    for i in s:
        if not i.is_empty():
            result.add(i)
    return result


def derives_empty(rules,phrase):
    """
    Args:
        args: a GrammarDict in Canonical form, with First sets computed
        phrase: a sequence of rules

    Returns:
        True if the phrase derives the empty string.
    """
    def lookup(rule):
        return rules[rule.content] if isinstance(rule,Symbol) else rule

    return all([lookup(i).derives_empty() for i in phrase])


def first(grammar,phrase):
    """
    Computes the First set for a Phrase, in the given grammar

    Args:
        grammar: a Grammar
        phrase: a sequence of terminals and non-terminals

    Returns:
        The First set for the phrase
    """
    def lookup(rule):
        return grammar.rules[rule.content] if isinstance(rule,Symbol) else rule

    # Map names of nonterminals to the nonterminals themselves
    phrase = [lookup(i) for i in phrase]

    result = set()
    for item in phrase:
        we = without_empty(item.first)
        result = result.union(we)
        if not item.derives_empty():
            break
    if derives_empty(grammar.rules,phrase):
        result.add(grammar.empty)
    return result


def compute_follow_sets(grammar):
    """
    Computes the Follow set for each node in the grammar.
    Assumes First sets have been computed.
    Populates the `follow` attribute of each node.

    Args:
        grammar: a Grammar in Canonical Form, with First sets populated
    """
    grammar.rules[grammar.start_symbol].follow = set({grammar.end_of_text})

    def lookup(rule):
        return grammar.rules[rule.content] if isinstance(rule,Symbol) else rule

    def process_seq(key,seq,keep_going):
        """
        Add to Follow sets by processing the given Seq node.

        Args:
            key: Python string name for the production
            seq: a Seq rule for the production
            keep_going: A boolean

        Returns:
            True if a Follow set was modified.
            keep_going otherwise
        """

        # Process indirections through symbols
        seq = [lookup(i) for i in seq]

        for bi in range(0,len(seq)):
            b = seq[bi]
            # We only care about nonterminals in the sequence
            if b.is_terminal() or b.is_empty():
                continue

            # If there is a production A -> alpha B beta
            # then everything in First(beta) except Empty is
            # added to Follow(B)
            beta = seq[bi+1:len(seq)]
            first_beta = first(grammar, beta)
            new_items = without_empty(first_beta) - b.follow
            if len(new_items) > 0:
                keep_going = True
                b.follow = b.follow.union(new_items)

            # If A -> alpha B, or A -> alpha B beta, where First(B)
            # contains epsilon, then add Follow(A) to Follow(B)
            if derives_empty(grammar.rules,beta):
                new_items = grammar.rules[key].follow - b.follow
                if len(new_items) > 0:
                    keep_going = True
                    b.follow = b.follow.union(new_items)

        return keep_going


    # Iterate until settled
    keep_going = True
    while keep_going:
        keep_going = False
        for key, rule in grammar.rules.items():
            if rule.is_terminal() or rule.is_symbol() or rule.is_empty():
                continue
            # We only care about sequences
            for seq in filter(lambda i: isinstance(i,Seq), rule):
                keep_going = process_seq(key,seq,keep_going)


def dump_rule(key,rule):
    print("{}  -> {}".format(key,str(rule)))
    print("{} .first: {}".format(key, [str(i) for i in rule.first]))
    print("{} .derives_empty: {}".format(key, str(rule.derives_empty())))
    print("{} .follow: {}".format(key, [str(i) for i in rule.follow]))


def dump_grammar(rules):
    for key, rule in rules.items():
        dump_rule(key,rule)

def walk(obj,dict_fn):
    """
    Walk a JSON structure, yielding a new copy of the object.
    But for any dictionary 'd', first walk its contents, and then
    yield the result of calling dict_fn(d).
    """
    if isinstance(obj,dict):
        result = dict()
        for key, value in obj.items():
            result[key] = walk(value, dict_fn)
        return dict_fn(result)
    if isinstance(obj,list):
        return [walk(i,dict_fn) for i in obj]
    return obj


class LookaheadSet(set):
    """
    A LookaheadSet is a set of terminals
    """
    def __str__(self):
        return "{{}}".format(" ".join([str(i) for i in self]))

class ItemSet(dict):
    """
    An ItemSet is an LR(1) set of Items, where each item maps to its lookahead set.
    """
    def __str__(self):
        parts = []
        for item, lookahead in self.items():
            parts.append("{} : {{}}".format(str(item), str(lookahead)))
        return "\n".join(parts)

    def close(self,grammar):
        """
        Update this set with the closure of items in itself, with respect to the
        given grammar.
        """
        keep_going = True
        while keep_going:
            keep_going = False
            copy = self.copy()
            for item, lookahead in copy.items():
                if item.position >= len(item.items):
                    continue
                B = item.items[item.position]
                afterB = item.items[item.position+1:]
                if not B.is_symbol():
                    continue
                for a in lookahead:
                    suffix = [i for i in afterB]
                    suffix.append(a)
                    for b in first(grammar, suffix):
                        # For each production B -> B_prod in G'
                        rhs = grammar.rules[B.content]
                        rhs = grammar.rules[rhs.content] if rhs.is_symbol() else rhs
                        for B_prod in rhs:
                            candidate = Item(B,B_prod,0)
                            if candidate not in self:
                                self[candidate] = LookaheadSet({b})
                                keep_going = True
                            else:
                                if b not in self[candidate]:
                                    self[candidate].add(b)
                                    keep_going = True


class Grammar:
    """
    A Grammar represents a language generated from a start symbol via
    a set of rules.
    Rules are either Terminals or Nonterminals.
    """

    def Load(json_text, start_symbol, ignore='_reserved'):
        """
        Loads a grammar from text.

        Args:
           json_text: The grammar in JSON form, as emitted by
             a Treesitter generation step.
           start_symbol: The name of the start symbol, as a Python string
           ignore: the name of a rule to ignore completely

        Returns:
            A canonical grammar with first and follow sets
        """
        g = Grammar(json_text, start_symbol, ignore=ignore)
        g.canonicalize()
        g.compute_first()
        g.compute_follow()
        return g

    def find(self, rule_name):
        return self.rules[rule_name]

    def __init__(self, json_text, start_symbol, ignore='_reserved'):
        """
        Args:
           json_text: The grammar in JSON form, as emitted by
             a Treesitter generation step.
           start_symbol: The name of the start symbol, as a Python string
           ignore: the name of a rule to ignore completely
        """
        self.json_text = json_text
        self.start_symbol = start_symbol
        self.empty = Empty()
        self.end_of_text = EndOfText()

        # First decode it without any interpretation.
        pass0 = json.loads(json_text)
        # Remove any rules that should be ignored
        # The WGSL grammar has _reserved, which includes 'attribute' but
        # that is also the name of a different grammar rule.
        if ignore in pass0["rules"]:
            del pass0["rules"][ignore]

        # Now decode, transforming leaves and nonterminals to Rule objects.
        memo = {} # memoization table used during construction
        pass1 = walk(pass0, lambda dct: json_hook(self,memo,True,dct))
        pass2 = walk(pass1, lambda dct: json_hook(self,memo,False,dct))
        self.json_grammar = pass2

        self.rules = self.json_grammar["rules"]

        # Augment the grammar:
        self.rules[LANGUAGE] = Seq([Symbol(start_symbol), self.end_of_text])

    def canonicalize(self):
        self.rules = canonicalize_grammar(self.rules,self.empty)

    def compute_first(self):
        compute_first_sets(self, self.rules)

    def compute_follow(self):
        compute_follow_sets(self)

    def dump(self):
        """
        Emits the internal representation of the grammar to stdout
        """
        dump_grammar(self.rules)

    def pretty_str(self):
        """
        Returns a pretty string form of the grammar.
        It's still in canonical form: nonterminals are at most a choice over
        a sequence of leaves.
        """
        def pretty_str(rule):
            """Returns a pretty string for a node"""
            if rule.is_terminal() or rule.is_empty():
                return str(rule)
            if rule.is_symbol():
                return rule.content
            if isinstance(rule,Choice):
                return " | ".join([pretty_str(i) for i in rule])
            if isinstance(rule,Seq):
                return " ".join([pretty_str(i) for i in rule])
            raise RuntimeError("unexpected node: {}".format(str(rule)))

        parts = []
        for key in sorted(self.rules):
            parts.append("{}: {}\n".format(key,pretty_str(self.rules[key])))
        return "".join(parts)

    def LL1(self):
        """
        Constructs an LL(1) parser table and associated conflicts (if any).

        Args:
            self: Grammar in canonical form with First and Follow
            sets computed.

        Returns: a 2-tuple:
            an LL(1) parser table
                Key is tuple (lhs,rhs) where lhs is the name of the nonterminal
                and rhs is the Rule for the right-hands side being reduced:
                It may be a Symbol, a Token, or a Sequence of Symbols and Tokens
            a list of conflicts
        """

        conflicts = []
        table = dict()
        def add(lhs,terminal,action):
            action_key = (lhs,terminal)
            if action_key in table:
                # Record the conflict, and only keep the original.
                prev = table[action_key]
                conflicts.append((lhs,terminal,prev,action))
            else:
                table[action_key] = action

        for lhs, rule in self.rules.items():
            if rule.is_nonterminal():
                # Top-level terminals are Choice nodes.
                if not isinstance(rule,Choice):
                    raise RuntimeException("expected Choice node for "+
                       +"'{}' rule, got: {}".format(lhs,rule))
                # For each terminal A -> alpha, 
                for rhs in rule:
                    # For each terminal x in First(alpha), add
                    # A -> alpha to M[A,x]
                    phrase = rhs if rhs.is_nonterminal() else [rhs]
                    for x in first(self,phrase):
                        if x.is_empty():
                            for f in rule.follow:
                                add(lhs,f,Reduce(lhs,rhs))
                        else:
                            add(lhs,x,Reduce(lhs,rhs))
        return (table,conflicts)

    def LALR1(self):
        """
        Constructs an LALR(1) parser table and associated conflicts (if any).

        Args:
            self: Grammar in canonical form with First and Follow
            sets computed.

        Returns: a 2-tuple:
            an LALRL(1) parser table...
            a list of conflicts
        """

        # Build the LR(1) sets of items.  But when making a new set Y
        # merge it into an existing one X if they have the same "core".
        # Here, a "core" of a set are the items which are either:
        #     the entire-language rule:     Seq(start_symbol, EndOfText())
        # or, have the "dot" not at the left end.

        # The root item is the one representing the entire language.
        # Since the grammar is in canonical form, it's a Choice over a
        # single sequence.
        root = Item(LANGUAGE, self.rules[LANGUAGE][0],0)

        # An ItemSet can be found by any of the items in its core.
        # Within an ItemSet, an item maps to its lookahead set.

        item_to_set = ItemSet()
        item_to_set[root] = LookaheadSet({EndOfText()})

        print(str(item_to_set))
        item_to_set.close(self)
        print("===")
        print(str(item_to_set))
        return ("not finished",[])

