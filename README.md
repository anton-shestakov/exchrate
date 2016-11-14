# exchrate
parsing exchange rates from various sources (currently only NationalBankOfUkraine is supported)
written in Python

Database backend required for storing exchange rates:
MSSQL Server

Used libraries:
pymssql --connect to MSSQL server instance
httplib2 --make http requests to exchange rate source URLs
