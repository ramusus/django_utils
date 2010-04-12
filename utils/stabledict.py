#! /usr/bin/env python
# (X)Emacs: -*- mode: python; coding: utf-8 -*-
# stabledict.py,v 1.13 2007/08/28 07:53:44 martin Exp
# This module has been tested with CPython 2.2.3, 2.3.5, 2.4.4, 2.5 and  2.5.1.
# It won't compile on Python 2.1.X or lower because of missing features.
# It won't work with Python 3.X because of the changed dict protocol. (PEP3106)

"""
A dictionary class remembering insertion order.

Order (i.e. the sequence) of insertions is remembered (internally
stored in a hidden list attribute) and replayed when iterating. A
StableDict does NOT sort or organize the keys in any other way.
"""

from __future__ import generators
from warnings import warn as _warn

__all__       = ("StableDict",)
__author__    = "Martin Kammerhofer <mkamm@gmx.net>"
__revision__  = "1.13"
__date__      = "2007/08/28 07:53:44"
__copyright__ = "Copyright (c) 2007 Martin Kammerhofer"
__license__   = "PSF"
__pychecker__ = "unusednames=__date__,__copyright__,__license__"


# Helper metaclass-function.  Not exported by default but accessible
# as StableDict.__metaclass__.
def copy_baseclass_docs(classname, bases, dict, metaclass=type):
    """Copy docstrings from baseclass.

    When overriding methods in a derived class the docstrings can
    frequently be copied from the base class unmodified.  According to
    the DRY principle (Don't Repeat Yourself) this should be
    automated. Putting a reference to this function into the
    __metaclass__ slot of a derived class will automatically copy
    docstrings from the base classes for all doc-less members of the
    derived class.
    """
    for (name, member) in dict.iteritems():
        if getattr(member, "__doc__", None):
            continue
        for base in bases: # look only in direct ancestors
            basemember = getattr(base, name, None)
            if not basemember:
                continue
            basememberdoc = getattr(basemember, "__doc__", None)
            if basememberdoc:
                member.__doc__ = basememberdoc
    return metaclass(classname, bases, dict)


# String constants for Exceptions / Warnings:
_ERRsizeChanged = "StableDict changed size during iteration!"
_WRNnoOrderArg  = "StableDict created/updated from unordered mapping object"
_WRNnoOrderKW   = \
              "StableDict created/updated with (unordered!) keyword arguments"


