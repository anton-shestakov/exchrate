#!/usr/bin/env python
'''sample usage of exchrate package'''

from pprint import pprint

import exchrate  # import package
from exchrate import exrateparse  # import parse module
from exchrate.exrateparse import ExchangeRateParse  # import class directly

# set parameters
exratesrc = 'NBU-json'  # exchange rate source
exratedate = ('2016-12-01', '2016-12-02')  # exchange rate dates
localcur = 'UAH'  # local currency code 1 base = x local
basecur = 'USD'  # base currency code

params = (exratesrc, exratedate, basecur, localcur)


def get_exch_rate_example():
    '''example of getting exchange rate'''
    # initialize objects from different import forms
    e1 = exchrate.ExchangeRateParse(*params)
    e2 = exrateparse.ExchangeRateParse(*params)
    e3 = ExchangeRateParse(*params)

    # assign result of method
    r1 = e1.get_exch_rate()

    # assign instance variable holding last result
    e2.get_exch_rate()
    r2 = e2._last_result

    r3 = e3.get_exch_rate()

    # print results
    print('')
    print('------------ START - get_exch_rate_example ------------')
    print('Import package')
    pprint(r1)
    print('____')
    print('Import parsing module')
    pprint(r2)
    print('____')
    print('Import class directly')
    pprint(r3)
    print('____')
    print('------------ END - get_exch_rate_example ------------')


def use_exch_rate_calc():
    '''example of using exchange rate result in calculation'''

    # sample data for calculation
    price_eur = 150.25  # e.g. we have price in EUR and we want to convert
    # it to PLN for displaying

    # create object
    e = ExchangeRateParse(*params)

    # change object settings
    e.set_source('ECB-Fixer')  # update exchange rate source
    e.exratedate = '2016-12-01'  # update exchange rate date
    e.localcur = 'PLN'  # update local currency (1 EUR = x PLN)
    e.basecur = 'EUR'  # update base currency (to)

    price_pln = price_eur * next(iter(e.get_exch_rate()), None).exrate

    print('')
    print('------------ START - use_exch_rate_calc ------------')
    print('{} EUR = {:.2f} PLN (on {})'.format(price_eur, price_pln, e.exratedate))
    print('------------ END - use_exch_rate_calc ------------')


if __name__ == '__main__':
    get_exch_rate_example()
    use_exch_rate_calc()
