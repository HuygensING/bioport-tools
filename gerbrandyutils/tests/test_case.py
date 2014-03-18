##########################################################################
# Copyright (C) 2009 - 2014 Huygens ING & Gebrandy S.R.L.
# 
# This file is part of bioport.
# 
# bioport is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/gpl-3.0.html>.
##########################################################################

#!/usr/bin/env python

import unittest
import time
import threading

from gerbrandyutils import sh, normalize_url, hilite, run_in_thread
from gerbrandyutils.compat import all, any, namedtuple
try:
    from gerbrandyutils import optimize
except ImportError:
    optimize = None


class TestCase(unittest.TestCase):

    def test_sh(self):
        stdout = sh("ls")
        self.assertTrue(stdout)
        self.assertRaises(RuntimeError, sh, 'badcmd')
          
    def test_normalize_url(self):
        nu = normalize_url
        self.assertEqual(nu('http://google.it'), 'http://google.it')
        self.assertEqual(nu('http://google.it?a=1&b=2'), 'http://google.it?a=1&b=2')

    if optimize is not None:
        def test_optimize(self):

            def foo():
                L = []
                for i in range(100):
                    L.append(i)
            t1 = time.time()
            for x in range(10000):
                foo()
            normal_time = time.time() - t1

            @optimize
            def foo():
                L = []
                for i in range(100):
                    L.append(i)
            t1 = time.time()
            for x in range(10000):
                foo()
            optimized_time = time.time() - t1
            self.assertTrue(optimized_time < normal_time)
            
    def test_hilite(self):
        hilite("foo", ok=1)
        hilite("foo", ok=1, bold=1)
        hilite("foo", ok=0)
        hilite("foo", ok=0, bold=1)
        
    def test_compat_all(self):
        self.assertTrue(all([1, 1, 1, 1]))
        self.assertFalse(all([1, 1, 1, 0]))

    def test_compat_any(self):
        self.assertTrue(any([1, 1, 1, 1]))
        self.assertTrue(any([1, 1, 1, 0]))
        self.assertFalse(all([0, 0, 0, 0]))
        
    def test_compat_namedtuple(self):
        init = namedtuple('meminfo', 'rss vms')
        nt = init(1, 2)
        self.assertEqual(nt[0], nt.rss)
        self.assertEqual(nt[1], nt.vms)
        self.assertEqual(str(nt), "meminfo(rss=1, vms=2)")
        
    def test_run_in_thread(self):
        flag = []
        
        @run_in_thread
        def foo():
            time.sleep(0.1)
            flag.append(None)
           
        t = foo()
        self.assertTrue(isinstance, threading.Thread)
        self.assertTrue(t.isAlive)
        t.join()
        self.assertFalse(t.isAlive())
        self.assertEqual(flag, [None])


def test_suite():
    test_suite = unittest.TestSuite()
    tests = [TestCase]
    for test in tests:
        test_suite.addTest(unittest.makeSuite(test))
    return test_suite

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')    

