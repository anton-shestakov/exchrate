from exchrate import config
import unittest

class TestCurrencyCode(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.cur = config.CurrencyCode()

    def test_loaded_data(self):
        
        self.assertTrue(self.cur.get_ccy_codes())
    
    def test_data_quality(self):
        
        self.assertEqual(self.cur.get_ccy_num_code('USD'), 840)

    def test_empty_data(self):
        
        self.assertEqual(self.cur.get_ccy_num_code('NA'), -1)


class TestExchangeRateSource(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.source_obj = config.ExchangeRateSource()

    def test_get_source_config(self):
        self.assertTrue(self.source_obj.get_source_config('NBU-json'))

    def test_get_source_config_bad(self):
        self.assertFalse(self.source_obj.get_source_config('N/a'))

