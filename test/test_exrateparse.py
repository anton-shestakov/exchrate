'''Test exhange rate parsing module'''

from exchrate import exrateparse
import unittest

# exchange rate parser class
exrateparser = exrateparse.ExchangeRateParse

class ExchRateTestKnownValues(unittest.TestCase):        
        
    known_values =  (
         (('NBU-json', ('2007-01-09',), 'USD', 'UAH'), [5.05])          # USD rate
        ,(('NBU-json', ('2007-01-09',), 'EUR', 'UAH'), [6.60742])       # EUR rate
        ,(('NBU-json', ('2007-01-09',), 'RUB', 'UAH'), [0.19179])       # RUB rate
        ,(('NBU-json', ('2000-01-01',), 'RUB', 'UAH'), [])              # empty response
        ,(('NBU-json', ('2015-01-12', '2015-01-15'), 'USD', 'UAH')
            ,[15.757965, 15.767906, 15.77124, 15.776095])               # USD rate date range
        ,(('ECB-Fixer', '2016-11-21', 'EUR', 'PLN'), [4.4307])        # 2nd source value
        ,(('ECB-Fixer', '2016-01-11', 'N/A', 'N/A'), [])              # 2nd source empty
        )

    # daterange represented as follows: 
    # first tuple has parameters to pass to generator function
    # second tuple has the expected result
    known_dateranges = (
         ((('2007-01-09', '2007-01-12'), '%Y-%m-%d'),                           # date range unpacked
             ['2007-01-09', '2007-01-10', '2007-01-11', '2007-01-12'])
         ,((('2005-01-01', '2004-01-01'), '%Y-%m-%d'),                          # 2 dates without unpacking
            ['2005-01-01','2004-01-01'])
        ,((('2005-01-01',), '%Y-%m-%d'),                                        # single date
            ['2005-01-01'])
        ,((None, None, None), [])                                               # no dates
        ,((('2000-01-01', 1), '%Y-%m-%d'),                                      # valid date only
            ['2000-01-01'])
        ,(('2000-01-01',), ['2000-01-01'])                                       # single date string
        )

    def test_exchratedate(self):
        
        for params, exchrate in self.known_values:
            exchratef = exrateparser(*params).get_exch_rate()
            self.assertItemsEqual([t.exrate for t in exchratef], exchrate)
            
    def test_datesplit(self):
        
        for tdaterange in self.known_dateranges:
            gen_daterange = exrateparser.split_dates(*tdaterange[0])
            self.assertItemsEqual(list(gen_daterange), tdaterange[1])


class ExchRateTestException(unittest.TestCase):
    ''' Test how exceptions are being rased '''    
    def test_unknown_source(self):
        self.assertRaises(exrateparse.UnknownSourceError,
                          exrateparser, 'N/A', '2002-01-01', 'USD', 'UAH'
                         )
                         

if __name__ == '__main__':
    unittest.main()

