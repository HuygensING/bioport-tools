#!/usr/bin/env python

import unittest

from gerbrandyutils import sh, normalize_url


class TestCase(unittest.TestCase):

    def test_sh(self):
        stdout = sh("ls")
        self.assertRaises(RuntimeError, sh, 'badcmd')
          
    def test_normalize_url(self):
        nu = normalize_url
        self.assertEqual(nu('http://google.it'), 'http://google.it')
        self.assertEqual(nu('http://google.it?a=1&b=2'), 'http://google.it?a=1&b=2')
    
        
def test_suite():
    test_suite = unittest.TestSuite()
    tests = [TestCase]
    for test in tests:
        test_suite.addTest(unittest.makeSuite(test))
    return test_suite

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')    


