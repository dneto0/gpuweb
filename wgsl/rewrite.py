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
#  When ebnd if source of truth:
#       Don't drop empty lines
#       Don't drop </div>

import argparse
import re
import sys

EBNF_METACHARS="?+*|()"

class Options:
    def __init__(self,emit_text=False,emit_bs=False,emit_ebnf=False,sot_ebnf=True,sot_bs=False):
        # True if the source of truth about the grammar rules is the EBNF.
        # If false, the source of truth is the bikeshed form of the grammar.
        self.sot_ebnf = sot_ebnf
        self.sot_bs = sot_bs
        if sot_ebnf and sot_bs:
            raise RuntimeError("Can't have both EBNF and BS as sources of truth")
        if sot_ebnf == sot_bs:
            raise RuntimeError("At least one EBNF and BS must be a sources of truth")
        # Emit non-grammar text?
        self.emit_text = emit_text
        # Emit bikeshed text?
        self.emit_bs = emit_bs
        # Emit EBNF grammar text?
        self.emit_ebnf = emit_ebnf

def ebnf_comment(tag,s):
    pre = '\n' if '\n' in s else ' '
    post = '' if '\n' in s else ' '
    return "<!--:ebnf:{}{}{}{}:ebnf:-->\n".format(tag,pre,s,post)


TAG_TEXT='text'
TAG_EBNF='ebnf'
TAG_EBNF_NEW='ebnf_new'
TAG_BS='bs' # The original bikeshed grammar text
TAG_BS_NEW='bs_new' # The new bikeshed grammar text
class TaggedLine:
    def __init__(self,tag,line):
        self.tag = tag
        self.line = line
    def __str__(self):
        if isinstance(self.line,GrammarElement):
            if (self.tag == TAG_BS) or (self.tag == TAG_BS_NEW):
                text = self.line.bs_str()
            elif (self.tag == TAG_EBNF) or (self.tag == TAG_EBNF_NEW):
                text = self.line.ebnf_str()
        else:
            text = self.line
        return text

class GrammarElement:
    def __str__(self):
        return self.ebnf_str()

class Rule(GrammarElement):
    def __init__(self,name,alternatives):
        self.name = name
        self.alternatives = alternatives

    def bs_str(self):
        header = "<div class='syntax' noexport='true'>\n  <dfn for=syntax>{}</dfn> :".format(self.name)
        body = "".join([x.bs_str() for x in self.alternatives])
        return "{}\n{}</div>\n".format(header,body)

    def ebnf_str(self):
        return ebnf_comment("rule","{}\n{}".format(self.name,"".join([x.ebnf_str() for x in self.alternatives])))

class Alternative(GrammarElement):
    def __init__(self,elements):
        self.elements = elements

    def bs_str(self):
        return "\n    | {}\n".format(" ".join([x.bs_str() for x in self.elements]))

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
        return "kw:"+self.name

class KeywordDef(GrammarElement):
    # A keyword, e.g. 'while'
    def __init__(self,name):
        self.name = name

    def bs_str(self):
        return "* <dfn for=syntax_kw noexport>`{}`</dfn>\n".format(self.name,self.name)

    def ebnf_str(self):
        return ebnf_comment("kw",self.name)

# Maps a syntax literal string to its link text name.
# When all we have is the EBNF text, the link text for a syntactic token
# is only given in its full definition, which occurs late in the file.
# Use this dictionary to store the link text, to be looked up later
# when generating new bikeshed grammar text.
syn_token_name = dict()

class SynToken(GrammarElement):
    # A syntactic token, e.g.   '>>=' with link text shift_right_equal
    def __init__(self,linktext,literal):
        self.linktext = linktext
        self.literal = literal

    def bs_str(self):
        # Hack: update the link text
        global syn_token_name
        if self.literal in syn_token_name:
            self.linktext = syn_token_name[self.literal]
        return "<a for=syntax_sym lt={}>`'{}'`</a>".format(self.linktext,self.literal)

    def ebnf_str(self):
        return "'{}'".format(self.literal)

class SynTokenDef(GrammarElement):
    def __init__(self,linktext,literal,codepoints):
        self.linktext = linktext
        self.literal = literal
        self.codepoints = codepoints
        global syn_token_name
        syn_token_name[literal] = linktext

    def bs_str(self):
        return "* <dfn for=syntax_sym lt='{}' noexport>`'{}'` {}</dfn>\n".format(self.linktext,self.literal,self.codepoints)

    def ebnf_str(self):
        return ebnf_comment("syn","{} {} {}".format(self.linktext,self.literal,self.codepoints))

