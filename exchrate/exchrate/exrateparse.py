from datetime import datetime
from collections import namedtuple
import httplib2
import json

sources = {'NBU-json': {'url':'https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?valcode={0}&date={1}&json', 'curfrom':('USD', 'EUR', 'RUB'), 'curto': ('UAH'), 'dateformat': '%Y%m%d', 'datapoints': {'r030','rate','exchangedate'}},
	   'NBU-xml': {'url':'https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?valcode={0}&date={1}', 'curfrom':('USD', 'EUR', 'RUB'), 'curto': ('UAH'), 'dateformat': '%Y%m%d'}}

# output of exchrate functions            
ExchRateTemplate = namedtuple('ExchRateOut', 'curfrom, rate, curto, date')
            
def getExchRate(sourceid, exchratedate, currencyfrom, currencyto):
		
    if sourceid in sources:
        #check date format
        try:
            exchratedt = datetime.strptime(exchratedate, '%Y-%m-%d').strftime(sources[sourceid]['dateformat'])
        except ValueError:
            raise InvalidDateFormatError('Date provided is not formatted properly (yyyy-mm-dd): {0}'.format(exchratedate))  
        
        #get source url from sources dict
        sourceurl = sources[sourceid]['url'].format(currencyfrom, exchratedt)
            
    else:
        raise UnknownSourceError('Unknown source provided: {0}'.format(sourceid))

    #check if currencies provided are valid
    validcurfrom, validcurto = (currencyfrom in sources[sourceid]['curfrom'],
                                currencyto in sources[sourceid]['curto'])

    if not validcurfrom:
        raise InvalidCurrencyError('Currency from provided ({0}) is not supported for selected source'.format(currencyfrom))

    if not validcurto:
        raise InvalidCurrencyError('Currency to provided ({0}) is not supported for selected source'.format(currencyto))

    #if everything's fine then make request and perform parsing based on source
    h = httplib2.Http('.cache')
    response, content = h.request(sourceurl)
    exchrate = json.loads(content.decode('utf-8'))
    #verify if returned response is not empty and contains all data points
    if exchrate and sources[sourceid]['datapoints'] <= set(exchrate[0].keys()):
        exchratef = ExchRateTemplate(exchrate[0]['r030'],
                                     exchrate[0]['rate'],
                                     980,
                                     datetime.strptime(exchrate[0]['exchangedate'], '%d.%m.%Y').date().isoformat()
                                     )
        return exchratef
    else:
        exchratef = ExchRateTemplate(None, 0.0, None, None)
        return exchratef
	
class UnknownSourceError(ValueError):
    pass
	
class InvalidDateFormatError(ValueError):
    pass
	
class InvalidCurrencyError(ValueError):
    pass
