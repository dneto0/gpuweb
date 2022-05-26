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

DRAGON_BOOK_EXAMPLE_4_42 = """
{
  "name": "dragon_book_ex_4_42",
  "word": "id",
  "rules": {
    "translation_unit": {
      "type": "SEQ",
      "members": [
        {
          "type": "SYMBOL",
          "name": "C"
        },
        {
          "type": "SYMBOL",
          "name": "C"
        }
      ]
    },
    "C": {
      "type": "CHOICE",
      "members": [
        {
          "type": "SEQ",
          "members": [
            {
              "type": "SYMBOL",
              "name": "c"
            },
            {
              "type": "SYMBOL",
              "name": "C"
            }
          ]
        },
        {
          "type": "SYMBOL",
          "name": "d"
        }
      ]
    },
    "c": {
      "type": "TOKEN",
      "content": {
        "type": "STRING",
        "value": "c"
      }
    },
    "d": {
      "type": "TOKEN",
      "content": {
        "type": "STRING",
        "value": "d"
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
    "_blankspace": {
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
      "name": "_blankspace"
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
        it = Grammar.Item("e",Grammar.Empty(),0)
        self.assertEqual(it.items, [])
        self.assertEqual(it.lhs, Grammar.Symbol("e"))
        self.assertEqual(it.position, 0)

    def test_Item_OfEmpty_PosTooSmall(self):
        self.assertRaises(RuntimeError, self.make_item, "a", Grammar.Empty(), -1)

    def test_Item_OfEmpty_PosTooBig(self):
        self.assertRaises(RuntimeError, self.make_item, "a", Grammar.Empty(), 1)

    def test_Item_OfFixed_Pos0(self):
        t = Grammar.Fixed('x')
        it = Grammar.Item("t",t,0)
        self.assertEqual(it.rule, t)
        self.assertEqual(it.position, 0)
        self.assertEqual(it.items, [t])

    def test_Item_OfFixed_Pos1(self):
        t = Grammar.Fixed('x')
        it = Grammar.Item("t",t,1)
        self.assertEqual(it.lhs, Grammar.Symbol("t"))
        self.assertEqual(it.rule, t)
        self.assertEqual(it.position, 1)
        self.assertEqual(it.items, [t])

    def test_Item_OfFixed_PosTooSmall(self):
        self.assertRaises(RuntimeError, self.make_item, "a", Grammar.Fixed('x'), -1)

    def test_Item_OfFixed_PosTooBig(self):
        self.assertRaises(RuntimeError, self.make_item, "a", Grammar.Fixed('x'), 2)

    def test_Item_OfPattern_Pos0(self):
        t = Grammar.Pattern('[a-z]+')
        it = Grammar.Item("t",t,0)
        self.assertEqual(it.rule, t)
        self.assertEqual(it.position, 0)
        self.assertEqual(it.items, [t])

    def test_Item_OfPattern_Pos1(self):
        t = Grammar.Pattern('[a-z]+')
        it = Grammar.Item("t",t,1)
        self.assertEqual(it.rule, t)
        self.assertEqual(it.position, 1)
        self.assertEqual(it.items, [t])

    def test_Item_OfPattern_PosTooSmall(self):
        self.assertRaises(RuntimeError, self.make_item, "a", Grammar.Pattern('[a-z]+'), -1)

    def test_Item_OfPattern_PosTooBig(self):
        self.assertRaises(RuntimeError, self.make_item, "a", Grammar.Pattern('[a-z]+'), 2)

    def test_Item_OfSymbol_Pos0(self):
        t = Grammar.Symbol('x')
        it = Grammar.Item("t",t,0)
        self.assertEqual(it.rule, t)
        self.assertEqual(it.position, 0)
        self.assertEqual(it.items, [t])

    def test_Item_OfSymbol_Pos1(self):
        t = Grammar.Symbol('x')
        it = Grammar.Item("t",t,1)
        self.assertEqual(it.rule, t)
        self.assertEqual(it.position, 1)
        self.assertEqual(it.items, [t])

    def test_Item_OfSymbol_PosTooSmall(self):
        self.assertRaises(RuntimeError, self.make_item, "a", Grammar.Symbol('x'), -1)

    def test_Item_OfSymbol_PosTooBig(self):
        self.assertRaises(RuntimeError, self.make_item, "a", Grammar.Symbol('x'), 2)

    def example_seq(self):
        return Grammar.Seq([Grammar.Fixed('x'), Grammar.Symbol('blah')])

    def test_Item_OfSeq_Pos0(self):
        t = self.example_seq()
        it = Grammar.Item("t",t,0)
        self.assertEqual(it.rule, t)
        self.assertEqual(it.position, 0)
        self.assertEqual(it.items, [i for i in t])

    def test_Item_OfSeq_Pos1(self):
        t = self.example_seq()
        it = Grammar.Item("t",t,1)
        self.assertEqual(it.rule, t)
        self.assertEqual(it.position, 1)
        self.assertEqual(it.items, [i for i in t])

    def test_Item_OfSeq_Pos2(self):
        t = self.example_seq()
        it = Grammar.Item("t",t,2)
        self.assertEqual(it.rule, t)
        self.assertEqual(it.position, 2)
        self.assertEqual(it.items, [i for i in t])

    def test_Item_OfSeq_PosTooSmall(self):
        self.assertRaises(RuntimeError, self.make_item, "s", self.example_seq(), -1)

    def test_Item_OfSeq_PosTooBig(self):
        self.assertRaises(RuntimeError, self.make_item, "s", self.example_seq(), 3)

    def test_Item_OfChoice(self):
        self.assertRaises(RuntimeError, self.make_item, "c", Grammar.Choice([]), 0)

    def test_Item_OfRepeat1(self):
        self.assertRaises(RuntimeError, self.make_item, "c", Grammar.Repeat1([Grammar.Empty()]), 0)

    def test_Item_is_accepting(self):
        tu = Grammar.Seq([Grammar.Fixed('translation_unit')])
        l0 = Grammar.Item(Grammar.LANGUAGE,tu,0)
        l1 = Grammar.Item(Grammar.LANGUAGE,tu,1)
        s0 = Grammar.Item("S",tu,0)
        s1 = Grammar.Item("S",tu,1)
        self.assertFalse(l0.is_accepting())
        self.assertTrue(l1.is_accepting())
        self.assertFalse(s0.is_accepting())
        self.assertFalse(s1.is_accepting())

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

    def test_Choice_internal_order(self):
        a1 = Grammar.Choice([Grammar.Fixed('a'), Grammar.Fixed('b')])
        a2 = Grammar.Choice([Grammar.Fixed('b'), Grammar.Fixed('a')])
        self.assertTrue(a1 == a2)
        self.assertFalse(a1 < a2)
        self.assertFalse(a2 < a1)

    def test_Seq_internal_order(self):
        a1 = Grammar.Seq([Grammar.Fixed('a'), Grammar.Fixed('b')])
        a2 = Grammar.Seq([Grammar.Fixed('b'), Grammar.Fixed('a')])
        self.assertFalse(a1 == a2)
        self.assertTrue(a1 < a2)
        self.assertFalse(a2 < a1)

    def test_Seq_internal_order(self):
        a1 = Grammar.Seq([Grammar.Fixed('a'), Grammar.Fixed('b')])
        a2 = Grammar.Seq([Grammar.Fixed('b'), Grammar.Fixed('a')])
        self.assertFalse(a1 == a2)
        self.assertTrue(a1 < a2)
        self.assertFalse(a2 < a1)

class Item_is_kernel(unittest.TestCase):

    def test_Item_OfEmpty(self):
        it = Grammar.Item("e",Grammar.Empty(),0)
        self.assertFalse(it.is_kernel())

    def test_Item_OfFixed_Pos0(self):
        it = Grammar.Item("e",Grammar.Fixed('a'),0)
        self.assertFalse(it.is_kernel())

    def test_Item_OfFixed_Pos1(self):
        it = Grammar.Item("e",Grammar.Fixed('a'),1)
        self.assertTrue(it.is_kernel())

    def test_Item_OfPattern_Pos0(self):
        it = Grammar.Item("e",Grammar.Pattern('a'),0)
        self.assertFalse(it.is_kernel())

    def test_Item_OfPattern_Pos1(self):
        it = Grammar.Item("e",Grammar.Pattern('a'),1)
        self.assertTrue(it.is_kernel())

    def test_Item_OfSymbol_Pos0(self):
        it = Grammar.Item("e",Grammar.Symbol('a'),0)
        self.assertFalse(it.is_kernel())

    def test_Item_OfSymbol_Pos1(self):
        it = Grammar.Item("e",Grammar.Symbol('a'),1)
        self.assertTrue(it.is_kernel())

    def test_Item_OfSeq_Pos0(self):
        it = Grammar.Item("s",Grammar.Seq([Grammar.Fixed('a')]),0)
        self.assertFalse(it.is_kernel())

    def test_Item_OfSeq_Pos1(self):
        it = Grammar.Item("s",Grammar.Seq([Grammar.Fixed('a')]),1)
        self.assertTrue(it.is_kernel())

    def test_Item_OfLanguage_Pos0(self):
        it = Grammar.Item(Grammar.LANGUAGE,Grammar.Seq([Grammar.Fixed('a'),Grammar.EndOfText()]),0)
        self.assertTrue(it.is_kernel())

    def test_Item_OfLanguage_Pos1(self):
        it = Grammar.Item(Grammar.LANGUAGE,Grammar.Seq([Grammar.Fixed('a'),Grammar.EndOfText()]),1)
        self.assertTrue(it.is_kernel())

    def test_Item_OfLanguage_Pos2(self):
        it = Grammar.Item(Grammar.LANGUAGE,Grammar.Seq([Grammar.Fixed('a'),Grammar.EndOfText()]),2)
        self.assertTrue(it.is_kernel())

class ItemSet_Less(unittest.TestCase):

    def setUp(self):
        self.g = Grammar.Grammar.Load(DRAGON_BOOK_EXAMPLE_4_42,'translation_unit')
        self.C = self.g.rules["C"]
        self.c = self.g.rules["c"]
        self.d = self.g.rules["d"]
        self.el = Grammar.LookaheadSet({})

    def iC(self,pos=0):
        return Grammar.Item("C",self.C[0],pos)
    def ic(self,pos=0):
        return Grammar.Item("c",self.c,0)
    def id(self,pos=0):
        return Grammar.Item("d",self.c,0)

    def is_C_0(self,closed=True,la=Grammar.LookaheadSet({})):
        result = Grammar.ItemSet({self.iC():la})
        result = result.close(self.g) if closed else result
        return result
    def is_C_1(self,closed=True,la=Grammar.LookaheadSet({})):
        result = Grammar.ItemSet({self.iC(1):la})
        result = result.close(self.g) if closed else result
        return result

    def test_Less(self):
        i0 = self.is_C_0()
        i1 = self.is_C_1()
        self.assertLess(i0,i1)
        self.assertGreater(i1,i0)

    def test_Equal(self):
        i0 = self.is_C_0()
        i1 = self.is_C_1()
        self.assertEqual(i0,i0)
        self.assertEqual(i1,i1)
        self.assertFalse(i0==i1)
        self.assertFalse(i1==i0)

    def test_Less(self):
        i0 = self.is_C_0()
        i1 = self.is_C_1()
        # The "dot" character is higher than '
        self.assertLess(i1,i0)
        self.assertGreater(i0,i1)

    def test_Less_Lookahead(self):
        i0c = self.is_C_0(la=Grammar.LookaheadSet({self.c}))
        i0d = self.is_C_0(la=Grammar.LookaheadSet({self.d}))
        self.assertLess(i0c,i0d)
        self.assertGreater(i0d,i0c)

    def test_Equal_Lookahead(self):
        i0c = self.is_C_0(la=Grammar.LookaheadSet({self.c}))
        i0d = self.is_C_0(la=Grammar.LookaheadSet({self.d}))
        self.assertEqual(i0c,i0c)
        self.assertEqual(i0d,i0d)
        self.assertFalse(i0c==i0d)
        self.assertFalse(i0d==i0c)

    def test_Less_Lookahead_Unclosed(self):
        i0c = self.is_C_0(closed=False,la=Grammar.LookaheadSet({self.c}))
        i0d = self.is_C_0(closed=False,la=Grammar.LookaheadSet({self.d}))
        self.assertLess(i0c,i0d)
        self.assertGreater(i0d,i0c)

    def test_Equal_Lookahead_Unclosed(self):
        i0c = self.is_C_0(closed=False,la=Grammar.LookaheadSet({self.c}))
        i0d = self.is_C_0(closed=False,la=Grammar.LookaheadSet({self.d}))
        self.assertEqual(i0c,i0c)
        self.assertEqual(i0d,i0d)
        self.assertFalse(i0c==i0d)
        self.assertFalse(i0d==i0c)

    def test_Less_Lookahead_ClosedFT(self):
        i0c = self.is_C_0(closed=False,la=Grammar.LookaheadSet({self.c}))
        i0d = self.is_C_0(closed=True,la=Grammar.LookaheadSet({self.d}))
        self.assertLess(i0c,i0d)
        self.assertGreater(i0d,i0c)

    def test_Equal_Lookahead_ClosedFT(self):
        i0c = self.is_C_0(closed=False,la=Grammar.LookaheadSet({self.c}))
        i0d = self.is_C_0(closed=True,la=Grammar.LookaheadSet({self.d}))
        self.assertEqual(i0c,i0c)
        self.assertEqual(i0d,i0d)
        self.assertFalse(i0c==i0d)
        self.assertFalse(i0d==i0c)

    def test_Less_Lookahead_ClosedTF(self):
        i0c = self.is_C_0(closed=True,la=Grammar.LookaheadSet({self.c}))
        i0d = self.is_C_0(closed=False,la=Grammar.LookaheadSet({self.d}))
        # We only compare on content, never by the index. So closure
        # doesn't matter here.
        self.assertLess(i0c,i0d)
        self.assertGreater(i0d,i0c)

    def test_Equal_Lookahead_ClosedTF(self):
        i0c = self.is_C_0(closed=True,la=Grammar.LookaheadSet({self.c}))
        i0d = self.is_C_0(closed=False,la=Grammar.LookaheadSet({self.d}))
        self.assertEqual(i0c,i0c)
        self.assertEqual(i0d,i0d)
        self.assertFalse(i0c==i0d)
        self.assertFalse(i0d==i0c)

class ItemSet_is_accepting(unittest.TestCase):

    def setUp(self):
        self.g = Grammar.Grammar.Load(DRAGON_BOOK_EXAMPLE_4_42,'translation_unit')
        self.L = self.g.rules[Grammar.LANGUAGE]
        self.C = self.g.rules["C"]
        self.c = self.g.rules["c"]
        self.d = self.g.rules["d"]
        self.l_empty = Grammar.LookaheadSet({})
        self.l_end = Grammar.LookaheadSet({Grammar.EndOfText()})
        self.l_end_and = Grammar.LookaheadSet({Grammar.Fixed('end'),Grammar.EndOfText()})

    def iL(self,pos=0):
        return Grammar.Item(Grammar.LANGUAGE,self.L[0],pos)
    def iC(self,pos=0):
        return Grammar.Item("C",self.C[0],pos)

    def test_L_empty(self):
        i0 = self.iL()
        i0_ = Grammar.ItemSet({i0:self.l_empty}).close(self.g)
        self.assertFalse(i0_.is_accepting())
        i1 = self.iL(1)
        i1_ = Grammar.ItemSet({i1:self.l_empty})
        self.assertFalse(i1_.is_accepting())

    def test_L_end_alone(self):
        i0 = self.iL()
        i0_ = Grammar.ItemSet({i0:self.l_end}).close(self.g)
        self.assertFalse(i0_.is_accepting())
        i1 = self.iL(1)
        i1_ = Grammar.ItemSet({i1:self.l_end})
        self.assertTrue(i1_.is_accepting())

    def test_L_end_and(self):
        i0 = self.iL()
        i0_ = Grammar.ItemSet({i0:self.l_end_and}).close(self.g)
        self.assertFalse(i0_.is_accepting())
        i1 = self.iL(1)
        i1_ = Grammar.ItemSet({i1:self.l_end_and})
        self.assertTrue(i1_.is_accepting())

    def test_C_empty(self):
        i0 = self.iC()
        i0_ = Grammar.ItemSet({i0:self.l_empty}).close(self.g)
        self.assertFalse(i0_.is_accepting())
        i1 = self.iC(1)
        i1_ = Grammar.ItemSet({i1:self.l_empty}).close(self.g)
        self.assertFalse(i1_.is_accepting())

    def test_C_end_alone(self):
        i0 = self.iC()
        i0_ = Grammar.ItemSet({i0:self.l_end}).close(self.g)
        self.assertFalse(i0_.is_accepting())
        i1 = self.iC(1)
        i1_ = Grammar.ItemSet({i1:self.l_end}).close(self.g)
        self.assertFalse(i1_.is_accepting())

    def test_C_end_and(self):
        i0 = self.iC()
        i0_ = Grammar.ItemSet({i0:self.l_end_and}).close(self.g)
        self.assertFalse(i0_.is_accepting())
        i1 = self.iC(1)
        i1_ = Grammar.ItemSet({i1:self.l_end_and}).close(self.g)
        self.assertFalse(i1_.is_accepting())

class Lookahead_is_a_set(unittest.TestCase):
    def test_init_empty(self):
        x = Grammar.LookaheadSet()
        self.assertTrue(x == set())

    def test_init_single(self):
        x = Grammar.LookaheadSet({1})
        self.assertTrue(x == set({1}))

    def test_init_several(self):
        x = Grammar.LookaheadSet({1,2,9})
        self.assertTrue(x == set({9,2,1}))

    def test_str_empty(self):
        x = Grammar.LookaheadSet({})
        self.assertEqual(str(x),"{}")

    def test_str_several_is_ordered(self):
        x = Grammar.LookaheadSet({9,2,1})
        self.assertEqual(str(x),"{1 2 9}")

class Lookahead_merge(unittest.TestCase):
    def test_merge_empty(self):
        x = Grammar.LookaheadSet({1,2,3})
        b = x.merge(Grammar.LookaheadSet({}))
        self.assertEqual(str(x),"{1 2 3}")
        self.assertFalse(b)

    def test_merge_same(self):
        x = Grammar.LookaheadSet({1,2,3})
        b = x.merge(Grammar.LookaheadSet({1,2,3}))
        self.assertEqual(str(x),"{1 2 3}")
        self.assertFalse(b)

    def test_merge_disjoint(self):
        x = Grammar.LookaheadSet({-1,9,4})
        b = x.merge(Grammar.LookaheadSet({1,2,3}))
        self.assertEqual(str(x),"{-1 1 2 3 4 9}")
        self.assertTrue(b)

    def test_merge_overlap(self):
        x = Grammar.LookaheadSet({1,2,4})
        b = x.merge(Grammar.LookaheadSet({1,2,3}))
        self.assertEqual(str(x),"{1 2 3 4}")
        self.assertTrue(b)


EX442_LR1_ITEMS_CLOSED_EXPECTED = sorted(map(lambda x: x.rstrip(), """#0
C -> · 'c' C : {'c' 'd'}
C -> · 'd' : {'c' 'd'}
language -> · translation_unit EndOfText : {EndOfText}
translation_unit -> · C C : {EndOfText}
===
#1
language -> translation_unit · EndOfText : {EndOfText}
===
#2
C -> · 'c' C : {EndOfText}
C -> · 'd' : {EndOfText}
translation_unit -> C · C : {EndOfText}
===
#3
C -> 'c' · C : {'c' 'd'}
C -> · 'c' C : {'c' 'd'}
C -> · 'd' : {'c' 'd'}
===
#3
C -> 'c' · C : {EndOfText}
C -> · 'c' C : {EndOfText}
C -> · 'd' : {EndOfText}
===
#4
C -> 'd' · : {'c' 'd'}
===
#4
C -> 'd' · : {EndOfText}
===
#5
C -> 'c' C · : {'c' 'd'}
===
#5
C -> 'c' C · : {EndOfText}
===
#6
translation_unit -> C C · : {EndOfText}
""".split("===\n")))

EX442_LALR1_ITEMS_CLOSED_EXPECTED = sorted(map(lambda x: x.rstrip(), """#0
C -> · 'c' C : {'c' 'd' EndOfText}
C -> · 'd' : {'c' 'd' EndOfText}
language -> · translation_unit EndOfText : {EndOfText}
translation_unit -> · C C : {EndOfText}
===
#1
language -> translation_unit · EndOfText : {EndOfText}
===
#2
C -> · 'c' C : {EndOfText}
C -> · 'd' : {EndOfText}
translation_unit -> C · C : {EndOfText}
===
#3
C -> 'c' · C : {'c' 'd' EndOfText}
C -> · 'c' C : {'c' 'd' EndOfText}
C -> · 'd' : {'c' 'd' EndOfText}
===
#4
C -> 'd' · : {'c' 'd' EndOfText}
===
#5
C -> 'c' C · : {'c' 'd' EndOfText}
===
#6
translation_unit -> C C · : {EndOfText}
""".split("===\n")))


#   translation_unit -> @ *
STAR_GRAMMAR = """ {
  "name": "firsts",
  "rules": {
    "s": {
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
        }
      ]
    },
    "at": {
      "type": "TOKEN",
      "content": {
        "type": "STRING",
        "value": "@"
      }
    }
  },
  "extras": [],
  "conflicts": [],
  "precedences": [],
  "externals": [
  ],
  "inline": [
  ],
  "supertypes": []
}
"""
STAR_ITEMS_EXPECTED = sorted(map(lambda x: x.rstrip(), """#0
at -> · '@' : {'@' EndOfText}
language -> · s EndOfText : {EndOfText}
s -> · s/0.0 : {EndOfText}
s/0.0 -> · s/0.0/0 : {EndOfText}
s/0.0/0 -> · at s/0.0/0 : {EndOfText}
===
#1
language -> s · EndOfText : {EndOfText}
===
#2
s -> s/0.0 · : {EndOfText}
===
#3
s/0.0 -> s/0.0/0 · : {EndOfText}
===
#4
at -> · '@' : {'@' EndOfText}
s/0.0/0 -> at · s/0.0/0 : {EndOfText}
s/0.0/0 -> · at s/0.0/0 : {EndOfText}
===
#5
at -> '@' · : {'@' EndOfText}
===
#6
s/0.0/0 -> at s/0.0/0 · : {EndOfText}
""".split("===\n")))

class LR1_items(unittest.TestCase):
    def test_ex442(self):
        g = Grammar.Grammar.Load(DRAGON_BOOK_EXAMPLE_4_42,'translation_unit')
        got = g.LR1_ItemSets()
        got_str = [str(i) for i in got]
        self.assertEqual(got_str, EX442_LR1_ITEMS_CLOSED_EXPECTED)

class LALR1_items(unittest.TestCase):
    def test_ex442(self):
        g = Grammar.Grammar.Load(DRAGON_BOOK_EXAMPLE_4_42,'translation_unit')
        expected = EX442_LALR1_ITEMS_CLOSED_EXPECTED
        got = g.LALR1_ItemSets()
        got_str = [str(i) for i in got]
        #print("got\n")
        #print("\n===\n".join(got_str))
        #print("end got\n")
        #print("\nexpected\n")
        #print("\n===\n".join(expected))
        #print("end expected\n")
        self.assertEqual(got_str, expected)

    def test_star(self):
        g = Grammar.Grammar.Load(STAR_GRAMMAR,'s')
        expected = STAR_ITEMS_EXPECTED
        got = g.LALR1_ItemSets()
        got_str = [str(i) for i in got]
        self.assertEqual(got_str, expected)

EX442_ACTIONS = """[#0 'c']: s#3
[#0 'd']: s#4
[#1 EndOfText]: acc
[#2 'c']: s#3
[#2 'd']: s#4
[#3 'c']: s#3
[#3 'd']: s#4
[#4 'c']: r#0
[#4 'd']: r#0
[#4 EndOfText]: r#0
[#5 'c']: r#1
[#5 'd']: r#1
[#5 EndOfText]: r#1
[#6 EndOfText]: r#2
"""

class LALR1_actions(unittest.TestCase):
    def test_ex442(self):
        g = Grammar.Grammar.Load(DRAGON_BOOK_EXAMPLE_4_42,'translation_unit')
        expected = EX442_ACTIONS
        parse_table = g.LALR1()
        got = "".join(parse_table.action_parts())
        self.assertEqual(got, expected)

EX442_GOTOS = """[#0 C]: #2
[#0 translation_unit]: #1
[#2 C]: #6
[#3 C]: #5
"""

class LALR1_gotos(unittest.TestCase):
    def test_ex442(self):
        g = Grammar.Grammar.Load(DRAGON_BOOK_EXAMPLE_4_42,'translation_unit')
        expected = EX442_GOTOS
        parse_table = g.LALR1()
        got = "".join(parse_table.goto_parts())
        self.assertEqual(got, expected)

if __name__ == '__main__':
	unittest.main()
