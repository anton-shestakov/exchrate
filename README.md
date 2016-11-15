# exchrate
parsing exchange rates from various sources (currently only National Bank Of Ukraine (bank.gov.ua) is supported)
written in Python. tested on python 2.7.12.

Database backend required for storing exchange rates:
MSSQL Server

Used libraries:
pymssql -- connect to MSSQL server instance
grequests -- make http requests to exchange rate source URLs
