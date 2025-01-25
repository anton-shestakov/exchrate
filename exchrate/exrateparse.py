'''
Module has class for parsing currencies exchange rate into python list
of named tuples. Currently following process is implemented:
    1. Create instance of ExchangeRateParse object with arguments needed
    2. Exchange rate source must have config data in config.py module.
    Currently 2 sources are supported: National Bank Of Ukraine and European
    Central Bank.
    3. Adding new exchange rate sources that do not need authentication
    requires:
        - entry in config.ExchangeRateSource._exrate_sources (similar to
        existing)
        - mapping function in ExchangeRateParse which maps output from API to
        Python named tuple
    4. If exchange rate source needs authentication than more changes to be
    made:
        - modifying _get_api_responses method to allow passing authentication
        data or object

    Class approach was selected for several reasons:
    - you can create multiple instances for different sources and set them
        as daemons for checking new data every day (since not all APIs provide
        update notify mechanism)
    - you can create multiple instances with different set of parameters to
        run them concurrently (for example, NBU does not support multi currency
        request for multiple dates, which can be bypassed by spawning multiple
        ExchangeRateParse objects)
'''

import asyncio
import json
from collections import namedtuple
from datetime import datetime, timedelta

import httpx

from . import config


class ExchangeRateParse:
    '''Exchange rate parsing class

    Constructor
    ExchangeRateParse(exratesrc, exratedate, localcur, basecur, daysadd, df)

    exratesrc -- exchange rate source code (config is read from config module)
    exratedate -- sequence of dates to parse rate for
    basecur -- ISO 4217 literal base currency code
    localcur -- ISO 4217 literal local currency code (1 basecur = x localcur)
    daysadd -- optional parameter used for unpacking dates sequence
    df -- dateformat of dates in exratedate

    For getting exchange rate for specified params use method:
        get_exch_rate()

    Last result of get_exch_rate() is stored in following attribute:
        _last_result

    For changing exchange rate source use method:
        set_source(exratesrc)

    For changing other settings use attributes:
        exratedate -- exchange dates
        localcur -- local currency
        basecur -- base currency
        daysadd -- days to be added to next date when unpacking dates
        df -- daterformat of dates in exratedate
    '''

    # result output template
    EXRATE_TEMPLATE = namedtuple('Exrate', 'sourceid,exdate,localcur,basecur,exrate')

    def __init__(
        self, exratesrc, exratedate, basecur, localcur, daysadd=1, df='%Y-%m-%d'
    ):
        self.set_source(exratesrc)
        self.exratedate = exratedate
        self.localcur = localcur
        self.basecur = basecur
        self.daysadd = daysadd
        self.df = df
        # read ISO 4217 currency codes mapping
        self._ccy_codes = config.CurrencyCode().get_ccy_codes()
        self._last_result = []

    def _get_api_responses(self, urls, max_connections=10):
        return asyncio.get_event_loop().run_until_complete(
            get_api_responses(urls, max_connections)
        )

    def set_source(self, exratesrc):
        '''update exchange rate source

        Positional arguments:
            exratesrc -- source code
        '''

        # read source config
        tmp = config.ExchangeRateSource().get_source_config(exratesrc)
        if not tmp:
            raise UnknownSourceError(
                'Unsupported source provided: {}'.format(exratesrc)
            )
        self._source_config, self.exratesrc = (tmp, exratesrc)

    def get_exch_rate(self):
        '''Get currency exchange rate from selected source, date(s)
        Returns: list of namedtuple instances with exchange rates

        namedtuple fields:
            sourceid -- internal id of exchange rate source supplied
            exdate -- date on which exchange rate has been set
            curfrom -- base currency 3 digit ISO 4217 code
            curto -- local currency 3 digit ISO 4217 code
            exrate -- exchange rate between base and local currency
        '''

        # initiate dates generator
        dates_gen = self.split_dates(
            self.exratedate, self.df, self._source_config['dateformat'], self.daysadd
        )

        # build api url list for dates provided
        urls = (
            self._source_config['url'].format(
                exdate=d, localcur=self.localcur, basecur=self.basecur
            )
            for d in dates_gen
        )

        # collect responses
        responses = self._get_api_responses(
            urls, self._source_config['max_connections']
        )

        # map responses and return result
        self._last_result = self._map_response(responses)

        return self._last_result

    def _map_response(self, response):
        '''call method according to exchange source'''

        def map_not_found():
            raise ValueError('map function in config is not found')

        return getattr(self, self._source_config['field_mapper'], map_not_found)(
            response
        )

    def _map_nbu_gov_ua(self, response):
        '''Maps json from NBU.gov.ua exchange rate source
        Returns: list of OrderedDict instances with data

        Positional arguments (expected):
            responses -- response from NBU WS
        '''
        _source_id = self._source_config['id']

        def json_object_hook(r):
            '''json object hook for mapping NBU data'''

            return self.EXRATE_TEMPLATE(
                _source_id,
                datetime.strptime(r['exchangedate'], '%d.%m.%Y').date().isoformat(),
                980,
                r['r030'],
                r['rate'],
            )

        return [
            exrate
            for _ in response
            for exrate in json.loads(_, object_hook=json_object_hook)
            if exrate
        ]

    def _map_ecb_fixer(self, response):
        '''Maps json from fixer.io exchange rate source
        Returns: list of OrderedDict instances with data

        Positional arguments (expected):
            responses -- response from ECB WS
        '''

        _source_id, _ccy_codes = (self._source_config['id'], self._ccy_codes)

        def json_object_hook(r):
            '''json object hook for mapping ECB Fixer data'''

            rates = r.get('rates', None)
            # Apply transform only if json is full
            if rates is not None:
                return [
                    self.EXRATE_TEMPLATE(
                        _source_id,
                        datetime.strptime(r['date'], '%Y-%m-%d').date().isoformat(),
                        _ccy_codes[cur],
                        _ccy_codes[r['base']],
                        rate,
                    )
                    for cur, rate in rates.iteritems()
                ]
            else:
                return r

        return [
            exrate
            for _ in response
            for exrate in json.loads(_, object_hook=json_object_hook)
            if exrate
        ]

    @staticmethod
    def split_dates(dates, df_in='%Y-%m-%d', df_out='%Y-%m-%d', daysadd=1):
        '''Generator function that provides valid dates from input

        Positional arguments:
        dates -- dates to be returned

        Keyword arguments:
        df_in -- format of input date strings. Must be valid dateformat string
        df_out -- format of output date strings. Must be valid dateformat string
        daysadd -- number of days to be added to the next date when unpacking period.
            Has effect only in case 1 described below. If not valid unpacking wont work

        Return values depend on input arguments:
        case1: if first 2 dates in sequence are valid and date1 < date2 then
            all dates between date1 and date2
        case2: all valid unique dates from sequence will be returned
        '''
        # convert to list if single date is provided
        dates = [dates] if isinstance(dates, str) else dates

        # logic case 1
        try:
            sd, ed = (datetime.strptime(d, df_in).date() for d in dates[0:2])
            td = timedelta(daysadd)
            if ed < sd:
                raise ValueError
        except (ValueError, TypeError):  # skip to logic case 2
            pass
        else:
            while ed >= sd:
                yield sd.strftime(df_out)
                sd += td
            return  # StopIteration

        # logic case 2
        dates_processed = set()
        try:
            for d in dates:
                if d not in dates_processed:
                    yield datetime.strptime(d, df_in).strftime(df_out)
                    dates_processed.add(d)
        except (ValueError, TypeError):
            pass


class UnknownSourceError(ValueError):
    '''Exception raised when unknown source is passed'''

    pass


async def _get_api_response(url, client, sem):
    '''generates requests and make calls to API

    I/O function. Can be updated to use different http client

    Return type:
        list with texts of responses
    '''

    async with sem:
        return await client.get(url)


async def get_api_responses(urls, max_connections=10):
    sem = asyncio.Semaphore(max_connections)
    async with httpx.AsyncClient(timeout=10) as client:
        futures = [_get_api_response(url, client, sem) for url in urls]
        responses = await asyncio.gather(*futures)
    return [response.text for response in responses if response.is_success]
