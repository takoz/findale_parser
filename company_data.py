import locale

from collections import namedtuple

import requests

CompanyDataRow = namedtuple(
    'CompanyDataRow', ['title', 'value']
)

JsonDataDesc = namedtuple(
    'JosnDataDesc', ['title', 'json_name', 'compact', 'prec']
)

class CompanyData:

    _valid = False

    _data = []
    _historical_data = []

    _company_id = None
    _currency = None
    _market_code = None
    _industry_id = None
    _sector_id = None

    _indicators = (
        JsonDataDesc('P/E  ', 'p_e_rt', True, 1),
        JsonDataDesc('P/OCF', 'p_ocf', True, 1),
        JsonDataDesc('P/BV ', 'p_bv', True, 1),
        JsonDataDesc('P/S  ', 'p_s_rt', True, 1),
        JsonDataDesc('EV/EBITDA', 'ev_ebitda_rt', True, 1),

        JsonDataDesc('NET DEBT/EBITDA', 'ebitda_net_rt', True, 3),
        JsonDataDesc('DEBT/EBITDA', 'ebitda_debt_rt', True, 3),
        JsonDataDesc('OCF/DEBT', 'ocf_debt', False, 1),
        JsonDataDesc('OCF/equity', 'd_e_rt', False, 3),

        JsonDataDesc('ROE  ', 'roe', True, 1),
        JsonDataDesc('ROA  ', 'roa', True, 1),
    )

    _report_fields = (
        JsonDataDesc('EPS   ', 'eps', True, 1),
        JsonDataDesc('MARKET CAP', 'market_cap', True, 0),
        JsonDataDesc('REVENUE', 'revenue', True, 0),
        JsonDataDesc('PROFIT', 'profit_net', True, 0),
        JsonDataDesc('OCF   ', 'cash_oper_activities_net', True, 0),
        JsonDataDesc('ASSETS', 'total_assets', True, 0),
        JsonDataDesc('FIXED ASSETS', 'noncur_assets', False, 0),
        JsonDataDesc('CURRENT ASSETS', 'cur_assets', False, 0),
        JsonDataDesc('DEBT', 'total_liab', True, 0),
        JsonDataDesc('LONGTERM DEBT', 'long_liab', False, 0),
        JsonDataDesc('SHORTTERM DEBT', 'short_liab', False, 0),
        JsonDataDesc('OTHER DEBT', 'other_liab', False, 0),
        JsonDataDesc('TOTAL EQUITY', 'total_equity', True, 0),
        JsonDataDesc('SHAREHOLD EQUITY', 'sharehold_eq', False, 0),
        JsonDataDesc('RESERVED EQUITY', 'reserv_eq', False, 0)
    )

    _company_info_url = (
        'https://findale.pro/api/company?code={}'
    )
    _company_indicators_url = (
        'https://findale.pro/api/report?company_id={}'
        '&currency={}&section=ind&type={}'
    )
    _company_report_url = (
        'https://findale.pro/api/report?company_id={}'
        '&currency={}&section=rep&type={}'
    )

    _compact = False

    def __init__(self, ticker, compact, report_period):
        self._compact = compact

        # getting general info
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
            CompanyDataRow('TICKER', ticker)
        )
        self._data.append(
            CompanyDataRow('NAME', r.json()['company']['name'])
        )
        if not compact:
            self._data.append(
                CompanyDataRow('SECTOR', r.json()['company']['sector'])
            )
            self._data.append(
                CompanyDataRow('INDUSTRY', r.json()['company']['industry'])
            )
        self._data.append(
            CompanyDataRow('SHARE PRICE',
                           self.strfloat(r.json()['asset']['last_price'], 4))
        )

        # getting indicators
        ri = requests.get(
            self._company_indicators_url.format(
                self._company_id, self._currency, report_period
            )
        )
        if r.status_code != 200:
            print(
                'Could not get {} indicators: {}'.format(ticker, r.status_code)
            )
            return

        # getting report
        r = requests.get(
            self._company_report_url.format(
                self._company_id, self._currency, report_period
            )
        )
        if r.status_code != 200:
            print('Could not get {} report: {}'.format(ticker, r.status_code))
            return

        for desc in self._report_fields:
            if compact and not desc.compact:
                continue
            self._data.append(
                CompanyDataRow(
                    desc.title,
                    self.strfloat(
                        r.json()['last_q']['last_q_data'].get(desc.json_name),
                        desc.prec
                    )
                )
            )

        for desc in self._indicators:
            if compact and not desc.compact:
                continue
            self._data.append(
                CompanyDataRow(
                    desc.title,
                    self.strfloat(
                        ri.json()['last_q']['last_q_data'].get(desc.json_name),
                        desc.prec
                    )
                )
            )

        # filling historical data
        self._historical_data = []
        for i, period in enumerate(r.json()['data']):
            if report_period == 'Y':
                row = ['/{}/'.format(period['year']), ]
            else:
                row = ['/{} {}/'.format(period['year'], period['quarter']), ]
            for desc in self._report_fields:
                if compact and not desc.compact:
                    continue
                row.append(
                    self.strfloat(
                        period['data'].get(desc.json_name), desc.prec
                    )
                )

            for desc in self._indicators:
                if compact and not desc.compact:
                    continue
                row.append(
                    self.strfloat(
                        ri.json()['data'][i]['data'].get(desc.json_name),
                        desc.prec
                    )
                )

            self._historical_data.append(row)

        self._valid = True

    def is_valid(self):
        return self._valid

    def get_titles(self):
        return [d.title for d in self._data]

    def get_values(self):
        return [d.value for d in self._data]

    def get_historical_values(self):
        return self._historical_data

    def get_historical_offset(self):
        return (len(self._data) - len(self._historical_data[0]))

    def get_historical_count(self):
        return len(self._historical_data[0])

    @staticmethod
    def strfloat(val, prec=1):
        if val is None:
            return '-'
        return locale.format_string('%.{}f'.format(prec), val)

    def get_precisions(self):
        precisions = []
        for r in self._report_fields:
            if self._compact and not r.compact:
                continue
            precisions.append(r.prec)
        for r in self._indicators:
            if self._compact and not r.compact:
                continue
            precisions.append(r.prec)

        return precisions
