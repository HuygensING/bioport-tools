#!/usr/bin/env python
# coding=utf8

import cProfile
import tempfile
import urllib
import urlparse
import os
import subprocess
import warnings
try:
    import pstats
except ImportError:
    pstats = None  # might be missing on some Linuxes

import psyco


if pstats is not None:

    def profile(sort='cumulative', lines=50, strip_dirs=False):
        """A decorator which profiles a callable.
        Example usage:

        >>> @profile
        ... def factorial(n):
        ...     n = abs(int(n))
        ...     if n < 1: 
        ...             n = 1
        ...     x = 1
        ...     for i in range(1, n + 1):
        ...             x = i * x
        ...     return x
        ... 
        >>> factorial(5)
        Thu Jul 15 20:58:21 2010    /tmp/tmpIDejr5

                 4 function calls in 0.000 CPU seconds

           Ordered by: internal time, call count

           ncalls  tottime  percall  cumtime  percall filename:lineno(function)
                1    0.000    0.000    0.000    0.000 profiler.py:120(factorial)
                1    0.000    0.000    0.000    0.000 {range}
                1    0.000    0.000    0.000    0.000 {abs}
                1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}

        120
        >>>
        """
        def outer(fun):
            def inner(*args, **kwargs):
                file = tempfile.NamedTemporaryFile()
                prof = cProfile.Profile()
                try:
                    ret = prof.runcall(fun, *args, **kwargs)
                except:
                    file.close()
                    raise

                prof.dump_stats(file.name)
                stats = pstats.Stats(file.name)
                if strip_dirs:
                    stats.strip_dirs()
                if isinstance(sort, (tuple, list)):
                    stats.sort_stats(*sort)
                else:
                    stats.sort_stats(sort)
                stats.print_stats(lines)

                file.close()
                return ret
            return inner

        # in case this is defined as "@profile" instead of "@profile()"
        if hasattr(sort, '__call__'):
            fun = sort
            sort = 'cumulative'
            outer = outer(fun)
        return outer


# TODO - can be extended to support python 2.6 class decorators
def optimize(fun):
    """Decorator to optimize a callable by using psyco.

    >>> @optimize
    ... def sum(a, b):
    ...     return a + b
    ...
    >>> sum(1, 2)
    3
    >>>
    """   
    def outer(fun):
        def inner(*args, **kwargs):
            psyco.bind(fun)
            return fun(*args, **kwargs)
        return inner
    return outer(fun)


def normalize_url(s, charset='utf-8'):
    """Sometimes you get an URL by a user that just isn't a real
    URL because it contains unsafe characters like ' ' and so on.  This
    function can fix some of the problems in a similar way browsers
    handle data entered by the user:

    >>> normalize_url(u'http://de.wikipedia.org/wiki/Elf (Begriffsklärung)')
    'http://de.wikipedia.org/wiki/Elf%20%28Begriffskl%C3%A4rung%29'

    :param charset: The target charset for the URL if the url was
                    given as unicode string.
    """
    if isinstance(s, unicode):
        s = s.encode(charset, 'ignore')
    scheme, netloc, path, qs, anchor = urlparse.urlsplit(s)
    path = urllib.quote(path, '/%')
    qs = urllib.quote_plus(qs, ':&=')
    return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))


def sh(cmdline):
    """run cmd in a subprocess and return its output.
    raises RuntimeError on error.
    """
    p = subprocess.Popen(cmdline, shell=1, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        raise RuntimeError(stderr)
    if stderr:
        warnings.warn(stderr, RuntimeWarning)
    return stdout

