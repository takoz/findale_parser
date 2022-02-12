import argparse
import requests

def get_company_data(ticker, compact):
    r = requests.get('https://findale.pro/api/company?code={}'.format(ticker))
    if r.status_code != 200:
        print('Could not get {} info: {}'.format(ticker, r.status_code))
        return None

    company_id = r.json()['asset']['company_id']
    currency = r.json()['asset']['currency']
    market_capitalization = r.json()['asset']['market_cap']
    market_code = r.json()['asset']['market_code']
    last_share_price = r.json()['asset']['last_price']

    name = r.json()['company']['name']
    industry = r.json()['company']['industry']
    sector = r.json()['company']['sector']
    industry_id = r.json()['company']['industry_id']
    sector_id = r.json()['company']['sector_id']

    result = []

    result.append(ticker)
    result.append(name)
    if not compact:
        result.append(sector)
        result.append(industry)
    result.append(repr(market_capitalization))
    result.append(repr(last_share_price))

    return result

def longest_len(header, data, index):
    result = len(header) + 1
    for d in data:
        result = max(result, len(d[index]) + 1)
    return result

def report(data, compact):
    headers = []
    headers.append(('Тикер', 10))
    headers.append(('Название', longest_len('Название', data, 1)))
    if not compact:
        headers.append(('Сектор', longest_len('Сектор', data, 2)))
        headers.append(('Индустрия', longest_len('Индустрия', data, 3)))
    headers.append(('Рыночная капитализация', 25))
    headers.append(('Текущая стоимость акции', 25))

    offsets_string = ' '.join('{{:{}}}'.format(h[1]) for h in headers)
    print(offsets_string.format(*[h[0] for h in headers]))
    for company_data in data:
        print(offsets_string.format(*company_data))

def main(compact, tickers):
    data = []
    for t in tickers:
        d = get_company_data(t, compact)
        if d is not None:
            data.append(d)
    report(data, compact)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--compact', action='store_true', help='compact view')
    parser.add_argument('tickers', metavar='T', type=str, nargs='+', help='tickers')
    args = parser.parse_args()

    main(args.compact, args.tickers)
