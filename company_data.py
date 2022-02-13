import locale

from collections import namedtuple

import requests

CompanyDataRow = namedtuple('CompanyDataRow', ['title', 'value', 'compact'])
IndicatorDesc = namedtuple('IndicatorDesc', ['title', 'name', 'compact', 'prec'])

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

    _indicators = (
        IndicatorDesc('P/E  ', 'p_e_rt', True, 1),
        IndicatorDesc('P/OCF', 'p_ocf', True, 1),
        IndicatorDesc('P/BV ', 'p_bv', True, 1),
        IndicatorDesc('P/S  ', 'p_s_rt', True, 1),
        IndicatorDesc('EV/EBITDA', 'ev_ebitda_rt', True, 1),

        IndicatorDesc('NET DEBT/EBITDA', 'ebitda_net_rt', True, 3),
        IndicatorDesc('DEBT/EBITDA', 'ebitda_debt_rt', True, 3),
        IndicatorDesc('OCF/DEBT', 'ocf_debt', False, 1),
        IndicatorDesc('OCF/equity', 'd_e_rt', False, 3),

        IndicatorDesc('ROE  ', 'roe', True, 1),
        IndicatorDesc('ROA  ', 'roa', True, 1),
    )

    _company_info_url = 'https://findale.pro/api/company?code={}'
    _company_indicators_url = (
        'https://findale.pro/api/report?company_id={}&currency={}&section=ind&type={}'
    )

    def __init__(self, ticker, compact, report_period):
        self._compact = compact

        r = requests.get(self._company_info_url.format(ticker))
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
            self._company_indicators_url.format(
                self._company_id, self._currency, report_period
            )
        )
        if r.status_code != 200:
            print('Could not get {} info: {}'.format(ticker, r.status_code))
            return

        self._data.append(
            CompanyDataRow('(EPS)', self.strfloat(r.json()['last_q']['last_q_data']['eps']), True)
        )

        for desc in self._indicators:
            self._data.append(
                CompanyDataRow(
                    desc.title,
                    self.strfloat(r.json()['last_q']['last_q_data'].get(desc.name), desc.prec),
                    desc.compact
                )
            )

        self._historical_data = []
        for period in r.json()['data']:
            if report_period == 'Y':
                row = ['/{}/'.format(period['year']), ]
            else:
                row = ['/{} {}/'.format(period['year'], period['quarter']), ]
            for desc in self._indicators:
                row.append(self.strfloat(period['data'].get(desc.name), desc.prec))
            self._historical_data.append(row)

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
        if not self._compact:
            return self._historical_data
        data = []
        for r in self._historical_data:
            data.append(
                [v for i, v in enumerate(r) if self._data[i + 6].compact]
            )
        return data

    def get_historical_offset(self):
        if self._compact:
            return 5
        else:
            return 7

    def strfloat(self, val, prec=1):
        if val is None:
            return '-'
        return locale.format_string('%.{}f'.format(prec), val)

