from lxml import etree
from copy import deepcopy
from . import exrateparse, exratedb

# *** To be moved to config file or environmental settings ***
# *** Not to be stored in plain text ***
DB_SERVER = 'enter_server_path'
DB_USER = 'enter_username'
DB_PASSWORD = 'enter_password'
DB_DATABASE = 'enter_database_name'

def getExchRateXml(exrate, chunksize=8000):
    '''returns xml generator with each element size <= chunksize
    
    Positional arguments:
    exrate -- list of exchange rates with named tuples
    
    Keyword arguments:
    chunksize -- size in bytes of xml fragment to be returned.
        Default is 8000 to comply with mssql driver text size limit
    '''

    if exrate:
        # create xml elements for output
        exRates = etree.Element('exchRates')
        exRate = etree.Element('exchRate')
        etree.SubElement(exRate, 'exchDate')
        etree.SubElement(exRate, 'exchSource')
        etree.SubElement(exRate, 'fromCurr')
        etree.SubElement(exRate, 'toCurr')
        etree.SubElement(exRate, 'exchRate')
        exRateList = []
        # populate xml elements with returned data
        for sourceId, exchDate, fromCurr, toCurr, exchRate in exrate:
            exRate[0].text = exchDate
            exRate[1].text = str(sourceId)
            exRate[2].text = str(fromCurr)
            exRate[3].text = str(toCurr)
            exRate[4].text = str(exchRate)
            exRateList.append(deepcopy(exRate))
        # populate xml root element with generated elements
        buffer_add = len(etree.tostring(exRates).decode())
        buffer_size = buffer_add

        for xmlExrate in exRateList:
            buffer_size = buffer_size + len(etree.tostring(xmlExrate).decode()) 
            if buffer_size < chunksize:
                exRates.append(xmlExrate)
            else:
                # return current list of exchange rates
                yield etree.tostring(exRates).decode() 
                # reset buffer and insert current element
                exRates.clear()
                exRates.append(xmlExrate)
                buffer_size = buffer_add + len(etree.tostring(xmlExrate).decode()) 

        # final result
        yield etree.tostring(exRates).decode() 


def loadExchRate(sourceid, startdate, enddate, currencyfrom, currencyto,
        overwrite = 'N', debug = False, debug_filename = ''):
    
    exrates = exrateparse.getExchRate(sourceid, (startdate, enddate), currencyfrom, currencyto)
    exrate = getExchRateXml(exrates)

    if debug:
        with open(debug_filename, 'w') as f:
            f.write(str(''.join(exrate)))
        return
    
    ins_rows = 0
    if exrates:
        conn = exratedb.connect_db(DB_SERVER, DB_USER, DB_PASSWORD, DB_DATABASE)

        for exratechunk in exrate:
            ins_rows += exratedb.execute_proc_return_value(conn
                                                          , 'ttsp_ins_exchrate'
                                                          , (exratechunk
                                                             , overwrite
                                                             , exratedb.output_param(long)
                                                             )
                                                          )[0]

        conn.close()

    return ins_rows

