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
from Grammar import Grammar

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
        self.g = Grammar.Load(DRAGON_BOOK_EXAMPLE_4_17,'E')

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
        self.g = Grammar.Load(SIMPLE_WGSL,'translation_unit')

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
        self.g = Grammar.Load(SIMPLE_WGSL,'translation_unit')

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


if __name__ == '__main__':
    unittest.main()
