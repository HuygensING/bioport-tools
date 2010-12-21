#!/usr/bin/env python
# coding=utf8

__all__ = [# --- modules
           "compat",
           # --- functions
            "normalize_url", "sh", "hilite", 
           # --- decorators
           "profile", "optimize", "run_in_thread",
           # --- classes           
           "ScriptBase"]

import tempfile
import urllib
import urlparse
import os
import sys
import subprocess
import warnings
import threading
import tarfile
import shutil
import time

try:
    import cProfile
    import pstats
except ImportError:
    cProfile = None  # fix it with "sudo apt-get install python-profiler"

try:
    import psyco
except ImportError:
    psyco = None

import compat  # pushes compat namespace up at this level

if cProfile is not None:

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
if psyco is not None:
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


def hilite(string, ok=True, bold=False):
    """Return an highlighted version of 'string'."""
    attr = []
    if ok:  # green
        attr.append('32')
    elif ok != -1:  # red
        attr.append('31')
    if bold:
        attr.append('1')
    return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)
    
if not sys.stdout.isatty():
    hilite = lambda string, ok=True, bold=False: string


def run_in_thread(fn):
    """Decorator to run a callable in a thread returning the 
    thread instance.
    Note: completely *NOT* thread safe.

    >>> import time
    >>>
    >>> @run_in_thread
    ... def foo():
    ...     time.sleep(100)
    ...     return "done"
    ...
    >>> t = foo()
    >>> t.isAlive()
    True
    >>> t.join()  # waits for thread completion
    >>> t.isAlive()
    False
    """
    def run(*k, **kw):
        t = threading.Thread(target=fn, args=k, kwargs=kw)
        t.start()
        return t
    return run


class ScriptBase(object):
    """A base class which can be used with import scripts.
    It provides facilities to:
    
     - print progress
     - print results (coloured)
     - gracefully add skipped imports during script iteration
     - write files in a safe manner (in case of errors, files are removed
       before exiting the interpreter)
     - compress generated files
    """
    compress_on_exit = True
    remove_output_dir_on_start = True

    def __init__(self):
        self.total = 0
        self._skipped = 0
        self._imported = 0
        self._exited = False
        self._lowercase_names = set()
        self._skip_reasons = []
        self._started = time.time()
        if self.remove_output_dir_on_start:
            self.safe_remove('out')
        if not os.path.isdir('out'):
            os.mkdir('out')       

    def __del__(self):
        if not self._exited:
            self._tear_down()

    def _tear_down(self):
        self._exited = True
        elapsed = "%0.3f" % (time.time() - self._started)
        hl = hilite
        print "total:%s imported:%s skipped=%s in %s secs" \
           % (hl(self.total), hl(self._imported), hl(self._skipped), hl(elapsed))
        if self._skip_reasons:
            print "skip reasons:"
            for x in set(self._skip_reasons):
                print "(%s) %s" % (hl(self._skip_reasons.count(x), 0), x)
        if self.compress_on_exit:
            self._compress_output_files()

    def skip(self, reason=""):
        """Adds a message to the skip queue shown on exit."""
        self._skipped += 1
        if reason:
            self._skip_reasons.append(reason)
            
    def name_already_processed(self, name):
        """Return True if the name of the person has already been
        processed to avoid duplicate persons.
        """
        if not name:
            return True
        lowercased_name = name.lower()
        if lowercased_name in self._lowercase_names:
            return True
        else:
            self._lowercase_names.add(lowercased_name)
            return False
        
    def print_progress(self, index, name=None):
        s = "processing: %s/%s" %(index, self.total)
        if name is not None:
            s += " - " + repr(name)
        print s
       
    def write_file(self, bdes, id):
        #index = str(index).zfill(len(str(self.total)))
        filename = os.path.join('out', "%s.xml" % id)
        try:
            bdes.to_file(filename)
        except:
            self.safe_remove(filename)
            raise
        self._imported += 1
        
        #from lxml import etree
        #namestring = bdes.get_namen()[0].to_string()
        #etree.fromstring(namestring)

    @staticmethod
    def safe_remove(self, path):
        if os.path.isdir(path)
            shutil.rmtree(path, ignore_errors=True)
        else:
            try:
                os.remove(path)
            except OSError:
                pass
    @staticmethod
    def _compress_output_files():
        tar = tarfile.open("out.tar.gz", "w:gz")
        for name in os.listdir("out"):
            tar.add("out/" + name, arcname=name)
        tar.close()


