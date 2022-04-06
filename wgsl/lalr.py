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

    # Apply fn over all my children
    def iterate(fn):
        pass

def json_hook(dct):
    """Translate a JSON Dict"""
    if "type" in dct:
        print("TYPE: "+str(dct["type"]))
        return dct


def main():
    argparser = argparse.ArgumentParser(description=inspect.getdoc(sys.modules[__name__]))
    argparser.add_argument('json_file',nargs='?',default='grammar/src/grammar.json',
                           help='file holding the JSON form of the grammar')
    args = argparser.parse_args()
    with open(args.json_file) as infile:
        json_text = "".join(infile.readlines())
    json.loads(json_text, object_hook=json_hook)
    sys.exit(0)


if __name__ == '__main__':
    main()
