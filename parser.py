import argparse
import requests

from company_data import CompanyData

def get_offset_string(data):
    titles = data[0].get_titles()

    lens = []
    for i, t in enumerate(titles):
        lens.append(len(t))
        for d in data:
            lens[i] = max(len(d.get_values()[i]), lens[i])

    return '  '.join('{{:{}}}'.format(l) for l in lens)

def report(data):
    if not len(data):
        print('Dataset is empty')

    offsets_string = get_offset_string(data)
    print(offsets_string.format(*data[0].get_titles()))
    for d in data:
        print(offsets_string.format(*d.get_values()))

def main(compact, tickers):
    data = []
    for t in tickers:
        d = CompanyData(t, compact)
        if d.is_valid():
            data.append(d)
    report(data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--compact', action='store_true', help='compact view')
    parser.add_argument('tickers', metavar='T', type=str, nargs='+', help='tickers')
    args = parser.parse_args()

    main(args.compact, args.tickers)
