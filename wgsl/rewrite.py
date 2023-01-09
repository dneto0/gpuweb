#!/usr/bin/env python3
#
# Copyright 2023 Google LLC
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


import argparse
import re
import sys

# Each line is in its own state.
# INITIAL: outside of any grammar rule
# SAW_DIV: just saw the introducer 'div' element
#       <div class='syntax' noexport='true'>
#   Expecting "dfn for=syntax" -> SAW_DFN
# SAW_DFN: just saw the introducer 'dfn' element
#         <dfn for=syntax>translation_unit</dfn> :
#   Expecting:
#       blank,
#       ALTERNATIVE:
#       END_DIV -> INITIAL
# Where ALTERNATIVE has pattern:
#   | [=syntax/global_directive=] * ? 

INITIAL=0
SAW_DIV=1
SAW_DFN=2

class GrammarElement:
    def __str__(self):
        return self.ebnf_str()

class Rule(GrammarElement):
    def __init__(self,name,alternatives):
        self.name = name
        self.alternatives = alternatives

    def bs_str(self):
        return "{}\n{}".format(self.name,"\n".join([x.bs_str() for x in self.alternatives]))

    def ebnf_str(self):
        return "{}\n{}".format(self.name,"\n".join([x.ebnf_str() for x in self.alternatives]))

class Alternative(GrammarElement):
    def __init__(self,elements):
        self.elements = elements

    def bs_str(self):
        return " | {}".format(" ".join([x.bs_str() for x in self.elements]))

    def ebnf_str(self):
        return "| {}".format(" ".join([x.ebnf_str() for x in self.elements]))

class Symbol(GrammarElement):
    # The name of a syntax rule, e.g. translation_unit
    def __init__(self,name):
        self.name = name

    def bs_str(self):
        return "[=syntax/{}=]".format(self.name)

    def ebnf_str(self):
        return self.name

class Keyword(GrammarElement):
    # A keyword, e.g. 'while'
    def __init__(self,name):
        self.name = name

    def bs_str(self):
        return "<a for=syntax_kw lt={}>`'{}'`</a>".format(self.name,self.name)

    def ebnf_str(self):
        return self.name

class SynToken(GrammarElement):
    # A syntactic token, e.g.   '>>=' with link text shift_right_equal
    def __init__(self,linktext,literal):
        self.linktext = linktext
        self.literal = literal

    def bs_str(self):
        return "<a for=syntax_sym lt={}>`'{}'`</a>".format(self.linktext,self.literal)

    def ebnf_str(self):
        return self.literal

class PatternToken(GrammarElement):
    # A pattern token, e.g.   '/[rgba]/'
    def __init__(self,pattern):
        self.pattern = pattern

    def bs_str(self):
        return self.pattern

    def ebnf_str(self):
        return self.pattern

class Meta(GrammarElement):
    # A grammar metacharcter, e.g. ( ) + ? *
    def __init__(self,name):
        self.name = name

    def bs_str(self):
        return self.name

    def ebnf_str(self):
        return self.name


def consume_part(line):
    """Parses a line of text, attempting to match an object
    at the beginning.

    Returns at triple: (succes:bool, object, rest-of-line)
    """

    # Match ebnf meta characters ? + * ( ) |
    meta = re.match("^([\?\*\+\(\)|])\s*(.*)",line)
    if meta:
        return (True,Meta(meta.group(1)),meta.group(2))

    # Match a regular expression for a pattern token
    pattern = re.match("^(`/\S+/[uy]*`)\s*(.*)",line)
    if pattern:
        return (True,PatternToken(pattern.group(1)),pattern.group(2))

    # Match a literal string 
    pattern = re.match("^(`'\S+'`)\s*(.*)",line)
    if pattern:
        return (True,PatternToken(pattern.group(1)),pattern.group(2))

    # Match [=syntax/vec_prefix=]
    ref = re.match("^\[=syntax/(\w+)=\]\s*(.*)",line)
    if ref:
        return (True,Symbol(ref.group(1)),ref.group(2))

    # Match <a for=syntax_kw lt=ptr>`'ptr'`</a>
    kw = re.match("^<a for=syntax_kw\s+lt=\w+>`'([^']+)'`</a>\s*(.*)",line)
    if kw:
        return (True,Keyword(kw.group(1)),kw.group(2))

    # Match <a for=syntax_sym lt=semicolon>`';'`</a>
    sym = re.match("^<a\s+for=syntax_sym\s+lt=(\w+)>`'([^']+)'`</a>\s*(.*)",line)
    if sym:
        return (True,SynToken(sym.group(1),sym.group(2)),sym.group(3))

    return (False,None,line)

