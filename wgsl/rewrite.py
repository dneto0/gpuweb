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


# TODO:
#  Read grammar from ebnf
#  Write ebnf

import argparse
import re
import sys

EBNF_METACHARS="?+*|()"

class Options:
    def __init__(self,emit_text=False,emit_bs=False,emit_ebnf=False,sot_ebnf=True):
        # True if the source of truth about the grammar rules is the EBNF.
        # If false, the source of truth is the bikeshed form of the grammar.
        self.sot_ebnf = sot_ebnf
        # Emit non-grammar text?
        self.emit_text = emit_text
        # Emit bikeshed text?
        self.emit_bs = emit_bs
        # Emit EBNF grammar text?
        self.emit_ebnf = emit_ebnf

def ebnf_comment(s):
    return "<!--ebnf {} ebnf-->\n".format(s)


TAG_TEXT='text'
TAG_EBNF='ebnf'
TAG_BS='bs'
class TaggedLine:
    def __init__(self,tag,line):
        self.tag = tag
        self.line = line

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

class StateEnum:
    def __init__(self):
        self.INITIAL = 0
        self.SAW_DIV = 1
        self.SAW_DFN = 1
State = StateEnum()

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
        return "{}\n{}".format(self.name,"".join([x.ebnf_str() for x in self.alternatives]))

class Alternative(GrammarElement):
    def __init__(self,elements):
        self.elements = elements

    def bs_str(self):
        return "\n | {}\n".format(" ".join([x.bs_str() for x in self.elements]))

    def ebnf_str(self):
        return "| {}\n".format(" ".join([x.ebnf_str() for x in self.elements]))

class Symbol(GrammarElement):
    # The name of a syntax rule, e.g. translation_unit
    def __init__(self,name):
        self.name = name

    def bs_str(self):
        return "[=syntax/{}=]".format(self.name)

    def ebnf_str(self):
        return self.name

class KeywordUse(GrammarElement):
    # A use of a keyword, e.g. 'true'
    def __init__(self,name):
        self.name = name

    def bs_str(self):
        return "<a for=syntax_kw lt={}>`'{}'`</a>".format(self.name,self.name)

    def ebnf_str(self):
        return self.name

class KeywordDef(GrammarElement):
    # A keyword, e.g. 'while'
    def __init__(self,name):
        self.name = name

    def bs_str(self):
        return "* <dfn for=syntax_kw noexport>`{}`</dfn>".format(self.name,self.name)

    def ebnf_str(self):
        return ebnf_comment("kw:"+self.name)

class SynToken(GrammarElement):
    # A syntactic token, e.g.   '>>=' with link text shift_right_equal
    def __init__(self,linktext,literal):
        self.linktext = linktext
        self.literal = literal

    def bs_str(self):
        return "<a for=syntax_sym lt={}>`'{}'`</a>".format(self.linktext,self.literal)

    def ebnf_str(self):
        return "'{}'".format(self.literal)

class SynTokenDef(GrammarElement):
    def __init__(self,linktext,literal,codepoints):
        self.linktext = linktext
        self.literal = literal
        self.codepoints = codepoints

    def bs_str(self):
        return "* <dfn for=syntax_sym lt='{}' noexport>`'{}' {}`</dfn>".format(self.linktext,self.literal,self.codepoints)

    def ebnf_str(self):
        return ebnf_comment("'{}'".format(self.literal))

class PatternToken(GrammarElement):
    # A pattern token, e.g.   '/[rgba]/'
    def __init__(self,pattern):
        self.pattern = pattern

    def bs_str(self):
        return self.pattern

    def ebnf_str(self):
        return "'{}'".format(self.pattern)

class Meta(GrammarElement):
    # A grammar metacharcter, e.g. ( ) + ? * |
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
    meta = re.match('^([\\'+'\\'.join(EBNF_METACHARS)+'])\s*(.*)',line)
    if meta:
        return (True,Meta(meta.group(1)),meta.group(2))

    # Match a regular expression for a pattern token
    pattern = re.match("^`(/\S+/[uy]*)`\s*(.*)",line)
    if pattern:
        return (True,PatternToken(pattern.group(1)),pattern.group(2))

    # Match a literal string 
    pattern = re.match("^`'(\S+)'`\s*(.*)",line)
    if pattern:
        return (True,PatternToken(pattern.group(1)),pattern.group(2))

    # Match [=syntax/vec_prefix=]
    ref = re.match("^\[=syntax/(\w+)=\]\s*(.*)",line)
    if ref:
        return (True,Symbol(ref.group(1)),ref.group(2))

    # Match <a for=syntax_kw lt=ptr>`'ptr'`</a>
    kw = re.match("^<a for=syntax_kw\s+lt=\w+>`'([^']+)'`</a>\s*(.*)",line)
    if kw:
        return (True,KeywordUse(kw.group(1)),kw.group(2))

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