class PatternToken(GrammarElement):
    # A pattern token, e.g.   '/[rgba]/'
    def __init__(self,pattern):
        self.pattern = pattern

    def bs_str(self):
        return "`{}`".format(self.pattern)

    def ebnf_str(self):
        return "'{}'".format(self.pattern)

class FixedToken(GrammarElement):
    # A fixed text token, e.g.   'invariant'
    def __init__(self,pattern):
        self.pattern = pattern

    def bs_str(self):
        return "`'{}'`".format(self.pattern)

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


def consume_part(options,line):
    """Parses a line of text, attempting to match an object
    at the beginning.

    Returns at triple: (succes:bool, object, rest-of-line)
    """

    # Match ebnf meta characters ? + * ( ) |
    meta = re.match('^([\\'+'\\'.join(EBNF_METACHARS)+'])\s*(.*)',line)
    if meta:
        return (True,Meta(meta.group(1)),meta.group(2))

    # Match a regular expression for a pattern token
    for quote in ('`', "'"):
        the_re = "^{}(/\S+/[uy]*){}\s*(.*)".format(quote,quote)
        pattern = re.match(the_re,line)
        if pattern:
            return (True,PatternToken(pattern.group(1)),pattern.group(2))
    if True:
        # Legacy swizzlename has `'/[rgba]/'`
        the_re = "^`'(/\S+/[uy]*)'`\s*(.*)"
        pattern = re.match(the_re,line)
        if pattern:
            return (True,PatternToken(pattern.group(1)),pattern.group(2))

    # Match a literal string 
    for quote in ('`', ""):
        the_re = "^{}'([a-zA-Z0-9_]+)'{}\s*(.*)".format(quote,quote)
        pattern = re.match(the_re,line)
        if pattern:
            return (True,FixedToken(pattern.group(1)),pattern.group(2))

    # For BS, match <a for=syntax_kw lt=ptr>`'ptr'`</a>
    kw = re.match("^<a for=syntax_kw\s+lt=\w+>`'([^']+)'`</a>\s*(.*)",line)
    if kw:
        return (True,KeywordUse(kw.group(1)),kw.group(2))
    # For EBNF, match kw:while
    kw = re.match("^kw:(\w+)\s*(.*)",line)
    if kw:
        return (True,KeywordUse(kw.group(1)),kw.group(2))

    # For BS, match things like [=syntax/vec_prefix=]
    ref = re.match("^\[=syntax/(\w+)=\]\s*(.*)",line)
    if ref:
        return (True,Symbol(ref.group(1)),ref.group(2))

    # For EBNF, match things like while
    ref = re.match("^(\w+)\s*(.*)",line)
    if ref:
        return (True,Symbol(ref.group(1)),ref.group(2))

    # For BS, match <a for=syntax_sym lt=semicolon>`';'`</a>
    sym = re.match("^<a\s+for=syntax_sym\s+lt=(\w+)>`'([^']+)'`</a>\s*(.*)",line)
    if sym:
        return (True,SynToken(sym.group(1),sym.group(2)),sym.group(3))
    # For EBNF, match things like ';'
    sym = re.match("^'(\S+)'\s*(.*)",line)
    if sym:
        madeup='syn:'+sym.group(1)
        return (True,SynToken(madeup,sym.group(1)),sym.group(2))

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

def match_alternative(options,line):
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
            (ok,part,rest) = consume_part(options,rest)
            if ok:
                parts.append(part)
            else:
                return (False, rest)
        if ok:
            result = Alternative(parts)

    return ok, result

class CurrentDef:
    def __init__(self):
        self.name = '' # string
        self.text = [] # list of string, containing the source-of-truth text
        self.alternatives = [] # list of Alternative objects representing the body
        # Invariant: self.text is non-empty whenever self.name is non-empty

    def generate(self):
        if len(self.alternatives) < 1:
            raise RuntimeError("expected at least one alternative for {}".format(self.name))
        return Rule(self.name, self.alternatives)

# Each line is in its own state.
# INITIAL: outside of any grammar rule
# BS_EXPECT_RULE_HEADER: just saw the introducer 'div' element
#       <div class='syntax' noexport='true'>
#   Expecting "<dfn for=syntax" -> BS_EXPECT_ALTERNATIVE
#   Expecting "<!--:ebnf:rule" -> EBNF_EXPECT_ALTERNATIVE
# BS_EXPECT_ALTERNATIVE: just saw the 'dfn' rule header
#         <dfn for=syntax>translation_unit</dfn> :
#   Expecting:
#       blank line
#       An alternative, e.g. | blah blah blah
#       "</div>" -> INITIAL
# EBNF_EXPECT_RULE_HEADER: just saw the introducer
#       <!--:ebnf:rule
#   Expecting "\S+" -> EBNF_EXPECT_ALTERNATIVE
#   Eample:  while_statement
# EBNF_EXPECT_ALTERNATIVE: just saw rule name \S+
#   Expecting:
#       An alternative, e.g. | blah blah blah
#       ":ebnf:-->" -> INITIAL

