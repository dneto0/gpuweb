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
Analyze a grammar, given in Treesitter JSON form
"""

import argparse
import inspect
import json
import os
import re
import subprocess
import sys

from Grammar import Grammar


def main():
    argparser = argparse.ArgumentParser(
            description=inspect.getdoc(sys.modules[__name__]))
    argparser.add_argument('json_file',
                           nargs='?',
                           default='grammar/src/grammar.json',
                           help='file holding the JSON form of the grammar')
    argparser.add_argument('-v', '--verbose',
                           help='increase output verbosity',
                           action="store_true")
    args = argparser.parse_args()
    with open(args.json_file) as infile:
        json_text = "".join(infile.readlines())

    g = Grammar.Load(json_text, 'translation_unit')
    if args.verbose:
        g.dump()
    else:
        print(g.pretty_str())
    sys.exit(0)


if __name__ == '__main__':
    main()