class Processor:
    def __init__(self,options):
        self.options = options
        # List of tagged output lines
        self.result = []

        # Compiled regular expressions
        self.start_div_re = re.compile("^\s*<div class='syntax'")
        self.end_div_re = re.compile("^\s*</div>")
        self.start_dfn_re = re.compile("^\s*<dfn for=syntax\W*>(\w+)<")
        self.kw_dfn_re = re.compile("^\*\s*<dfn for=syntax_kw noexport>`(\w+)`</dfn>")
        self.syn_dfn_re = re.compile("^\*\s*<dfn for=syntax_sym lt='(\w+)'\s+noexport>`'([^']+)'`\s+(.*)</dfn>")

        self.reset()

    def reset(self):
        self.result = []

    def emit(self,element):
        if isinstance(element,GrammarElement):
            # When both are present, EBNF should precede the BS
            self.result.append(TaggedLine(TAG_EBNF,element.ebnf_str()))
            self.result.append(TaggedLine(TAG_BS,element.bs_str()))
        elif isinstance(element,TaggedLine):
            self.result.append(element)
        else:
            self.result.append(TaggedLine(TAG_TEXT,element))

    def process(self,lines):
        self.reset()

        current_def = None
        current_def_text = []
        current_alternatives = []
        def generate():
            if len(current_alternatives) < 1:
                raise RuntimeError("expected at least one alternative for {}".format(current_def))
            return Rule(current_def, current_alternatives)


        state = State.INITIAL
        line_num = 0
        for line in lines:
            line_num += 1
            #result.append("state {} {}".format(state,line.rstrip())+"\n")

            # Blank lines are not significant
            if len(line.rstrip()) == 0:
                if len(current_def_text) > 0:
                    current_def_text.append(line)
                else:
                    self.emit(line)
                continue

            kw_dfn = self.kw_dfn_re.match(line)
            if kw_dfn:
                self.emit(KeywordDef(kw_dfn.group(1)))
                continue
            syn_dfn = self.syn_dfn_re.match(line)
            if syn_dfn:
                self.emit(SynTokenDef(syn_dfn.group(1),syn_dfn.group(2),syn_dfn.group(3)))
                continue

            if self.end_div_re.match(line):
                # Flush the current definition, then clear it
                if current_def:
                    self.emit(generate())
                    for l in current_def_text:
                        self.emit(TaggedLine(TAG_BS,l))
                    self.emit(TaggedLine(TAG_BS,line))
                    current_def = None
                    current_def_text = []
                else:
                    # We went from INITIAL -> SAW_DIV and back directly to INITIAL
                    # Flush the false alarm "<div for=syntax..." line
                    for l in current_def_text:
                        self.emit(l)
                    current_def_text = []
                    # Write the current line
                    self.emit(line)
                state = State.INITIAL
                continue

            if state == State.INITIAL:
                if self.start_div_re.match(line):
                    state = State.SAW_DIV
                    current_def_text = [line]
                    continue
            if state == State.SAW_DIV:
                start_dfn = self.start_dfn_re.match(line)
                if start_dfn:
                    current_def = start_dfn.group(1)
                    current_def_text.append(line)
                    current_alternatives = []
                    state = State.SAW_DFN
                    continue
            if state == State.SAW_DFN:
                current_def_text.append(line)
                (ok,alt) = match_alternative(line)
                if ok:
                    current_alternatives.append(alt)
                else:
                    raise RuntimeError("{}: unrecognized alternative: {}".format(line_num,alt))

        return self.result

    def filter(self):
        """Returns the processed output, filtered by options"""
        result = []
        for tl in self.result:
            if self.options.emit_text and tl.tag == TAG_TEXT:
                result.append(tl.line)
            if self.options.emit_ebnf and tl.tag == TAG_EBNF:
                result.append(tl.line)
            if self.options.emit_bs and tl.tag == TAG_BS:
                result.append(tl.line)
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
    argparser.add_argument('-a',
                           action='store_true',
                           help="Write all kinds of outputs")
    argparser.add_argument('-b',
                           action='store_true',
                           help="Write Bikeshed grammar")
    argparser.add_argument('-e',
                           action='store_true',
                           help="Write EBNF")
    argparser.add_argument('-t',
                           action='store_true',
                           help="Write non-grammar text")
    args = argparser.parse_args()
    if args.help:
        print(argparser.format_help())
        return 0

    options = Options()
    if args.a:
        options.emit_text = True
        options.emit_ebnf = True
        options.emit_bs = True
    if args.b:
        options.emit_bs = True
    if args.e:
        options.emit_ebnf = True
    if args.t:
        options.emit_text = True

    with open(args.file,'r') as r:
        lines = r.readlines()

    processor = Processor(options)

    processor.process(lines)
    outlines = processor.filter()
    if args.i:
        with open(args.file,'w') as w:
            w.writelines(outlines)
    else:
        sys.stdout.writelines(outlines)

    return 0

if __name__ == '__main__':
    exit(main(sys.argv[1:]))
