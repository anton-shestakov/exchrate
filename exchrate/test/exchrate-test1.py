import os
import sys
sys.path.insert(1, os.path.abspath('..'))

from exchrate import exrateparse, exratemain
from lxml import etree
import xmltodict
import unittest


class ExchRateTestKnownValues(unittest.TestCase):        
        
    known_values =  (
         (('NBU-json', ('2007-01-09',), 'USD', 'UAH'), [5.05])          # USD rate
        ,(('NBU-json', ('2007-01-09',), 'EUR', 'UAH'), [6.60742])       # EUR rate
        ,(('NBU-json', ('2007-01-09',), 'RUB', 'UAH'), [0.19179])       # RUB rate
        ,(('NBU-json', ('2000-01-01',), 'RUB', 'UAH'), [])              # empty response
        ,(('NBU-json', ('2015-01-12', '2015-01-15'), 'USD', 'UAH')
            ,[15.757965, 15.767906, 15.77124, 15.776095])               # USD rate date range
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
        , ((None, None, None), [])                                              # no dates
        ,((('2000-01-01', 1), '%Y-%m-%d'),                                      # valid date only
            ['2000-01-01'])
        )

    # xml list with exchange rates
    known_values_xml = (
            (
                ('NBU-json', ('2015-01-12', '2015-01-13'), 'USD', 'UAH'),
                '''
                <exchRates>
                <exchRate>
                    <exchDate>2015-01-12</exchDate>
                    <exchSource>1</exchSource>
                    <fromCurr>840</fromCurr>
                    <toCurr>980</toCurr>
                    <exchRate>15.757965</exchRate>
                </exchRate>
                <exchRate>
                    <exchDate>2015-01-13</exchDate>
                    <exchSource>1</exchSource>
                    <fromCurr>840</fromCurr>
                    <toCurr>980</toCurr>
                    <exchRate>15.767906</exchRate>
                </exchRate>	
                </exchRates>
                '''
                )
            ,
            )

    
    def test_exchratedate(self):
        
        for params, exchrate in self.known_values:
            exchratef = exrateparse.getExchRate(*params)
            self.assertItemsEqual([t.exrate for t in exchratef], exchrate)
            
    def test_datesplit(self):
        
        for tdaterange in self.known_dateranges:
            gen_daterange = exrateparse.splitDates(*tdaterange[0])
            self.assertItemsEqual(list(gen_daterange), tdaterange[1])


    def test_exchangerate_xml(self):

        for params, result in self.known_values_xml:
            known_xml = xmltodict.parse(result.strip(), dict_constructor=dict)
            produced_xml = xmltodict.parse(
                    ''.join(exratemain.getExchRateXml(
                        exrateparse.getExchRate(*params))).strip()
                    , dict_constructor=dict
                    )
            self.assertEqual(known_xml, produced_xml)
            

                
class ExchRateTestException(unittest.TestCase):
    ''' Test how exceptions are being rased '''    
    def test_unknown_source(self):
        self.assertRaises(exrateparse.UnknownSourceError, exrateparse.getExchRate, 'N/A', '2002-01-01', 'USD', 'UAH')
    
#    def test_invalid_date(self):
#        self.assertRaises(exrateparse.InvalidDateFormatError, exrateparse.getExchRate, 'NBU-json', '1', 'USD', 'UAH')
    
    def test_invalid_currency(self):
        self.assertRaises(exrateparse.InvalidCurrencyError, exrateparse.getExchRate, 'NBU-json', '2002-01-01', 'N/A', 'UAH')

#    def test_split_empty_range(self):
#        f = exrateparse.splitDateRange(None, None, None)
#        self.assertRaises(StopIteration, next, f)
    
if __name__ == '__main__':
    unittest.main()
    

    
