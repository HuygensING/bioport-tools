#!/usr/bin/env python

import unittest
import time

from gerbrandyutils import sh, normalize_url
try:
    from gerbrandyutils import optimize
except ImportError:
    optimize = None


class TestCase(unittest.TestCase):

    def test_sh(self):
        stdout = sh("ls")
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
            

def test_suite():
    test_suite = unittest.TestSuite()
    tests = [TestCase]
    for test in tests:
        test_suite.addTest(unittest.makeSuite(test))
    return test_suite

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')    

