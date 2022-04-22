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
Unit tests for Grammar.py
"""

import unittest
import Grammar

# Like Aho, Sethi, Ullman Example 4.17, but with E changed
DRAGON_BOOK_EXAMPLE_4_17 = """
{
  "name": "dragon_book_ex_4_17",
  "word": "id",
  "rules": {
    "E": {
      "type": "SEQ",
      "members": [
        {
          "type": "SYMBOL",
          "name": "T"
        },
        {
          "type": "SYMBOL",
          "name": "Eprime"
        }
      ]
    },
    "Eprime": {
      "type": "CHOICE",
      "members": [
        {
          "type": "SEQ",
          "members": [
            {
              "type": "SYMBOL",
              "name": "plus"
            },
            {
              "type": "SYMBOL",
              "name": "T"
            },
            {
              "type": "SYMBOL",
              "name": "Eprime"
            }
          ]
        },
        {
          "type": "BLANK"
        }
      ]
    },
    "T": {
      "type": "SEQ",
      "members": [
        {
          "type": "SYMBOL",
          "name": "F"
        },
        {
          "type": "SYMBOL",
          "name": "Tprime"
        }
      ]
    },
    "Tprime": {
      "type": "CHOICE",
      "members": [
        {
          "type": "SEQ",
          "members": [
            {
              "type": "SYMBOL",
              "name": "times"
            },
            {
              "type": "SYMBOL",
              "name": "F"
            },
            {
              "type": "SYMBOL",
              "name": "Tprime"
            }
          ]
        },
        {
          "type": "BLANK"
        }
      ]
    },
    "F": {
      "type": "CHOICE",
      "members": [
        {
          "type": "SEQ",
          "members": [
            {
              "type": "SYMBOL",
              "name": "paren_left"
            },
            {
              "type": "SYMBOL",
              "name": "E"
            },
            {
              "type": "SYMBOL",
              "name": "paren_right"
            }
          ]
        },
        {
          "type": "SYMBOL",
          "name": "id"
        }
      ]
    },
    "id": {
      "type": "TOKEN",
      "content": {
        "type": "STRING",
        "value": "id"
      }
    },
    "plus": {
      "type": "TOKEN",
      "content": {
        "type": "STRING",
        "value": "+"
      }
    },
    "times": {
      "type": "TOKEN",
      "content": {
        "type": "STRING",
        "value": "*"
      }
    },
    "paren_left": {
      "type": "TOKEN",
      "content": {
        "type": "STRING",
        "value": "("
      }
    },
    "paren_right": {
      "type": "TOKEN",
      "content": {
        "type": "STRING",
        "value": ")"
      }
    }
  },
  "extras": [],
  "conflicts": [],
  "precedences": [],
  "externals": [],
  "inline": [],
  "supertypes": []
}
"""


SIMPLE_WGSL = """
{
  "name": "firsts",
  "word": "ident",
  "rules": {
    "translation_unit": {
      "type": "SEQ",
      "members": [
        {
          "type": "CHOICE",
          "members": [
            {
              "type": "REPEAT1",
              "content": {
                "type": "SYMBOL",
                "name": "global_decl"
              }
            },
            {
              "type": "BLANK"
            }
          ]
        }
      ]
    },
    "type_alias_decl": {
      "type": "SEQ",
      "members": [
        {
          "type": "SYMBOL",
          "name": "type"
        },
        {
          "type": "SYMBOL",
          "name": "ident"
        },
        {
          "type": "SYMBOL",
          "name": "equal"
        },
        {
          "type": "SYMBOL",
          "name": "ident"
        }
      ]
    },
    "global_decl": {
      "type": "CHOICE",
      "members": [
        {
          "type": "SYMBOL",
          "name": "semicolon"
        },
        {
          "type": "SEQ",
          "members": [
            {
              "type": "SYMBOL",
              "name": "type_alias_decl"
            },
            {
              "type": "SYMBOL",
              "name": "semicolon"
            }
          ]
        },
        {
          "type": "SYMBOL",
          "name": "function_decl"
        }
      ]
    },
    "function_decl": {
      "type": "SEQ",
      "members": [
        {
          "type": "CHOICE",
          "members": [
            {
              "type": "REPEAT1",
              "content": {
                "type": "SYMBOL",
                "name": "at"
              }
            },
            {
              "type": "BLANK"
            }
          ]
        },
        {
          "type": "SYMBOL",
          "name": "function_header"
        },
        {
          "type": "SYMBOL",
          "name": "brace_left"
        },
        {
          "type": "SYMBOL",
          "name": "brace_right"
        }
      ]
    },
    "function_header": {
      "type": "SEQ",
      "members": [
        {
          "type": "SYMBOL",
          "name": "fn"
        },
        {
          "type": "SYMBOL",
          "name": "ident"
        },
        {
          "type": "SYMBOL",
          "name": "paren_left"
        },
        {
          "type": "SYMBOL",
          "name": "paren_right"
        }
      ]
    },
    "ident": {
      "type": "TOKEN",
      "content": {
        "type": "PATTERN",
        "value": "[a-z]+"
      }
    },
    "at": {
      "type": "TOKEN",
      "content": {
        "type": "STRING",
        "value": "@"
      }
    },
    "_space": {
      "type": "TOKEN",
      "content": {
        "type": "PATTERN",
        "value": "\\\\s+"
      }
    },
    "fn": {
      "type": "TOKEN",
      "content": {
        "type": "STRING",
        "value": "fn"
      }
    },
    "type": {
      "type": "TOKEN",
      "content": {
        "type": "STRING",
        "value": "type"
      }
    },
    "equal": {
      "type": "TOKEN",
      "content": {
        "type": "STRING",
        "value": "="
      }
    },
    "semicolon": {
      "type": "TOKEN",
      "content": {
        "type": "STRING",
        "value": ";"
      }
    },
    "brace_left": {
      "type": "TOKEN",
      "content": {
        "type": "STRING",
        "value": "{"
      }
    },
    "brace_right": {
      "type": "TOKEN",
      "content": {
        "type": "STRING",
        "value": "}"
      }
    },
    "paren_left": {
      "type": "TOKEN",
      "content": {
        "type": "STRING",
        "value": "("
      }
    },
    "paren_right": {
      "type": "TOKEN",
      "content": {
        "type": "STRING",
        "value": ")"
      }
    }
  },
  "extras": [
    {
      "type": "SYMBOL",
      "name": "_space"
    }
  ],
  "conflicts": [],
  "precedences": [],
  "externals": [
  ],
  "inline": [
  ],
  "supertypes": []
}
"""

EPSILON=u"\u03b5"

def strset(s):
    return " ".join(sorted([str(i) for i in s]))

class DragonBook(unittest.TestCase):
    def setUp(self):
        self.g = Grammar.Grammar.Load(DRAGON_BOOK_EXAMPLE_4_17,'E')

    # Check First sets
    def test_E_first(self):
        r = self.g.find("E")
        self.assertEqual(strset(r.first), "'(' 'id'")

    def test_T_first(self):
        r = self.g.find("T")
        self.assertEqual(strset(r.first), "'(' 'id'")

    def test_F_first(self):
        r = self.g.find("F")
        self.assertEqual(strset(r.first), "'(' 'id'")

    def test_Eprime_first(self):
        r = self.g.find("Eprime")
        self.assertEqual(strset(r.first), "'+' {}".format(EPSILON))

    def test_Tprime_first(self):
        r = self.g.find("Tprime")
        self.assertEqual(strset(r.first), "'*' {}".format(EPSILON))

    # Check Follow sets
    def test_E_follow(self):
        r = self.g.find("E")
        self.assertEqual(strset(r.follow), "')' EndOfText")

    def test_Eprime_follow(self):
        r = self.g.find("Eprime")
        self.assertEqual(strset(r.follow), "')' EndOfText")

    def test_T_follow(self):
        r = self.g.find("T")
        self.assertEqual(strset(r.follow), "')' '+' EndOfText")

    def test_Tprime_follow(self):
        r = self.g.find("Tprime")
        self.assertEqual(strset(r.follow), "')' '+' EndOfText")

    def test_F_follow(self):
        r = self.g.find("F")
        self.assertEqual(strset(r.follow), "')' '*' '+' EndOfText")


class SimpleWgsl_First(unittest.TestCase):

    def setUp(self):
        self.g = Grammar.Grammar.Load(SIMPLE_WGSL,'translation_unit')

    def test_token_string(self):
        r = self.g.find('at')
        self.assertEqual(1,len(r.first))
        self.assertEqual("'@'",strset(r.first))
        self.assertFalse(r.derives_empty())

    def test_token_pattern(self):
        r = self.g.find('ident')
        self.assertEqual("/[a-z]+/",strset(r.first))
        self.assertFalse(r.derives_empty())

    def test_empty(self):
        r = self.g.empty
        self.assertEqual(EPSILON,strset(r.first))
        self.assertTrue(r.derives_empty())

    def test_end_of_text(self):
        r = self.g.end_of_text
        self.assertEqual("EndOfText",strset(r.first))
        self.assertFalse(r.derives_empty())

    def test_function_header(self):
        # A Sequence rule with definite first symbol
        r = self.g.find('function_header')
        self.assertEqual("'fn'",strset(r.first))
        self.assertFalse(r.derives_empty())

    def test_function_decl(self):
        # A sequence with an optional first symbol
        r = self.g.find('function_decl')
        self.assertEqual("'@' 'fn'",strset(r.first))
        self.assertFalse(r.derives_empty())

    def test_translation_unit_0_0(self):
        # Can be empty.
        r = self.g.find('translation_unit/0.0')
        self.assertEqual("';' '@' 'fn' 'type' {}".format(EPSILON),strset(r.first))
        self.assertTrue(r.derives_empty())

    def test_translation_unit(self):
        # Can be empty.
        r = self.g.find('translation_unit')
        self.assertEqual("';' '@' 'fn' 'type' {}".format(EPSILON),strset(r.first))
        self.assertTrue(r.derives_empty())


class SimpleWgsl_Follow(unittest.TestCase):

    def setUp(self):
        self.g = Grammar.Grammar.Load(SIMPLE_WGSL,'translation_unit')

    def test_token_string(self):
        r = self.g.find('at')
        self.assertEqual(set(), r.follow)

    def test_token_pattern(self):
        r = self.g.find('ident')
        self.assertEqual(set(), r.follow)

    def test_empty(self):
        r = self.g.empty
        self.assertEqual(set(), r.follow)

    def test_end_of_text(self):
        r = self.g.end_of_text
        self.assertEqual(set(), r.follow)

    def test_function_decl_0_0(self):
        # Attribute list is followed by 'fn'
        r = self.g.find('function_decl/0.0')
        self.assertEqual("'fn'",strset(r.follow))

    def test_function_decl(self):
        r = self.g.find('function_decl')
        self.assertEqual("",strset(r.follow))

    def test_global_decl(self):
        # A global decl can be followed by another global decl.
        # So the non-Empty symbols from global-decl's First set
        # is what is in its Follow set.
        r = self.g.find('global_decl')
        self.assertEqual("';' '@' 'fn' 'type'",strset(r.follow))

    def test_translation_unit(self):
        # Can be empty.
        r = self.g.find('translation_unit')
        self.assertEqual("EndOfText",strset(r.follow))


class Item_Basics(unittest.TestCase):

    def make_item(self,*args):
        return Grammar.Item(*args)

    def test_Item_OfEmpty_Good(self):
        it = Grammar.Item(Grammar.Empty(),0)
        self.assertEqual(it.items, [])

    def test_Item_OfEmpty_PosTooSmall(self):
        self.assertRaises(RuntimeError, self.make_item, Grammar.Empty(), -1)

    def test_Item_OfEmpty_PosTooBig(self):
        self.assertRaises(RuntimeError, self.make_item, Grammar.Empty(), 1)

    def test_Item_OfFixed_Pos0(self):
        t = Grammar.Fixed('x')
        it = Grammar.Item(t,0)
        self.assertEqual(it.rule, t)
        self.assertEqual(it.position, 0)
        self.assertEqual(it.items, [t])

    def test_Item_OfFixed_Pos1(self):
        t = Grammar.Fixed('x')
        it = Grammar.Item(t,1)
        self.assertEqual(it.rule, t)
        self.assertEqual(it.position, 1)
        self.assertEqual(it.items, [t])

    def test_Item_OfFixed_PosTooSmall(self):
        self.assertRaises(RuntimeError, self.make_item, Grammar.Fixed('x'), -1)

    def test_Item_OfFixed_PosTooBig(self):
        self.assertRaises(RuntimeError, self.make_item, Grammar.Fixed('x'), 2)

    def test_Item_OfPattern_Pos0(self):
        t = Grammar.Pattern('[a-z]+')
        it = Grammar.Item(t,0)
        self.assertEqual(it.rule, t)
        self.assertEqual(it.position, 0)
        self.assertEqual(it.items, [t])

    def test_Item_OfPattern_Pos1(self):
        t = Grammar.Pattern('[a-z]+')
        it = Grammar.Item(t,1)
        self.assertEqual(it.rule, t)
        self.assertEqual(it.position, 1)
        self.assertEqual(it.items, [t])

    def test_Item_OfPattern_PosTooSmall(self):
        self.assertRaises(RuntimeError, self.make_item, Grammar.Pattern('[a-z]+'), -1)

    def test_Item_OfPattern_PosTooBig(self):
        self.assertRaises(RuntimeError, self.make_item, Grammar.Pattern('[a-z]+'), 2)

    def test_Item_OfSymbol_Pos0(self):
        t = Grammar.Symbol('x')
        it = Grammar.Item(t,0)
        self.assertEqual(it.rule, t)
        self.assertEqual(it.position, 0)
        self.assertEqual(it.items, [t])

    def test_Item_OfSymbol_Pos1(self):
        t = Grammar.Symbol('x')
        it = Grammar.Item(t,1)
        self.assertEqual(it.rule, t)
        self.assertEqual(it.position, 1)
        self.assertEqual(it.items, [t])

    def test_Item_OfSymbol_PosTooSmall(self):
        self.assertRaises(RuntimeError, self.make_item, Grammar.Symbol('x'), -1)

    def test_Item_OfSymbol_PosTooBig(self):
        self.assertRaises(RuntimeError, self.make_item, Grammar.Symbol('x'), 2)

    def example_seq(self):
        return Grammar.Seq([Grammar.Fixed('x'), Grammar.Symbol('blah')])

    def test_Item_OfSeq_Pos0(self):
        t = self.example_seq()
        it = Grammar.Item(t,0)
        self.assertEqual(it.rule, t)
        self.assertEqual(it.position, 0)
        self.assertEqual(it.items, [i for i in t])

    def test_Item_OfSeq_Pos1(self):
        t = self.example_seq()
        it = Grammar.Item(t,1)
        self.assertEqual(it.rule, t)
        self.assertEqual(it.position, 1)
        self.assertEqual(it.items, [i for i in t])

    def test_Item_OfSeq_Pos2(self):
        t = self.example_seq()
        it = Grammar.Item(t,2)
        self.assertEqual(it.rule, t)
        self.assertEqual(it.position, 2)
        self.assertEqual(it.items, [i for i in t])

    def test_Item_OfSeq_PosTooSmall(self):
        self.assertRaises(RuntimeError, self.make_item, self.example_seq(), -1)

    def test_Item_OfSeq_PosTooBig(self):
        self.assertRaises(RuntimeError, self.make_item, self.example_seq(), 3)

    def test_Item_OfChoice(self):
        self.assertRaises(RuntimeError, self.make_item, Grammar.Choice([]), 0)

    def test_Item_OfRepeat1(self):
        self.assertRaises(RuntimeError, self.make_item, Grammar.Repeat1([]), 0)


class Rule_Equality(unittest.TestCase):
    def test_Empty(self):
        a = Grammar.Empty()
        a2 = Grammar.Empty()
        self.assertEqual(a,a)
        self.assertTrue(a == a)
        self.assertTrue(a == a2)

    def test_EndOfText(self):
        a = Grammar.EndOfText()
        a2 = Grammar.EndOfText()
        self.assertEqual(a,a)
        self.assertTrue(a == a)
        self.assertTrue(a == a2)

    def test_Fixed(self):
        a = Grammar.Fixed('a')
        a2 = Grammar.Fixed('a')
        b = Grammar.Fixed('b')
        self.assertEqual(a,a)
        self.assertTrue(a == a)
        self.assertTrue(a == a2)
        self.assertFalse(a == b)

    def test_Symbol(self):
        a = Grammar.Symbol('a')
        a2 = Grammar.Symbol('a')
        b = Grammar.Symbol('b')
        self.assertEqual(a,a)
        self.assertTrue(a == a)
        self.assertTrue(a == a2)
        self.assertFalse(a == b)

    def test_Pattern(self):
        a = Grammar.Pattern('a')
        a2 = Grammar.Pattern('a')
        b = Grammar.Pattern('b')
        self.assertEqual(a,a)
        self.assertTrue(a == a)
        self.assertTrue(a == a2)
        self.assertFalse(a == b)

    def test_Repeat1(self):
        a = Grammar.Repeat1([Grammar.Pattern('a')])
        a2 = Grammar.Repeat1([Grammar.Pattern('a')])
        b = Grammar.Repeat1([Grammar.Pattern('b')])
        self.assertEqual(a,a)
        self.assertTrue(a == a)
        self.assertTrue(a == a2)
        self.assertFalse(a == b)

    def test_Choice(self):
        a = Grammar.Choice([Grammar.Pattern('a'), Grammar.Empty()])
        a2 = Grammar.Choice([Grammar.Pattern('a'), Grammar.Empty()])
        b = Grammar.Choice([Grammar.Pattern('a')])
        c = Grammar.Choice([Grammar.Pattern('a'), Grammar.EndOfText()])
        d = Grammar.Choice([Grammar.Fixed('a'), Grammar.Empty()])
        self.assertEqual(a,a)
        self.assertTrue(a == a)
        self.assertTrue(a == a2)
        self.assertFalse(a == b)
        self.assertFalse(a == c)
        self.assertFalse(a == d)

    def test_Seq(self):
        a = Grammar.Seq([Grammar.Pattern('a'), Grammar.Empty()])
        a2 = Grammar.Seq([Grammar.Pattern('a'), Grammar.Empty()])
        b = Grammar.Seq([Grammar.Pattern('a')])
        c = Grammar.Seq([Grammar.Pattern('a'), Grammar.EndOfText()])
        d = Grammar.Seq([Grammar.Fixed('a'), Grammar.Empty()])
        self.assertEqual(a,a)
        self.assertTrue(a == a)
        self.assertTrue(a == a2)
        self.assertFalse(a == b)
        self.assertFalse(a == c)
        self.assertFalse(a == d)

    def test_CrossProduct(self):
        empty = Grammar.Empty()
        end = Grammar.EndOfText()
        fixed = Grammar.Fixed('a')
        symbol = Grammar.Symbol('a')
        pattern = Grammar.Pattern('a')
        choice = Grammar.Choice([Grammar.Pattern('a')])
        repeat1 = Grammar.Repeat1([Grammar.Pattern('a')])
        seq = Grammar.Seq([Grammar.Pattern('a')])

        self.assertTrue( empty == empty )
        self.assertFalse( empty == end )
        self.assertFalse( empty == fixed )
        self.assertFalse( empty == symbol )
        self.assertFalse( empty == pattern )
        self.assertFalse( empty == choice )
        self.assertFalse( empty == repeat1 )
        self.assertFalse( empty == seq )

        self.assertFalse( end == empty )
        self.assertTrue( end == end )
        self.assertFalse( end == fixed )
        self.assertFalse( end == symbol )
        self.assertFalse( end == pattern )
        self.assertFalse( end == choice )
        self.assertFalse( end == repeat1 )
        self.assertFalse( end == seq )

        self.assertFalse( fixed == empty )
        self.assertFalse( fixed == end )
        self.assertTrue( fixed == fixed )
        self.assertFalse( fixed == symbol )
        self.assertFalse( fixed == pattern )
        self.assertFalse( fixed == choice )
        self.assertFalse( fixed == repeat1 )
        self.assertFalse( fixed == seq )

        self.assertFalse( symbol == empty )
        self.assertFalse( symbol == end )
        self.assertFalse( symbol == fixed )
        self.assertTrue( symbol == symbol )
        self.assertFalse( symbol == pattern )
        self.assertFalse( symbol == choice )
        self.assertFalse( symbol == repeat1 )
        self.assertFalse( symbol == seq )

        self.assertFalse( pattern == empty )
        self.assertFalse( pattern == end )
        self.assertFalse( pattern == fixed )
        self.assertFalse( pattern == symbol )
        self.assertTrue( pattern == pattern )
        self.assertFalse( pattern == choice )
        self.assertFalse( pattern == repeat1 )
        self.assertFalse( pattern == seq )

        self.assertFalse( choice == empty )
        self.assertFalse( choice == end )
        self.assertFalse( choice == fixed )
        self.assertFalse( choice == symbol )
        self.assertFalse( choice == pattern )
        self.assertTrue( choice == choice )
        self.assertFalse( choice == repeat1 )
        self.assertFalse( choice == seq )

        self.assertFalse( repeat1 == empty )
        self.assertFalse( repeat1 == end )
        self.assertFalse( repeat1 == fixed )
        self.assertFalse( repeat1 == symbol )
        self.assertFalse( repeat1 == pattern )
        self.assertFalse( repeat1 == choice )
        self.assertTrue( repeat1 == repeat1 )
        self.assertFalse( repeat1 == seq )

        self.assertFalse( seq == empty )
        self.assertFalse( seq == end )
        self.assertFalse( seq == fixed )
        self.assertFalse( seq == symbol )
        self.assertFalse( seq == pattern )
        self.assertFalse( seq == choice )
        self.assertFalse( seq == repeat1 )
        self.assertTrue( seq == seq )


class Rule_Less(unittest.TestCase):
    def test_Empty(self):
        a = Grammar.Empty()
        a2 = Grammar.Empty()
        self.assertFalse(a < a)
        self.assertFalse(a < a2)

    def test_EndOfText(self):
        a = Grammar.EndOfText()
        a2 = Grammar.EndOfText()
        self.assertFalse(a < a)
        self.assertFalse(a < a2)

    def test_Fixed(self):
        a = Grammar.Fixed('a')
        a2 = Grammar.Fixed('a')
        b = Grammar.Fixed('b')
        self.assertFalse(a < a)
        self.assertFalse(a < a2)
        self.assertTrue(a < b)
        self.assertFalse(b < a)

    def test_Symbol(self):
        a = Grammar.Symbol('a')
        a2 = Grammar.Symbol('a')
        b = Grammar.Symbol('b')
        self.assertFalse(a < a)
        self.assertFalse(a < a2)
        self.assertTrue(a < b)
        self.assertFalse(b < a)

    def test_Pattern(self):
        a = Grammar.Pattern('a')
        a2 = Grammar.Pattern('a')
        b = Grammar.Pattern('b')
        self.assertFalse(a < a)
        self.assertFalse(a < a2)
        self.assertTrue(a < b)
        self.assertFalse(b < a)

    def test_Repeat1(self):
        a = Grammar.Repeat1([Grammar.Pattern('a')])
        a2 = Grammar.Repeat1([Grammar.Pattern('a')])
        b = Grammar.Repeat1([Grammar.Pattern('b')])
        self.assertFalse(a < a)
        self.assertFalse(a < a2)
        self.assertTrue(a < b)
        self.assertFalse(b < a)

    def test_Choice(self):
        a = Grammar.Choice([Grammar.Pattern('a'), Grammar.Empty()])
        a2 = Grammar.Choice([Grammar.Pattern('a'), Grammar.Empty()])
        b = Grammar.Choice([Grammar.Pattern('a')])
        c = Grammar.Choice([Grammar.Pattern('a'), Grammar.EndOfText()])
        d = Grammar.Choice([Grammar.Fixed('a'), Grammar.Empty()])
        self.assertFalse(a < a)
        self.assertFalse(a < a2)
        self.assertTrue(a > b)
        self.assertTrue(b < a)
        self.assertTrue(a < c)
        self.assertTrue(d < a)

    def test_Seq(self):
        a = Grammar.Seq([Grammar.Pattern('a'), Grammar.Empty()])
        a2 = Grammar.Seq([Grammar.Pattern('a'), Grammar.Empty()])
        b = Grammar.Seq([Grammar.Pattern('a')])
        c = Grammar.Seq([Grammar.Pattern('a'), Grammar.EndOfText()])
        d = Grammar.Seq([Grammar.Fixed('a'), Grammar.Empty()])
        self.assertFalse(a < a)
        self.assertFalse(a < a2)
        self.assertTrue(a > b)
        self.assertTrue(b < a)
        self.assertTrue(a < c)
        self.assertTrue(d < a)

    def test_CrossProduct(self):
        empty = Grammar.Empty()
        end = Grammar.EndOfText()
        fixed = Grammar.Fixed('a')
        symbol = Grammar.Symbol('a')
        pattern = Grammar.Pattern('a')
        choice = Grammar.Choice([Grammar.Pattern('a')])
        repeat1 = Grammar.Repeat1([Grammar.Pattern('a')])
        seq = Grammar.Seq([Grammar.Pattern('a')])

        self.assertFalse( empty < empty )
        self.assertTrue( empty < end )
        self.assertFalse( empty < fixed )
        self.assertFalse( empty < symbol )
        self.assertFalse( empty < pattern )
        self.assertFalse( empty < choice )
        self.assertFalse( empty < repeat1 )
        self.assertFalse( empty < seq )

        self.assertFalse( end < empty )
        self.assertFalse( end < end )
        self.assertFalse( end < fixed )
        self.assertFalse( end < symbol )
        self.assertFalse( end < pattern )
        self.assertFalse( end < choice )
        self.assertFalse( end < repeat1 )
        self.assertFalse( end < seq )

        self.assertTrue( fixed < empty )
        self.assertTrue( fixed < end )
        self.assertFalse( fixed < fixed )
        self.assertFalse( fixed < symbol )
        self.assertTrue( fixed < pattern )
        self.assertFalse( fixed < choice )
        self.assertFalse( fixed < repeat1 )
        self.assertFalse( fixed < seq )

        self.assertTrue( symbol < empty )
        self.assertTrue( symbol < end )
        self.assertTrue( symbol < fixed )
        self.assertFalse( symbol < symbol )
        self.assertTrue( symbol < pattern )
        self.assertFalse( symbol < choice )
        self.assertFalse( symbol < repeat1 )
        self.assertFalse( symbol < seq )

        self.assertTrue( pattern < empty )
        self.assertTrue( pattern < end )
        self.assertFalse( pattern < fixed )
        self.assertFalse( pattern < symbol )
        self.assertFalse( pattern < pattern )
        self.assertFalse( pattern < choice )
        self.assertFalse( pattern < repeat1 )
        self.assertFalse( pattern < seq )

        self.assertTrue( choice < empty )
        self.assertTrue( choice < end )
        self.assertTrue( choice < fixed )
        self.assertTrue( choice < symbol )
        self.assertTrue( choice < pattern )
        self.assertFalse( choice < choice )
        self.assertTrue( choice < repeat1 )
        self.assertTrue( choice < seq )

        self.assertTrue( repeat1 < empty )
        self.assertTrue( repeat1 < end )
        self.assertTrue( repeat1 < fixed )
        self.assertTrue( repeat1 < symbol )
        self.assertTrue( repeat1 < pattern )
        self.assertFalse( repeat1 < choice )
        self.assertFalse( repeat1 < repeat1 )
        self.assertFalse( repeat1 < seq )

        self.assertTrue( seq < empty )
        self.assertTrue( seq < end )
        self.assertTrue( seq < fixed )
        self.assertTrue( seq < symbol )
        self.assertTrue( seq < pattern )
        self.assertFalse( seq < choice )
        self.assertTrue( seq < repeat1 )
        self.assertFalse( seq < seq )

if __name__ == '__main__':
    unittest.main()
