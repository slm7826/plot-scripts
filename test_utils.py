import unittest
import numpy  as np
import xarray as xr
import utils  as ut

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
            [1,2,3,4,5,6,7,8,9,10,11,12])
        self.assertEqual(ut.monthsInSeason('ANN'),
            [1,2,3,4,5,6,7,8,9,10,11,12])
        self.assertEqual(ut.monthsInSeason('DJF'),[12,1,2])
        self.assertEqual(ut.monthsInSeason(' d JF   '),[12,1,2])
        self.assertEqual(ut.monthsInSeason('MAM'),[3,4,5])
        self.assertEqual(ut.monthsInSeason('JJA'),[6,7,8])
        self.assertEqual(ut.monthsInSeason('SON'),[9,10,11])
        self.assertEqual(ut.monthsInSeason('JJAS'),[6,7,8,9])

        self.assertEqual(ut.monthsInSeason('Jul'),[7])
        self.assertEqual(ut.monthsInSeason('July'),[7])

        self.assertEqual(ut.monthsInSeason('DEC'),[12])
        self.assertEqual(ut.monthsInSeason('December'),[12])

        with self.assertRaises(ValueError):
            ut.monthsInSeason('J')
        with self.assertRaises(ValueError):
            ut.monthsInSeason('ABCD')

class TestGetBounds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temp=[1.0, 1.0, 2.0, 2.0]

        # create test data set without bounds attribute
        cls.ds1 = xr.Dataset(
            data_vars=dict(
                temp = (['lon'],temp,{'units':'deg_C'})
            ),
            coords = dict(
                lon=(["lon"], [0.5,1.5,2.5,3.5])
            ),
            attrs = {'title': 'Test data set'}
        )

        # create test data set with bounds attribute
        bnds=[[0.1,1.0],[1.0,2.1],[2.0,3.0],[3.0,4.5]]
        cls.ds2 = xr.Dataset(
            data_vars = dict(
                temp     = (['lon'],temp,{'units':'deg_C'}),
                lon_bnds = (['lon','bnds'],bnds)
            ),
            coords = dict(
                lon=(["lon"], [0.5,1.5,2.5,3.5],{'bounds':'lon_bnds'})
            ),
            attrs = {'title': 'Test data set'}
        )
        # self.ds2.info()


    def test_noBounds(self):
        ''' Test coordinate bounds without "bnds" attribute'''
        bounds = ut.getBounds(self.ds1,'lon').values
        np.testing.assert_array_equal(bounds[:,0],[0.0,1.0,2.0,3.0],verbose=True)
        np.testing.assert_array_equal(bounds[:,1],[1.0,2.0,3.0,4.0],verbose=True)

    def test_withBounds(self):
        ''' Test coordinate bounds with "bnds" attribute'''
        bounds = ut.getBounds(self.ds2,'lon').values
        np.testing.assert_array_equal(bounds[:,0],[0.1,1.0,2.0,3.0],verbose=True)
        np.testing.assert_array_equal(bounds[:,1],[1.0,2.1,3.0,4.5],verbose=True)

    def test_errors(self):
        ''' Test error conditions '''
        with self.assertRaises(KeyError):
            bounds = ut.getBounds(self.ds1,'lat').values

if __name__ == '__main__':
    unittest.main()
