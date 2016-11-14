import os
import sys
sys.path.insert(1, os.path.abspath('..'))

from exchrate import exrateparse as exchratemod, exratemain as exchratemain
from lxml import etree
import xmltodict
import unittest


class ExchRateTestKnownValues(unittest.TestCase):
        ''' Test how known values are being parsed from WS '''

        known_values =  (
             ('NBU-json', '2007-01-09', 'USD', 'UAH', 5.05)          # USD rate
            ,('NBU-json', '2007-01-09', 'EUR', 'UAH', 6.60742)       # EUR rate
            ,('NBU-json', '2007-01-09', 'RUB', 'UAH', 0.19179)       # RUB rate
            ,('NBU-json', '2000-01-01', 'RUB', 'UAH', 0.0)           # empty response
            )

        # daterange represented as follows: first tuple has parameters to pass to generator function, second tuple has the expected result
        known_dateranges = (
             (('2007-01-09', '2007-01-12', 1), ('2007-01-09', '2007-01-10', '2007-01-11', '2007-01-12'))    # should return all dates in range between start and end
            ,(('2005-01-01', '2004-01-01', 1), ('2005-01-01',))                                             # should return start date only
            #, ((None, None, None), (None,))                                                                # should return None
            )

        # daterange values represent tuple of following: tuple with parameters to pass to function and list with expected result
        known_values_range = (
            (('NBU-json', '2015-01-12', '2015-01-15', 'USD', 'UAH')
             , [(840, '2015-01-12', 15.757965), (840, '2015-01-13', 15.767906)
                , (840, '2015-01-14', 15.77124), (840, '2015-01-15', 15.776095)]
             )
            ,
            )

        # xml list with exchange rates
        known_values_xml = (
                (
                    ('NBU-json', '2015-01-12', '2015-01-13', 'USD', 'UAH'),
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
            
            for sourceid, exchratedate, currencyfrom, currencyto, exchrate in self.known_values:
                exchratef = exchratemod.getExchRate(sourceid,
                                                    exchratedate,
                                                    currencyfrom,
                                                    currencyto)
                print('Date: {0}, currency: {1}, rate: {2}'.format(exchratef.date,
                                                                   exchratef.curfrom,
                                                                   exchratef.rate))
                self.assertEqual(exchratef.rate, exchrate)
                
        def test_exchratedatesplit(self):
            
            for tdaterange in self.known_dateranges:
                gen_daterange = exchratemain.splitDateRange(*tdaterange[0])
                for tdate in tdaterange[1]:
                    gen_tdate = next(gen_daterange)
                    self.assertEqual(gen_tdate, tdate)

        def test_exchraterange(self):

            for params, results in self.known_values_range:
                result = exchratemain.getExchRateRange(*params)
                i = 0
                for known_exrate in results:
                    self.assertEqual(result[i].curfrom, known_exrate[0])
                    self.assertEqual(result[i].date, known_exrate[1])
                    self.assertEqual(result[i].rate, known_exrate[2])
                    i += 1

        def test_exchangerate_xml(self):

            for params, result in self.known_values_xml:
                known_xml = xmltodict.parse(result.strip(), dict_constructor=dict)
                produced_xml = xmltodict.parse(exchratemain.getExchRateAsXml(*params).strip(), dict_constructor=dict)
                self.assertEqual(known_xml, produced_xml)
                

                
class ExchRateTestException(unittest.TestCase):
    ''' Test how exceptions are being rased '''    
    def test_unknown_source(self):
        self.assertRaises(exchratemod.UnknownSourceError, exchratemod.getExchRate, 'N/A', '2002-01-01', 'USD', 'UAH')
    
    def test_invalid_date(self):
        self.assertRaises(exchratemod.InvalidDateFormatError, exchratemod.getExchRate, 'NBU-json', '1', 'USD', 'UAH')
    
    def test_invalid_currency(self):
        self.assertRaises(exchratemod.InvalidCurrencyError, exchratemod.getExchRate, 'NBU-json', '2002-01-01', 'N/A', 'UAH')

    def test_split_empty_range(self):
        f = exchratemain.splitDateRange(None, None, None)
        self.assertRaises(StopIteration, next, f)
    
if __name__ == '__main__':
    unittest.main()
    

    
