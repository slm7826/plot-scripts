import unittest
import utils as ut

class TestParseLevels(unittest.TestCase):

#     def test_empty_input(self):
#         self.assertEqual(ut.parseLevels(''), None)

    def test_levels(self):
        self.assertEqual(ut.parseLevels('0, 0.5, 1'),[0.0,0.5,1.0])
        self.assertEqual(ut.parseLevels('0:1.5:0.5'),[0.0,0.5,1.0,1.5])
        self.assertEqual(ut.parseLevels('0:1:0.5, 0.1'),[0.0,0.1,0.5,1.0])
        self.assertEqual(ut.parseLevels('-1:1:.5,0.1,del(0)'),[-1,-0.5,0.1,0.5,1.0])

    def test_level_errors(self):
        with self.assertRaises(ValueError):
            ut.parseLevels('0:1')
        with self.assertRaises(ValueError):
            ut.parseLevels('0:1:0.5:2')
        with self.assertRaises(ValueError):
            ut.parseLevels('1:0.5:0.1')
        with self.assertRaises(ValueError):
            ut.parseLevels('0.5:1:-0.1')
        with self.assertRaises(ValueError):
            ut.parseLevels('0.5')

class TestParseRange(unittest.TestCase):

    def test_range(self):
        self.assertEqual(ut.parseRange('1980:2000'),(1980,2000))
        self.assertEqual(ut.parseRange('2000:1980'),(1980,2000))

    def test_range_errors(self):
        with self.assertRaises(ValueError):
            ut.parseRange('1980')
        with self.assertRaises(ValueError):
            ut.parseRange('1980:2000:2100')

if __name__ == '__main__':
    unittest.main()
