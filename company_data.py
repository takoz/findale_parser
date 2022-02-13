import locale

from collections import namedtuple

import requests

CompanyDataRow = namedtuple('CompanyDataRow', ['title', 'value', 'compact'])

class CompanyData:

    _valid = False

    _data = []
    _historical_data = []

    _company_id = None
    _currency = None
    _market_code = None
    _industry_id = None
    _sector_id = None

    _compact = False

    def __init__(self, ticker, compact):
        self._compact = compact

        r = requests.get('https://findale.pro/api/company?code={}'.format(ticker))
        if r.status_code != 200:
            print('Could not get {} info: {}'.format(ticker, r.status_code))
            return

        self._company_id = r.json()['asset']['company_id']
        self._currency = r.json()['asset']['currency']
        self._market_code = r.json()['asset']['market_code']
        self._industry_id = r.json()['company']['industry_id']
        self._sector_id = r.json()['company']['sector_id']

        self._data = []

        self._data.append(
            CompanyDataRow('Тикер', ticker, True)
        )
        self._data.append(
            CompanyDataRow('Название', r.json()['company']['name'], True)
        )
        self._data.append(
            CompanyDataRow('Сектор', r.json()['company']['sector'], False)
        )
        self._data.append(
            CompanyDataRow('Индустрия', r.json()['company']['industry'], False)
        )
        self._data.append(
            CompanyDataRow('Рыночная капитализация',
                           self.strfloat(r.json()['asset']['market_cap']),
                           True)
        )
        self._data.append(
            CompanyDataRow('Текущая стоимость акции',
                           self.strfloat(r.json()['asset']['last_price'], 2),
                           True)
        )

        r = requests.get(
            'https://findale.pro/api/report?company_id={}&currency={}&section=ind&type=Y'.format(
                self._company_id, self._currency
            )
        )
        if r.status_code != 200:
            print('Could not get {} info: {}'.format(ticker, r.status_code))
            return

        last_market_cap = r.json()['last_q']['last_q_data']['market_cap']
        last_profit = r.json()['last_q']['last_q_data']['profit_net']
        last_ocf = r.json()['last_q']['last_q_data']['cash_oper_activities_net']
        last_total_equity = r.json()['last_q']['last_q_data']['total_equity']
        last_total_assets = r.json()['last_q']['last_q_data']['total_assets']
        last_net_debt = r.json()['last_q']['last_q_data']['debt_net']
        last_ebitda = r.json()['last_q']['last_q_data']['ebitda']
        last_revenue = r.json()['last_q']['last_q_data']['revenue']
        roe = last_profit / last_total_equity * 100
        roa = last_profit / last_total_assets * 100
        p_e = last_market_cap / last_profit
        p_ocf = last_market_cap / last_ocf
        p_bv = last_market_cap / last_total_equity
        p_s = last_market_cap / last_revenue
        net_debt_ebitda = last_net_debt / last_ebitda

        self._historical_data = []
        for period in r.json()['data']:
            year = period['year']
            p = period['data']['market_cap']
            e = period['data']['profit_net']
            ocf = period['data']['cash_oper_activities_net']
            total_equity = period['data']['total_equity']
            total_assets = period['data']['total_assets']
            net_debt = period['data']['debt_net']
            ebitda = period['data']['ebitda']
            revenue = period['data']['revenue']

            self._historical_data.append(
                (
                    '/{}/'.format(year),
                    self.strfloat(p / e),
                    self.strfloat(p / ocf),
                    self.strfloat(p / total_equity),
                    self.strfloat(p / revenue),
                    self.strfloat(e / total_equity * 100),
                    self.strfloat(e / total_assets * 100),
                    self.strfloat(net_debt / ebitda, 3),
                )
            )

        self._data.append(
            CompanyDataRow('(P/E)', self.strfloat(p_e), True)
        )
        self._data.append(
            CompanyDataRow('(P/OCF)', self.strfloat(p_ocf), True)
        )
        self._data.append(
            CompanyDataRow('(P/BV)', self.strfloat(p_bv), True)
        )
        self._data.append(
            CompanyDataRow('(P/S)', self.strfloat(p_s), True)
        )
        self._data.append(
            CompanyDataRow('(ROE)', self.strfloat(roe), True)
        )
        self._data.append(
            CompanyDataRow('(ROA)', self.strfloat(roa), True)
        )
        self._data.append(
            CompanyDataRow('(NET DEBT/EBITDA)', self.strfloat(net_debt_ebitda, 3), True)
        )

        self._valid = True

    def is_valid(self):
        return self._valid

    def get_titles(self):
        if self._compact:
            return [d.title for d in self._data if d.compact]
        else:
            return [d.title for d in self._data]

    def get_values(self):
        if self._compact:
            return [d.value for d in self._data if d.compact]
        else:
            return [d.value for d in self._data]

    def get_historical_values(self):
        return self._historical_data

    def get_historical_offset(self):
        if self._compact:
            return 4
        else:
            return 6

    def strfloat(self, val, prec=1):
        return locale.format_string('%.{}f'.format(prec), val)

