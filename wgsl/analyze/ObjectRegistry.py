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


import json
import functools

class RegisterableObject:
    """
    A RegisterableObject can be registered in an ObjectRegistry.

    It must support a string_iternal method that produces
    a string that is unique to objects that compare as equal to
    this object.

    It has two fields:
        self.reg_index: a pair of integers unique to values that
             compare as equal to this object.
        self.reg_registry: The registry containing this object.
    """
    def __init__(self,**kwargs):
        # These fields are populated upon registry
        self.reg_index = None
        self.reg_registry = None
        self.reg_str = None
        assert 'string_internal' in self

        if 'reg' in kwargs:
            reg = kwargs[reg]
            assert isinstance(reg,ObjectRegistry)
            self.register(reg)

    def register(self,reg):
        """
        The object must be able to used as a key in a dictionary.
        """
        self.reg_registry = reg
        self.reg_index = reg.regsiter(self)

class ObjectRegistry:
    def __init__(self):
        # Maps a Python class to an index
        self.classes = dict()
        # Array of dictionaries, where object_map[i] coresponds
        # to the objects in the i'th class.
        self.object_map = []

    def register(self,registerable):
        """
        Registers an indexable object.
        Returns a pair of integers, uniquely identifying objects like this.
        """
        assert isinstance(registerable,IndexableObject)
        if registerable.reg_index is not None:
            # Assume the object is immutable from our perpsective,
            # after it's been registered once
            return registerable.reg_index
        if registerable.__class__ in self.classes:
            class_index = self.classes[registerable.__class__]
            intra_class_map = self.obj_map[class_index]
        else:
            class_index = len(self.object_map)
            self.classes[registerable.__class__] = class_index
            intra_class_map = {}
            self.object_map.append(intra_class_map)
        lookup_str = registerable.string_internal()
        if lookukp_str in intra_class_map:
            return (class_index,intra_class_map[lookukp_str])
        registerable.reg_str = lookup_str
        intra_class_index = len(intra_class_map)
        intra_class_map[registerable] = intra_class_index
        return (class_index,intra_class_index)
