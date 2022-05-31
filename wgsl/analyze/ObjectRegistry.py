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

class RegistryInfo:
    """
    Info tracked for a registered object
    """
    def __init__(self,registry,obj,index,unique_str):
        # The ObjectRegistry managing this object
        self.registry = registry
        # The first equivalent registered object
        self.obj = obj
        # The unique integer index for this object, in the context of the registry
        self.index = index
        # The string that distinguishes the registered object from all others
        # in the registry
        self.str = unique_str

    def __eq__(self,other):
        return (self.index == other.index) and (self.registry == other.registry)


@functools.total_ordering
class RegisterableObject:
    """
    A RegisterableObject can be registered in an ObjectRegistry.

    It must support a string_iternal method that produces
    a string that is unique to objects that compare as equal to
    this object.

    It has a reg_info object.
    """
    def __init__(self,**kwargs):
        assert 'string_internal' in dir(self)
        # The fields are populated when this object is registered.
        self.reg_info = RegistryInfo(None,None,None,None)

    def register_conditionally(self,**kwargs):
        if 'reg' in kwargs:
            reg = kwargs['reg']
            self.register(reg)

    def register(self,reg):
        """
        The object must be able to used as a key in a dictionary.
        """
        reg.register(self)

    def __eq__(self,other):
        if self.reg_info.index is not None:
            if isinstance(other,RegisterableObject) and other.reg_info.index is not None:
                return self.reg_info == other.reg_info
            else:
                return False
        return self.x__eq__(other)

    def __lt__(self,other):
        if self.reg_info.index is not None:
            if isinstance(other,RegisterableObject) and other.reg_info.index is not None:
                return self.reg_info.index < other.reg_info.index
            else:
                return False
        return self.x__lt__(other)

    def __hash__(self):
        if self.reg_info.index is not None:
            return self.reg_info.index.__hash__()
        return self.x__hash__()


class ObjectRegistry:
    """
    An ObjectRegistry maintains a unique index for unique objects,
    where uniqueness for an object is determined by the pair:
        (object.__class__, object.string_internal())
    """

    def __init__(self):
        # Maps an object unique string to a pair:
        #  (unique index,
        #   first regsitered object with that unique string)
        self.str_to_object = dict()

    def register(self,registerable):
        """
        Registers an indexable object.

        Returns:
            The first object registered that compares as equal.
            If this object is the first such one, then it also
            populates the object's reg_info field.
        """
        assert 'reg_info' in dir(registerable)
        assert registerable.reg_info is not None
        if registerable.reg_info.index is not None:
            # Assume immutability after it's been registered once.
            assert registerable.reg_info.registry is self
            assert registerable.reg_info.str is not None
            return registerable.reg_info.obj

        lookup_str = "{} {}".format(registerable.__class__.__name__,registerable.string_internal())

        if lookup_str in self.str_to_object:
            return self.str_to_object[lookup_str]
        registerable.reg_info = RegistryInfo(self, registerable, len(self.str_to_object), lookup_str)
        self.str_to_object[lookup_str] = registerable
        return registerable

    def __str__(self):
        def sort_key(registerable):
            return registerable.reg_info.index
        objects = sorted(self.str_to_object.values(), key = lambda o: o.reg_info.index)
        parts = []
        parts.append("<ObjectRegistry>\n")
        for o in objects:
            parts.append(" {} {}\n".format(o.reg_info.index, o.reg_info.str))
        parts.append("</ObjectRegistry>\n")
        return "".join(parts)
