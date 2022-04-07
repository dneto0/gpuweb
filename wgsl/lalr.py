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
                        parts.append("\u03b5") # Epsilon
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

    """Emulate an indexable sequence"""
    def __len__(self):
        return self.children.__len__()

    def __length_hint__(self):
        return self.children.__length_hint__()

    def __get_item__(self,key):
        return self.children.__get_item__(key)

    def __set_item__(self,key,value):
        self.children.__set_item__(key,value)

    def __del_item__(self,key):
        self.children.__set_item__(key)

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
    Translates a JSON dictionary into a corresponding grammar node, based on the 'type' field.
    Returns 'dct' itself when 'dct' has no type entry or has an unrecognized type entry.

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
        A right-hand-side is a Seq of LeafRule nodes
    """

    # First ensure right-hand sides of containers are lists.
    result = {}
    for key, value in rules.items():
        if isinstance(value,ContainerRule):
            if isinstance(value, Choice):
                # Choice nodes expand to themselves
                result[key] = value
            else:
                result[key] = Choice([value])
        else:
            result[key] = value

    return result


def main():
    argparser = argparse.ArgumentParser(description=inspect.getdoc(sys.modules[__name__]))
    argparser.add_argument('json_file',nargs='?',default='grammar/src/grammar.json',
                           help='file holding the JSON form of the grammar')
    args = argparser.parse_args()
    with open(args.json_file) as infile:
        json_text = "".join(infile.readlines())
    g = json.loads(json_text, object_hook=json_hook)

    # Agument the grammar.
    rules = g["rules"]
    rules["translation_unit"] = Seq([rules["translation_unit"], EndOfText()])

    rules = canonicalize_grammar(rules)

    # Each non-terminal
    for key, value in rules.items():
        print("{}: {}".format(key,str(value)))
    sys.exit(0)


if __name__ == '__main__':
    main()
