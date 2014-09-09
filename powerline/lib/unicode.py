# vim:fileencoding=utf-8:noet
from __future__ import (unicode_literals, division, absolute_import, print_function)

import sys
import codecs

from locale import getpreferredencoding


try:
	from __builtin__ import unicode
except ImportError:
	unicode = str


try:
	from __builtin__ import unichr
except ImportError:
	unichr = chr


def u(s):
	'''Return unicode instance assuming UTF-8 encoded string.
	'''
	if type(s) is unicode:
		return s
	else:
		return unicode(s, 'utf-8')


if sys.version_info < (3,):
	def tointiter(s):
		'''Convert a byte string to the sequence of integers
		'''
		return (ord(c) for c in s)
else:
	def tointiter(s):
		'''Convert a byte string to the sequence of integers
		'''
		return iter(s)


def powerline_decode_error(e):
	if not isinstance(e, UnicodeDecodeError):
		raise NotImplementedError
	return (''.join((
		'<{0:02X}>'.format(c)
		for c in tointiter(e.object[e.start:e.end])
	)), e.end)


codecs.register_error('powerline_decode_error', powerline_decode_error)


def out_u(s):
	'''Return unicode string suitable for displaying

	Unlike other functions assumes getpreferredencoding() first. Unlike u() does 
	not throw exceptions for invalid unicode strings. Unlike safe_unicode() does 
	throw an exception if object is not a string.
	'''
	if isinstance(s, unicode):
		return s
	elif isinstance(s, bytes):
		return unicode(s, getpreferredencoding(), 'powerline_decode_error')
	else:
		raise TypeError('Expected unicode or bytes instance, got {0}'.format(repr(type(s))))


def safe_unicode(s):
	'''Return unicode instance without raising an exception.

	Order of assumptions:
	* ASCII string or unicode object
	* UTF-8 string
	* Object with __str__() or __repr__() method that returns UTF-8 string or 
	  unicode object (depending on python version)
	* String in locale.getpreferredencoding() encoding
	* If everything failed use safe_unicode on last exception with which 
	  everything failed
	'''
	try:
		try:
			return unicode(s)
		except UnicodeDecodeError:
			try:
				return unicode(s, 'utf-8')
			except TypeError:
				return unicode(str(s), 'utf-8')
			except UnicodeDecodeError:
				return unicode(s, getpreferredencoding())
	except Exception as e:
		return safe_unicode(e)


class FailedUnicode(unicode):
	'''Builtin ``unicode`` (``str`` in python 3) subclass indicating fatal 
	error.

	If your code for some reason wants to determine whether `.render()` method 
	failed it should check returned string for being a FailedUnicode instance. 
	Alternatively you could subclass Powerline and override `.render()` method 
	to do what you like in place of catching the exception and returning 
	FailedUnicode.
	'''
	pass


def string(s):
	if type(s) is not str:
		return s.encode('utf-8')
	else:
		return s
