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
        self.name = "<rule superclass>"

    def children(self):
        if "children" in dir(self):
            return self.children
        return []

    # Apply fn over all my children
    def preorder(self,fn):
        fn(self)
        for c in self.children():
            fn(c)

class Empty(Rule):
    def __init__(self):
        self.name = "Empty"
        self.children = []

    def __str__(self):
        return "Empty"

class Choice:
    def __init__(self,children):
        self.name = "Choice"
        self.children = children

    def __str__(self):
        return "Choice(...)"

class Seq:
    def __init__(self,children):
        self.name = "Seq"
        self.children = children

    def __str__(self):
        return "Seq(...)"

class Repeat1:
    def __init__(self,children):
        self.name = "Repeat1"
        self.children = children

    def __str__(self):
        return "Repeat1(...)"

class String:
    def __init__(self,content):
        self.name = "String"
        self.content = content

    def __str__(self):
        return "String({})".format(str(self.content))

class Pattern:
    def __init__(self,content):
        self.name = "Pattern"
        self.content = content

    def __str__(self):
        return "Pattern({})".format(str(self.content))

class Symbol:
    def __init__(self,content):
        self.name = "Symbol"
        self.content = content

    def __str__(self):
        return "Symbol({})".format(str(self.content))

class Token:
    def __init__(self,content):
        self.name = "Token"
        self.content = content

    def __str__(self):
        return "Token({})".format(str(self.content))

def json_hook(dct):
    """Translate a JSON Dict"""
    result = dct
    if "type" in dct:
        print("TYPE: "+str(dct["type"]))
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
            result = Repeat1(dct["content"])
        if  dct["type"] == "SYMBOL":
            result = Symbol(dct["name"])
    #print(str(result)+"\n")
    return result


def main():
    argparser = argparse.ArgumentParser(description=inspect.getdoc(sys.modules[__name__]))
    argparser.add_argument('json_file',nargs='?',default='grammar/src/grammar.json',
                           help='file holding the JSON form of the grammar')
    args = argparser.parse_args()
    with open(args.json_file) as infile:
        json_text = "".join(infile.readlines())
    g = json.loads(json_text, object_hook=json_hook)
    #print(str(g))
    print(str(g["rules"]))
    sys.exit(0)


if __name__ == '__main__':
    main()
