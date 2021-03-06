import argparse
import requests
import locale

from company_data import CompanyData
from report import report_console, report_csv, report_md


if __name__ == '__main__':
    locale.setlocale(locale.LC_NUMERIC, 'ru_RU.utf8')
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-a', '--all-data', action='store_true', help='report all data'
    )
    parser.add_argument(
        '-i', '--historical', action='store_true', help='show historical data'
    )
    parser.add_argument(
        '-f', '--format', choices=['CONSOLE', 'CSV', 'MD'],
        default='CONSOLE', help='output format'
    )
    parser.add_argument(
        '-p', '--period', choices=['Y', 'Q'],
        default='Y', help='historical data period'
    )
    parser.add_argument(
        'tickers', metavar='T', type=str, nargs='+', help='tickers'
    )
    args = parser.parse_args()

    data = []
    for t in args.tickers:
        d = CompanyData(t, (not args.all_data), args.period)
        if d.is_valid():
            data.append(d)

    if args.format == 'CONSOLE':
        report_console(data, args.historical)
    elif args.format == 'CSV':
        report_csv(data, args.historical)
    elif args.format == 'MD':
        report_md(data, args.historical)
