#!/usr/bin/env python3
"""
Verify the WGSL grammar is LL(1) and LALR(1)
"""

import argparse
import inspect
import json
import os
import re
import subprocess
import sys

class Rule:
    def __init__(self):
        self.name = self.__class__.__name__

    def is_token(self):
        return False

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
                    elif isinstance(obj, String):
                        parts.append("'{}'".format(obj.content))
                    elif isinstance(obj, Pattern):
                        parts.append("/{}/".format(obj.content))
                    elif isinstance(obj, Empty):
                        parts.append(u"\u03b5") # Epsilon
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

class ContainerRule(Rule):
    """A ContainerRule is a rule with children"""
    def __init__(self,children):
        super().__init__()
        self.children = children

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

class LeafRule(Rule):
    """A LeafRule is a rule without children"""
    def __init__(self,content):
        super().__init__()
        self.content = content

class Token(LeafRule):
    """A Token represents a non-empty contiguous sequence of code points"""
    def __init__(self,content):
        super().__init__(content)
    def is_token(self):
        return True

class Choice(ContainerRule):
    def __init__(self,children):
        super().__init__(children)

class Seq(ContainerRule):
    def __init__(self,children):
        super().__init__(children)

class Repeat1(ContainerRule):
    def __init__(self,children):
        super().__init__(children)

class Symbol(LeafRule):
    def __init__(self,content):
        super().__init__(content)

class Empty(LeafRule):
    def __init__(self):
        super().__init__(None)

class EndOfText(LeafRule):
    def __init__(self):
        super().__init__(None)

class String(Token):
    def __init__(self,content):
        super().__init__(content)

class Pattern(Token):
    def __init__(self,content):
        super().__init__(content)


def json_hook(dct):
    """
    Translates a JSON dictionary into a corresponding grammar node, based on
    the 'type' entry.
    Returns 'dct' itself when 'dct' has no type entry or has an unrecognized
    type entry.

    Args:
      dct: A JSON dictionary

    Returns: A grammar node if recognized, otherwise 'dct' itself.
    """
    result = dct
    if "type" in dct:
        if  dct["type"] == "STRING":
            result = String(dct["value"])
        if  dct["type"] == "BLANK":
            result = Empty()
        if  dct["type"] == "CHOICE":
            result = Choice(dct["members"])
        if  dct["type"] == "SEQ":
            result = Seq(dct["members"])
        if  dct["type"] == "TOKEN":
            # Return the content itself. Don't wrap it.
            result = dct["content"]
        if  dct["type"] == "PATTERN":
            result = Pattern(dct["value"])
        if  dct["type"] == "REPEAT1":
            result = Repeat1([dct["content"]])
        if  dct["type"] == "SYMBOL":
            result = Symbol(dct["name"])
    return result


def canonicalize_grammar(rules):
    """
    Expands grammar rules into canoncial form.

    Args:
        rules: A dictionary mapping a Symbol node to its right-hand-side.

    Returns:
        A dictionary with entries:
            key: a Symbol naming the left-hand side of a rule.
            value:
                a LeafRule node, or
                a Choice of alternative right-hand sides
        A right-hand-side is a Seq of LeafRule nodes, or the Empty node
    """

    # First ensure right-hand sides of containers are lists.
    result = {}
    for key, value in rules.items():
        if isinstance(value,ContainerRule):
            if isinstance(value,Choice):
                # Choice nodes expand to themselves
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
            #print("{} --> {}".format(str(key),str(value)))
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
                    #print("   {} --> {}".format(str(key),format(rhs)))
                    return key
                for i in range(len(value)):
                    item = value[i]
                    item_key = Symbol("{}.{}".format(key,str(i)))
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
                                              Empty()))
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
                                    "{}.{}={}".format(key,str(i),str(j)))
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

    dump_grammar(result)
    return result


def dump_grammar(rules):
    # Each non-terminal
    for key, value in rules.items():
        print("{}: {}".format(key,str(value)))


def main():
    argparser = argparse.ArgumentParser(
            description=inspect.getdoc(sys.modules[__name__]))
    argparser.add_argument('json_file',
                           nargs='?',
                           default='grammar/src/grammar.json',
                           help='file holding the JSON form of the grammar')
    args = argparser.parse_args()
    with open(args.json_file) as infile:
        json_text = "".join(infile.readlines())
    g = json.loads(json_text, object_hook=json_hook)

    # Agument the grammar.  The start node is followed by an end-of-text marker.
    rules = g["rules"]
    rules["translation_unit"] = Seq([rules["translation_unit"], EndOfText()])

    rules = canonicalize_grammar(rules)

    dump_grammar(rules)
    sys.exit(0)


if __name__ == '__main__':
    main()
