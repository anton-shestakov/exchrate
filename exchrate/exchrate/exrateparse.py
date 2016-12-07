from datetime import datetime, timedelta
from collections import namedtuple
import grequests

# dictionary containing information about supported sources 
# *** To be moved to config file/database later ***
EXRATE_SOURCES = {
        'NBU-json': 
        {
            'id': 1,
            'url': 'https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?date={0}&valcode={1}&json', 
            'curfrom': ('USD', 'EUR', 'RUB'), 
            'curto': ('UAH'), 
            'dateformat': '%Y%m%d', 
            'datapoints': {'r030','rate','exchangedate'},
            'max_connections': 10
        }
        }

# output template of exchrate functions
EXRATE_TEMPLATE = namedtuple('ExchRateOut', 'sourceid, exdate, curfrom, curto, exrate')

def splitDates(dates, df_in = '%Y-%m-%d', df_out='%Y-%m-%d', daysadd = 1):
    '''Generator function that provides dates in order from input sequence

    Positional arguments:
    dates -- sequence which contains dates as strings

    Keyword arguments:
    df_in -- format of input date strings. Must be valid dateformat string
    df_out -- format of output date strings. Must be valid dateformat string
    daysadd -- number of days to be added to the next date when unpacking period.
        Has effect only in logic case 1 described below. If not valid unpacking wont work

    Logic cases:
    case1: if sequence has 2 valid dates and date1 < date2 then
        all %date% values such as date1<=%date%<=date2 will be returned
    case2: in all other cases all valid dates from sequence will be returned
    '''
    # logic case 1
    try:
        sd, ed = [datetime.strptime(d, df_in).date() for d in dates[0:2]]
        td = timedelta(daysadd)
        if ed < sd: raise ValueError    
    except (ValueError, TypeError):     # skip to logic case 2
        pass
    else:
        while ed >= sd:
            yield sd.strftime(df_out)
            sd += td
        return # StopIteration
    
    # logic case 2
    try:
        for d in dates:
            yield datetime.strptime(d, df_in).strftime(df_out)
    except (ValueError, TypeError):
        pass


def getExchRate(exratesrc, exratedate, currencyfrom, currencyto, 
        exratedaysadd=1, exratedateformat='%Y-%m-%d', debug=False,
        debug_filename=''):
    '''Get exchange rate from passed source, date(s) and currencies provided
    Returns: list of named tuples with exchange rates
    
    Elements of individual named tuple:
    sourceid -- internal id of exchange rate source supplied
    exdate -- date on which exchange rate has been set
    curfrom -- base currency code
    curto -- local currency code
    exrate -- exchange rate between base and local currency
    
    Positional arguments:
    exratesrc -- code of exchange rate source to be used for parsing
    exratedate -- tuple of dates to be parsed. Passed to generator function
        splitDates which defines logic for this parameter
    currencyfrom -- base currency code
    currencyto -- local currency code

    Keywords arguments:
    exratedaysadd -- number of days between exchange dates in a period
    exratedateformat -- format of exchange date strings provided
    '''
    try:
        source_config = EXRATE_SOURCES[exratesrc]
    except KeyError:
        raise UnknownSourceError('Unknown source provided: {0}'.format(exratesrc))
    else:
        # verify currencies
        msg = [[], []]
        if not currencyfrom in source_config['curfrom']:
            msg[0].append('Base')
            msg[1].append(currencyfrom)

        if not currencyto in source_config['curto']:
            msg[0].append('Local')
            msg[1].append(currencyto)

        if msg[0]:
            raise InvalidCurrencyError('{0} currency provided {1} not valid ("{2}")'.format(
                ', '.join(msg[0]),
                'is' if len(msg[0]) == 1 else 'are',
                '","'.join(msg[1])
                )
                )

        # perform data parsing if everything is correct
        dates_gen = splitDates(
            exratedate, 
            exratedateformat,
            source_config['dateformat'],
            exratedaysadd
            )

        output = []
        # prepare list of requests and execute them
        req_list = (grequests.get(source_config['url'].format(d, currencyfrom)) for d in dates_gen)
        resp_list = grequests.map(req_list, size=source_config['max_connections'])
        
        if debug:
            with open(debug_filename, 'w') as f:
                f.write('\n'.join((
                    str(t.status_code) 
                    + ':' 
                    + t.text.encode('utf-8') 
                    for t in resp_list)
                    )
                    )

        # collect good responses
        resp_good = (t.json() for t in resp_list if t.ok)
        
        for exrate in (x[0] for x in resp_good if x and source_config['datapoints'] <= set(x[0].keys())):
            output.append(
                    EXRATE_TEMPLATE(
                        source_config['id'],
                        datetime.strptime(exrate['exchangedate'], '%d.%m.%Y').date().isoformat(),
                        exrate['r030'],
                        980,
                        exrate['rate']
                        )
                    )

        return output


class UnknownSourceError(ValueError):
    pass
	
class InvalidDateFormatError(ValueError):
    pass
	
class InvalidCurrencyError(ValueError):
    pass


