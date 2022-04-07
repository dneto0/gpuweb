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
                    parts.extend(["(",obj.name, str(obj.content),")"])
            else:
                if on_entry:
                    parts.extend(["(",obj.name])
                else:
                    parts.append(")")
        self.traverse(lambda obj, on_entry: f(parts,obj,on_entry))
        return " ".join(parts)

class ContainerRule(Rule):
    def __init__(self,children):
        super().__init__()
        self.children = children

class LeafRule(Rule):
    def __init__(self,content):
        super().__init__()
        self.content = content


class Choice(ContainerRule):
    def __init__(self,children):
        super().__init__(children)

class Seq(ContainerRule):
    def __init__(self,children):
        super().__init__(children)

class Repeat1(ContainerRule):
    def __init__(self,children):
        super().__init__(children)



class Empty(LeafRule):
    def __init__(self):
        super().__init__(None)

class String(LeafRule):
    def __init__(self,content):
        super().__init__(content)

class Pattern(LeafRule):
    def __init__(self,content):
        super().__init__(content)

class Symbol(LeafRule):
    def __init__(self,content):
        super().__init__(content)

class Token(LeafRule):
    def __init__(self,content):
        super().__init__(content)


def json_hook(dct):
    """Translate a JSON Dict"""
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
            result = Token(dct["content"])
        if  dct["type"] == "PATTERN":
            result = Pattern(dct["value"])
        if  dct["type"] == "REPEAT1":
            result = Repeat1([dct["content"]])
        if  dct["type"] == "SYMBOL":
            result = Symbol(dct["name"])
    return result


def main():
    argparser = argparse.ArgumentParser(description=inspect.getdoc(sys.modules[__name__]))
    argparser.add_argument('json_file',nargs='?',default='grammar/src/grammar.json',
                           help='file holding the JSON form of the grammar')
    args = argparser.parse_args()
    with open(args.json_file) as infile:
        json_text = "".join(infile.readlines())
    g = json.loads(json_text, object_hook=json_hook)
    rules = g["rules"]
    for key, value in rules.items():
        print("{}: {}".format(key,str(value)))
    sys.exit(0)


if __name__ == '__main__':
    main()
