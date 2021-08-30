from unittest import TestCase
import Scanner.connect as cn
import datetime

user_name = input("Username: ")
pass_word = input("Password: ")


class ConnectTest(TestCase):
    def setUp(self) -> None:
        username = user_name
        password = pass_word
        self.market_VS_two_offers = "../SavedMarkets/market_VS_two_offers.html"
        self.session = cn.dantem_login(username=username, password=password)
        self.response = cn.scan_market(self.session, "16.12.2020", "18.12.2020")
        self.parsed_offers = [{'datetime': '16.4.2021 15:05',
                               'place': 'Podivín',
                               'link': 'https://moznosti.dantem.net/options/mar'
                                       'ket/?market-id=123249&do=market-accept'},
                              {'datetime': '20.4.2021 18:15',
                               'place': 'Pelhřimov',
                               'link': 'https://moznosti.dantem.net/options/mar'
                                       'ket/?market-id=123218&do=market-accept'}]
        self.dates = [[datetime.datetime(2021, 4, 14, 15, 0),
                       datetime.datetime(2021, 4, 14, 17, 0)],
                      [datetime.datetime(2021, 4, 16, 15, 0),
                       datetime.datetime(2021, 4, 16, 17, 0)]]


    def test_dantem_login(self):
        self.assertEqual(self.session.headers['Connection'], 'keep-alive')


    def test_scan_market(self):
        no_offer_text = "Aktuálnímu filtru neodpovídají žádné nabídky"
        self.assertTrue(no_offer_text in self.response)


    def test_parse_market(self):
        with open(self.market_VS_two_offers, encoding="utf-8") as f:
            response = f.read()
        self.assertEqual(cn.parse_market(response), self.parsed_offers)


    def test_get_datetime(self):
        date_time = cn.get_datetime(self.parsed_offers[0])
        self.assertEqual(date_time, datetime.datetime(2021, 4, 16, 15, 5))


    def test_is_valid_offer(self):
        self.assertTrue(cn.is_valid_offer(self.parsed_offers[0], self.dates))