def consume_bar(line):
    """Parses a line of text, attempting to match an object
    at the beginning.

    Returns at pair: (succes:bool, rest-of-line)
    """

    m = re.match("^\s*\|\s+(.*)",line)
    if m:
        return (True,m.group(1))
    return (False,None)

def match_alternative(line):
    """Parses a text line, attempting to produce a rule alternative.
    Returns: (True,Alternative)
        or   (False, rest-of-line)
    """

    rest = line.rstrip()
    result = None
    (ok,rest) = consume_bar(rest)
    if ok:
        parts = []
        while (ok and len(rest)>0):
            (ok,part,rest) = consume_part(rest)
            if ok:
                parts.append(part)
            else:
                return (False, rest)
        if ok:
            result = Alternative(parts)

    return ok, result

def process_file_to_ebnf(lines):
    result = []
    start_div_re = re.compile("^\s*<div class='syntax'")
    end_div_re = re.compile("^\s*</div>")
    start_dfn_re = re.compile("^\s*<dfn for=syntax\W*>(\w+)<")

    current_def = None
    current_alternatives = []
    def emit():
        if len(current_alternatives) < 1:
            raise RuntimeError("expected at least one alternative for {}".format(current_def))
        rule = Rule(current_def, current_alternatives)
        result.append(str(rule)+"\n")

    state = INITIAL
    line_num = 0
    for line in lines:
        line_num += 1
        #result.append("state {} {}".format(state,line.rstrip())+"\n")

        # Blank lines are not significant
        if len(line.rstrip()) == 0:
            continue
        if end_div_re.match(line):
            state = INITIAL
            # Flush the current definition, then clear it
            if current_def:
                emit()
                current_def = None
            continue
        if state == INITIAL:
            if start_div_re.match(line):
                state = SAW_DIV
                continue
        if state == SAW_DIV:
            start_dfn = start_dfn_re.match(line)
            if start_dfn:
                current_def = start_dfn.group(1)
                current_alternatives = []
                state = SAW_DFN
                continue
        if state == SAW_DFN:
            (ok,alt) = match_alternative(line)
            if ok:
                current_alternatives.append(alt)
            else:
                raise RuntimeError("{}: unrecognized alternative: {}".format(line_num,alt))

    return result
        



def main(argv):
    argparser = argparse.ArgumentParser(
            prog = 'rewrite.py',
            description = 'Rewrite grammar rules in WGSL spec source',
            add_help = False)
    argparser.add_argument('--help', '-h',
                           action='store_true',
                           help="show this help and exit")
    argparser.add_argument('file',
                           nargs='?',
                           default='index.bs',
                           help="Bikeshed source to be processed")
    argparser.add_argument('-i',
                           action='store_true',
                           help="Overwrite the original file instead of outputting to stdout")
    args = argparser.parse_args()
    if args.help:
        print(argparser.format_help())
        return 0

    with open(args.file,'r') as r:
        lines = r.readlines()
    outlines = process_file_to_ebnf(lines)
    if args.i:
        with open(args.file,'w') as w:
            w.writelines(outlines)
    else:
        sys.stdout.writelines(outlines)

    return 0

if __name__ == '__main__':
    exit(main(sys.argv[1:]))
