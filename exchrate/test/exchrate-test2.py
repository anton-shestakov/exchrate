import os
import sys
sys.path.insert(1, os.path.abspath('..'))

from exchrate import exrateparse as exchratemod, exratemain as exchratemain, exratedb
from lxml import etree
import xmltodict
import pymssql
import unittest

DB_SERVER = 'enter_server_path'
DB_USER = 'enter_username'
DB_PASSWORD = 'enter_password'
DB_DATABASE = 'enter_database_name'


class ExrateDbTest(unittest.TestCase):

    def test_connection(self):
        conn = exratedb.connect_db(DB_SERVER, DB_USER, DB_PASSWORD, DB_DATABASE)
        self.assertIsInstance(conn, pymssql.Connection)
        conn.close()

    def test_execute_select(self):
        conn = exratedb.connect_db(DB_SERVER, DB_USER, DB_PASSWORD, DB_DATABASE)
        ret_value = exratedb.execute_query(conn, 'SELECT 1 as a')
        self.assertEqual(ret_value[0][0], 1)
        conn.close()

    def test_execute_sp(self):        
        conn = exratedb.connect_db(DB_SERVER, DB_USER, DB_PASSWORD, DB_DATABASE)
        ret_value = exratedb.execute_proc(conn, 'tsp_select_param', (2,))
        self.assertEqual(ret_value[0][0], 2)
        conn.close()

    def test_execute_sp_retvalue(self):
        conn = exratedb.connect_db(DB_SERVER, DB_USER, DB_PASSWORD, DB_DATABASE)
        ret_value = exratedb.execute_proc_return_value(conn, 'tsp_return_param', (3, pymssql.output(long)))
        self.assertEqual(ret_value[0], 3)
        conn.close()

class ExrateImportTest(unittest.TestCase):

    params_load = (
        (('NBU-json', '2015-01-12', '2015-01-13', 'USD', 'UAH', 'Y'), 2)
        ,
        (('NBU-json', '2016-01-01', '2016-03-13', 'USD', 'UAH', 'Y'), 73)
        )
    
    def test_load_period(self):

        for params, result in self.params_load:
            ins_rows = exchratemain.loadExchRate(*params)
            self.assertEqual(ins_rows, result)

if __name__ == '__main__':
    unittest.main()