class StateEnum:
    def __init__(self):
        self.INITIAL = 'init'
        self.BS_EXPECT_RULE_HEADER = 'bs_erh'
        self.BS_EXPECT_ALTERNATIVE = 'bs_ea'
        self.EBNF_EXPECT_RULE_HEADER = 'ebnf_erh'
        self.EBNF_EXPECT_ALTERNATIVE = 'ebnf_ea'
State = StateEnum()


class Processor:
    def __init__(self,options):
        self.options = options
        # List of tagged output lines
        self.result = []

        # Compiled regular expressions
        self.bs_start_rule_re = re.compile("^\s*<div class='syntax'")
        self.bs_end_rule_re = re.compile("^\s*</div>")
        self.bs_start_dfn_re = re.compile("^\s*<dfn for=syntax\W*>(\w+)<")
        self.bs_kw_dfn_re = re.compile("^\*\s*<dfn for=syntax_kw noexport>`(\w+)`</dfn>")
        self.bs_syn_dfn_re = re.compile("^\*\s*<dfn for=syntax_sym lt='(\w+)'\s+noexport>`'([^']+)'`\s+(.*)</dfn>")

        self.ebnf_start_rule_re = re.compile("^\s*<!--:ebnf:rule\s*$")
        self.ebnf_end_rule_re = re.compile("^:ebnf:-->")
        self.ebnf_start_dfn_re = re.compile("^(\S+)")
        self.ebnf_kw_dfn_re = re.compile("^<!--:ebnf:kw (\w+) :ebnf:-->")
        self.ebnf_syn_dfn_re = re.compile("^<!--:ebnf:syn (\w+) (\S+) (.*) :ebnf:-->")

        self.reset()

    def reset(self):
        self.result = []

    def emit(self,element):
        if isinstance(element,GrammarElement):
            # When both are present, EBNF should precede the BS
            self.result.append(TaggedLine(TAG_EBNF_NEW,element))
            self.result.append(TaggedLine(TAG_BS_NEW,element))
        elif isinstance(element,TaggedLine):
            self.result.append(element)
        else:
            self.result.append(TaggedLine(TAG_TEXT,element))

    def parse_kw_dfn(self,line):
        bs_kw_dfn = self.bs_kw_dfn_re.match(line)
        if bs_kw_dfn:
            if self.options.sot_bs:
                self.emit(KeywordDef(bs_kw_dfn.group(1)))
            return True
        ebnf_kw_dfn = self.ebnf_kw_dfn_re.match(line)
        if ebnf_kw_dfn:
            if self.options.sot_ebnf:
                self.emit(KeywordDef(ebnf_kw_dfn.group(1)))
            return True
        return False

    def parse_syn_dfn(self,line):
        bs_syn_dfn = self.bs_syn_dfn_re.match(line)
        if bs_syn_dfn:
            if self.options.sot_bs:
                self.emit(SynTokenDef(bs_syn_dfn.group(1),bs_syn_dfn.group(2),bs_syn_dfn.group(3)))
            return True
        ebnf_syn_dfn = self.ebnf_syn_dfn_re.match(line)
        if ebnf_syn_dfn:
            if self.options.sot_ebnf:
                self.emit(SynTokenDef(ebnf_syn_dfn.group(1),ebnf_syn_dfn.group(2),ebnf_syn_dfn.group(3)))
            return True
        return False

    def process(self,lines):
        self.reset()

        current_def = CurrentDef()

        state = State.INITIAL
        line_num = 0
        for line in lines:
            line_num += 1

            if self.parse_kw_dfn(line):
                continue
            if self.parse_syn_dfn(line):
                continue

            # Blank lines are not significant
            if len(line.rstrip()) == 0:
                if len(current_def.text) > 0:
                    current_def.text.append(line)
                else:
                    self.emit(line)
                continue

            if self.bs_end_rule_re.match(line):
                # Flush the current definition, then clear it
                if self.options.sot_bs:
                    if current_def.name:
                        self.emit(current_def.generate())
                        for l in current_def.text:
                            self.emit(TaggedLine(TAG_BS,l))
                        self.emit(TaggedLine(TAG_BS,line))
                        current_def = CurrentDef()
                    else:
                        # We went from INITIAL -> BS_EXPECT_RULE_HEADER and back directly to INITIAL
                        # Flush the false alarm "<div for=syntax..." line
                        for l in current_def.text:
                            self.emit(l)
                        current_def = CurrentDef()
                        # Write the current line
                        self.emit(line)
                state = State.INITIAL
                continue
            if self.ebnf_end_rule_re.match(line):
                # Flush the current definition, then clear it
                if self.options.sot_ebnf:
                    if current_def.name:
                        self.emit(current_def.generate())
                        for l in current_def.text:
                            self.emit(TaggedLine(TAG_EBNF,l))
                        self.emit(TaggedLine(TAG_EBNF,line))
                        current_def = CurrentDef()
                    else:
                        # We went from INITIAL -> EBNFEXPECT_RULE_HEADER and back directly to INITIAL
                        # Flush the false alarm
                        for l in current_def.text:
                            self.emit(l)
                        current_def = CurrentDef()
                        # Write the current line
                        self.emit(line)
                state = State.INITIAL
                continue

            if state == State.INITIAL:
                if self.bs_start_rule_re.match(line):
                    state = State.BS_EXPECT_RULE_HEADER
                    current_def.text = [line]
                    continue
                if self.ebnf_start_rule_re.match(line):
                    state = State.EBNF_EXPECT_RULE_HEADER
                    current_def.text = [line]
                    continue
            # Procdss contents of BS rules
            if state == State.BS_EXPECT_RULE_HEADER:
                start_dfn = self.bs_start_dfn_re.match(line)
                if start_dfn:
                    if self.options.sot_bs:
                        current_def.name = start_dfn.group(1)
                        current_def.text.append(line)
                        current_def.alternatives = []
                    state = State.BS_EXPECT_ALTERNATIVE
                    continue
            if state == State.BS_EXPECT_ALTERNATIVE:
                if self.options.sot_bs:
                    current_def.text.append(line)
                (ok,alt) = match_alternative(self.options,line)
                if ok:
                    if self.options.sot_bs:
                        current_def.alternatives.append(alt)
                    continue
                else:
                    raise RuntimeError("{}: unrecognized alternative: {}".format(line_num,alt))
            # Procdss contents of EBNF rules
            if state == State.EBNF_EXPECT_RULE_HEADER:
                start_dfn = self.ebnf_start_dfn_re.match(line)
                if start_dfn:
                    if self.options.sot_ebnf:
                        current_def.name = start_dfn.group(1)
                        current_def.text.append(line)
                        current_def.alternatives = []
                    state = State.EBNF_EXPECT_ALTERNATIVE
                    continue
            if state == State.EBNF_EXPECT_ALTERNATIVE:
                if self.options.sot_ebnf:
                    current_def.text.append(line)
                (ok,alt) = match_alternative(self.options,line)
                if ok:
                    if self.options.sot_ebnf:
                        current_def.alternatives.append(alt)
                    continue
                else:
                    raise RuntimeError("{}: unrecognized alternative: {}".format(line_num,alt))
            self.emit(line)

        return self.result

    def filter(self):
        """Returns the processed output, filtered by options"""
        result = []
        for tl in self.result:
            if self.options.emit_text and tl.tag == TAG_TEXT:
                result.append(str(tl))
            if self.options.emit_ebnf and tl.tag == TAG_EBNF_NEW:
                result.append(str(tl))
            if self.options.emit_bs and tl.tag == TAG_BS_NEW:
                result.append(str(tl))
        return result

    def __str__(self):
        parts = ["".join([str(x) for x in self.result])]
        parts.append("syn_token_name {}".format(str(syn_token_name)))
        return "\n".join(parts)


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
    argparser.add_argument('--dump', '-d',
                           action='store_true',
                           help="Dump internal state.")
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
    direction_arg = argparser.add_mutually_exclusive_group()
    direction_arg.add_argument('-f',
                               action='store_true',
                               help="Forward. Source of truth is EBNF. This is the default")
    direction_arg.add_argument('-r',
                               action='store_true',
                               help="Reverse. Source of truth is Bikeshed")
    args = argparser.parse_args()
    if args.help:
        print(argparser.format_help())
        return 0

    # Default to forward
    if args.f == False and args.r == False:
        args.f = True

    options = Options(sot_ebnf = args.f, sot_bs = args.r)
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

    if args.dump:
        print(">>>DUMP")
        print(processor)
        print("<<<DUMP")

    outlines = processor.filter()
    if args.i:
        with open(args.file,'w') as w:
            w.writelines(outlines)
    else:
        sys.stdout.writelines(outlines)

    return 0

if __name__ == '__main__':
    exit(main(sys.argv[1:]))
