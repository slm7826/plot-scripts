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

class TestMonthsInSeason(unittest.TestCase):

    def test_months(self):
        self.assertEqual(ut.monthsInSeason('Annual'),
            {1,2,3,4,5,6,7,8,9,10,11,12})
        self.assertEqual(ut.monthsInSeason('ANN'),
            {1,2,3,4,5,6,7,8,9,10,11,12})
        self.assertEqual(ut.monthsInSeason('DJF'),{1,2,12})
        self.assertEqual(ut.monthsInSeason(' d JF   '),{1,2,12})
        self.assertEqual(ut.monthsInSeason('MAM'),{3,4,5})
        self.assertEqual(ut.monthsInSeason('JJA'),{6,7,8})
        self.assertEqual(ut.monthsInSeason('SON'),{9,10,11})
        self.assertEqual(ut.monthsInSeason('JJAS'),{6,7,8,9})
        with self.assertRaises(ValueError):
            ut.monthsInSeason('J')
        with self.assertRaises(ValueError):
            ut.monthsInSeason('ABCD')

if __name__ == '__main__':
    unittest.main()
