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

from wgsl_unit_tests import Case, XFail

cases = [
    Case("alias abc=0;"),
    Case("alias z = a<b;"),
    Case("alias z = a>b;"),
    Case("alias z = (a<b)>c;"),
    Case("alias z = a<(b>c);"),
    Case("alias z = a((b<c), d>(e));"),
    Case("alias z = a<b[c>(d)];"),
    Case("alias z = a<b;c>d();"),
    Case("fn z() if a < b {} else if c > d {}}"),
    Case("alias z = a<b&&c>d;"),
    Case("alias z = a<b||c>d;"),
    Case("alias z = a<b<c||d>>;"),
    Case("alias z = a<b>();"),
    XFail("alias z = a<b>c;"),
    Case("alias z = vec3<i32>;"),
    Case("alias z = vec3<i32>();"),
    Case("alias z = array<vec3<i32>,5>;"),
    Case("alias z = a(b<c, d>(e));"),
    Case("alias z = a<1+2>();"),
    Case("alias z = a<1,b>();"),
    Case("alias z = a<b,c>=d;"),
    Case("alias z = a<b,c>=d>();"),
    Case("alias z = a<b<c>>=;"),
    Case("alias z = a<b>c>();"),
    Case("alias z = a<b<c>();"),
    Case("alias z = a<b<c>>();"),
    Case("alias z = a<b<c>()>();"),
    Case("alias z = a<b>.c;"),
    Case("alias z = a<(b&&c)>d;"),
    Case("alias z = a<(b||c)>d;"),
    Case("alias z = a<b<(c||d)>>;"),
]
