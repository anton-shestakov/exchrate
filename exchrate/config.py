#!/usr/bin/env/python
'''All settings are instantiated here:
    ISO currency codes dict
    Exchange Rate sources
'''

import urllib2 as http
import xml.etree.ElementTree as xml
from pkg_resources import resource_string


class CurrencyCode():
    '''Class contains methods to get currency codes from ISO 4217 list
    It uses package data file 'data/iso_4217.xml' if filename not provided
    If package data file is missing or empty then it tries to download list
    from website and save it to filename if provided
    '''

    def __init__(self, filename=None):
        '''build dict of ISO currency codes:
            numeric codes are used in database
            literal codes are used in WS calls and responses
        
        Keyword arguments: 
            filename -- path to xml list with currency codes
        '''
        self._ccy_codes = {}
        
        try:
            s = resource_string(__name__, 'data/iso_4217.xml')
        except IOError as err:
            # try to load from website
            url = 'http://www.currency-iso.org/dam/downloads/lists/list_one.xml'
            s = http.urlopen(url).read()
            
            # try to save to file if provided
            if filename is not None:
                with open(filename, 'w') as f:
                    f.write(s)


        if s:
            # build dict using comprehension
            self._ccy_codes = {
                ccy_entry[2].text: {
                    'cntry_name': ccy_entry[0].text,
                    'ccy_name': ccy_entry[1].text,
                    'ccy_code': int(ccy_entry[3].text),
                    'ccy_units': ccy_entry[4].text
                }
                for ccy_entry
                in xml.fromstring(s).iter('CcyNtry')
                if len(ccy_entry) == 5
            }

    def get_ccy_num_code(self, ccy_char_code):
        '''returns currency ISO 4217 numeric code by character code'''
        return self._ccy_codes.get(ccy_char_code, {}).get('ccy_code', -1)
    
    def get_ccy_num_codes(self, ccy_char_codes):
        '''returns dict with char_code : num_code values'''
        return {ccy_char_code: self._ccy_codes[ccy_char_code]['ccy_code']
                for ccy_char_code 
                in ccy_char_codes
                if ccy_char_code in self._ccy_codes.keys()
               }
    
    def get_ccy_codes(self):
        '''returns literal: digit code pairs'''
        return {k: v['ccy_code'] for k, v in self._ccy_codes.iteritems()}

    def get_ccy_info(self, ccy_char_code):
        '''returns all currency info from ISO 4217 table by character code'''
        return self._ccy_codes.get(ccy_char_code, {})


class ExchangeRateSource():
    '''dictionary containing information about supported sources.
    Config fields:
        key -- string key used for lookup in python
        id -- integer identifier. used in database table
        url -- string representation of source url (contains formatting points)
        dateformat -- format of date used for constructing source URL
        datapoints -- set of mandatory field names in JSON response (for
            informational purpose only)
        max_connections -- number of concurrent requests to be made to WS
        field_mapper -- method name for generating output from JSON
    '''
    
    def __init__(self):
        '''initiate exrate source config dict
        rewrite this method if config needs to be moved to file or database'''

        self._exrate_sources = {
                'NBU-json':
                {
                            'id': 1,
                            'url': 'https://bank.gov.ua/NBUStatService/v1/' +
                                'statdirectory/exchange?' +
                                'date={exdate}&valcode={basecur}&json',
                            'dateformat': '%Y%m%d',
                            'datapoints': {'r030', 'rate', 'exchangedate'},
                            'max_connections': 10,
                            'field_mapper': '_map_nbu_gov_ua'
                        },
                'ECB-Fixer':
                {
                            'id': 2,
                            'url': 'https://api.fixer.io/' +
                                '{exdate}?base={basecur}&symbols={localcur}',
                            'dateformat': '%Y-%m-%d',
                            'datapoints': {'base', 'date', 'rates'},
                            'max_connections': 10,
                            'field_mapper': '_map_ecb_fixer'
                        }
        }

    def get_source_config(self, exratesrc):
        '''returns dict containing information for provided source'''

        return self._exrate_sources.get(exratesrc, {})