# Note: This class won't work with Python 3000 because the dict
#       protocol will change according to PEP3106. (However porting it
#       to Python 3.X will not be much of an effort.)
class StableDict(dict):
    """Dictionary remembering insertion order

    Order of item assignment is preserved and repeated when iterating
    over an instance.

    CAVEAT: When handing an unordered dict to either the constructor
    or the update() method the resulting order is obviously
    undefined. The same applies when initializing or updating with
    keyword arguments; i.e. keyword argument order is not preserved. A
    runtime warning will be issued in these cases via the
    warnings.warn function."""

    __metaclass__ = copy_baseclass_docs # copy docstrings from base class

    # Python 2.2 does not mangle __* inside __slots__
    __slots__ = ("_StableDict__ksl",) # key sequence list aka __ksl

    # @staticmethod
    def is_ordered(dictInstance):
        """Returns true if argument is known to be ordered."""
        if isinstance(dictInstance, StableDict):
            return True
        try: # len() may raise an exception.
            if len(dictInstance) <= 1:
                return True # A length <= 1 implies ordering.
        except:
            pass
        return False # Assume dictInstance.keys() is _not_ ordered.
    is_ordered = staticmethod(is_ordered)

    def __init__(self, *arg, **kw):
        if arg:
            if len(arg) > 1:
                raise TypeError("at most one argument permitted")
            arg = arg[0]
            if hasattr(arg, "keys"):
                if not self.is_ordered(arg):
                    _warn(_WRNnoOrderArg, RuntimeWarning, stacklevel=2)
                super(StableDict, self).__init__(arg, **kw)
                self.__ksl = arg.keys()
            else: # Must be a sequence of 2-tuples.
                super(StableDict, self).__init__(**kw)
                self.__ksl = []
                for pair in arg:
                    if len(pair) != 2:
                        raise ValueError("not a 2-tuple", pair)
                    self.__setitem__(pair[0], pair[1])
                if kw:
                    ksl = self.__ksl
                    for k in super(StableDict, self).iterkeys():
                        if k not in ksl:
                            ksl.append(k)
                    self.__ksl = ksl
        else: # No positional argument given.
            super(StableDict, self).__init__(**kw)
            self.__ksl = super(StableDict, self).keys()
        if len(kw) > 1:
            # There have been additionial keyword arguments.
            # Since Python passes them in an (unordered) dict
            # we cannot possibly preserve their order (without
            # inspecting the source or byte code of the call).
            _warn(_WRNnoOrderKW, RuntimeWarning, stacklevel=2)

    def update(self, *arg, **kw):
        if arg:
            if len(arg) > 1:
                raise TypeError("at most one non-keyword argument permitted")
            arg = arg[0]
            if hasattr(arg, "keys"):
                if not self.is_ordered(arg):
                    _warn(_WRNnoOrderArg, RuntimeWarning, stacklevel=2)
                super(StableDict, self).update(arg)
                ksl = self.__ksl
                for k in arg.keys():
                    if k not in ksl:
                        ksl.append(k)
                self.__ksl = ksl
            else: # Must be a sequence of 2-tuples.
                 for pair in arg:
                    if len(pair) != 2:
                        raise ValueError("not a 2-tuple", pair)
                    self.__setitem__(pair[0], pair[1])
        if kw:
            # There have been additionial keyword arguments.
            # Since Python passes them in an (unordered) dict
            # we cannot possibly preserve their order (without
            # inspecting the source or byte code of the call).
            if len(kw) > 1:
                _warn(_WRNnoOrderKW, RuntimeWarning, stacklevel=2)
            super(StableDict, self).update(kw)
            ksl = self.__ksl
            for k in kw.iterkeys():
                if k not in ksl:
                    ksl.append(k)
            self.__ksl = ksl

    def __str__(self):
        def _repr(x):
            if x is self:
                return "StableDict({...})" # Avoid unbounded recursion.
            return repr(x)
        return ( "StableDict({" + ", ".join([
                 "%r: %s" % (k, _repr(v)) for k, v in self.iteritems()])
                 + "})" )

    # Try to achieve: self == eval(repr(self))
    def __repr__(self):
        def _repr(x):
            if x is self:
                return "StableDict({...})" # Avoid unbounded recursion.
            return repr(x)
        return ( "StableDict([" + ", ".join([
                 "(%r, %s)" % (k, _repr(v)) for k, v in self.iteritems()])
                 + "])" )

    def __setitem__(self, key, value):
        super(StableDict, self).__setitem__(key, value)
        if key not in self.__ksl:
            self.__ksl.append(key)

    def __delitem__(self, key):
        if key in self.__ksl:
            self.__ksl.remove(key)
        super(StableDict, self).__delitem__(key)

    def __iter__(self):
        length = len(self)
        for key in self.__ksl[:]:
            yield key
        if length != len(self):
            raise RuntimeError(_ERRsizeChanged)

    def keys(self):
        return self.__ksl[:]

    def iterkeys(self):
        return self.__iter__()

    def values(self):
        return [ self[k] for k in self.__ksl ]

    def itervalues(self):
        length = len(self)
        for key in self.__ksl[:]:
            yield self[key]
        if length != len(self):
            raise RuntimeError(_ERRsizeChanged)

    def items(self):
        return [ (k, self[k]) for k in self.__ksl ]

    def iteritems(self):
        length = len(self)
        for key in self.__ksl[:]:
            yield ( key, self[key] )
        if length != len(self):
            raise RuntimeError(_ERRsizeChanged)

    def clear(self):
        super(StableDict, self).clear()
        self.__ksl = []

    def copy(self):
        return StableDict(self)

    def pop(self, k, *default):
        if k in self.__ksl:
            self.__ksl.remove(k)
        return super(StableDict, self).pop(k, *default)

    def popitem(self):
        item = super(StableDict, self).popitem()
        try:
            self.__ksl.remove(item[0])
        except:
            raise ValueError("cannot remove", item, self.__ksl, self)
        return item

# Our metaclass function became a method.  Make it a function again.
StableDict.__metaclass__ = staticmethod(copy_baseclass_docs)


if __name__ == "__main__":
    try:
        import test_stabledict
    except ImportError:
        from test import test_stabledict # Try the "test" package too.
    test_stabledict.test_main()

#EOF#