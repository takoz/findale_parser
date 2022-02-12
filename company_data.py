from collections import namedtuple

import requests

CompanyDataRow = namedtuple('CompanyDataRow', ['title', 'value', 'compact'])

class CompanyData:

    _data = []

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
            CompanyDataRow('Рыночная капитализация', r.json()['asset']['market_cap'], True)
        )
        self._data.append(
            CompanyDataRow('Текущая стоимость акции', r.json()['asset']['last_price'], True)
        )

    def is_valid(self):
        return self._company_id is not None

    def get_titles(self):
        if self._compact:
            return [d.title for d in self._data if d.compact]
        else:
            return [d.title for d in self._data]

    def get_values(self):
        if self._compact:
            return [str(d.value) for d in self._data if d.compact]
        else:
            return [str(d.value) for d in self._data]

