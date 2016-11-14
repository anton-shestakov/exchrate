from datetime import date, timedelta, datetime
from lxml import etree
from copy import deepcopy
from . import exrateparse, exratedb

def splitDateRange(startdate, enddate, adddays):

    try:
        sd, ed, td = (datetime.strptime(startdate, '%Y-%m-%d').date(),
                      datetime.strptime(enddate, '%Y-%m-%d').date(),
                      timedelta(adddays)
                      )

        # return start date in any case
        yield sd.isoformat()

        while ed > sd:
            sd += td
            yield sd.isoformat()

    except (ValueError, TypeError):
        return

def getExchRateRange(sourceid, startdate, enddate, currencyfrom, currencyto):

    gen_daterange = splitDateRange(startdate, enddate, 1)
    exrateout = []
    for exrdate in gen_daterange:
        exrate = exrateparse.getExchRate(sourceid, exrdate, currencyfrom, currencyto)
        if exrate.curfrom != None:
            exrateout.append(exrate)

    return exrateout

def getExchRateAsXml(sourceid, startdate, enddate, currencyfrom, currencyto):

    exrate = getExchRateRange(sourceid, startdate, enddate, currencyfrom, currencyto)
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
        for fromCurr, exchRate, toCurr, exchDate in exrate:
            exRate[0].text = exchDate
            exRate[1].text = '1'      # temporarily hardcoded since only 1 source is implemented
            exRate[2].text = str(fromCurr)
            exRate[3].text = str(toCurr)
            exRate[4].text = str(exchRate)
            exRateList.append(deepcopy(exRate))
        # populate xml root element with generated elements
        for xmlExrate in exRateList:
            exRates.append(xmlExrate)
        return etree.tostring(exRates, pretty_print=True).decode()
    else:
        return ''


def loadExchRate(sourceid, startdate, enddate, currencyfrom, currencyto, overwrite='N'):

    exrate = getExchRateAsXml(sourceid, startdate, enddate, currencyfrom, currencyto)
    if exrate:
        conn = exratedb.connect_db('MYPC\DBMAIN', 'py_app', 'zxcv123', 'FRD')
        ins_rows = exratedb.execute_proc_return_value(conn
                                                      , 'ttsp_ins_exchrate'
                                                      , (exrate
                                                         , overwrite
                                                         , exratedb.output_param(long)
                                                         )
                                                      )
        conn.close()
        if ins_rows:
            return ins_rows[0]
    return 0
