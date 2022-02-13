dltr = '  '

def get_offset_strings(data):
    titles = data[0].get_titles()

    lens = []
    for i, t in enumerate(titles):
        lens.append(len(t))
        for d in data:
            lens[i] = max(len(d.get_values()[i]), lens[i])

    hist_lens = [0, ]
    for i in range(data[0].get_historical_offset()):
        hist_lens[0] += (lens[i] + len(dltr))
    hist_lens[0] -= len(dltr)
    for i in range(data[0].get_historical_offset(), len(lens)):
        hist_lens.append(lens[i])

    return (
        lens, dltr.join('{{:{}}}'.format(l) for l in lens),
        hist_lens, '{{:>{}}}{}{}'.format(
            hist_lens[0], dltr, dltr.join('{{:{}}}'.format(l) for l in hist_lens[1:])
        )
    )

def report_console(data, historical):
    if not len(data):
        print('Dataset is empty')

    lens, offsets_string, hist_lens, hist_offsets_string = get_offset_strings(data)
    total_len = sum(lens) + len(lens)*len(dltr) - len(dltr)

    print(offsets_string.format(*data[0].get_titles()))
    print('-' * total_len)
    for d in data:
        print(offsets_string.format(*d.get_values()))
        if not historical:
            continue
        for v in d.get_historical_values():
            print(hist_offsets_string.format(*v))
        print('-' * total_len)

def report_csv(data, historical):
    dltr = ';'

    if not len(data):
        print('Dataset is empty')

    row = data[0]

    offsets_string = dltr.join('{}' for t in row.get_titles())
    historical_values_count = len(row.get_titles()) - row.get_historical_offset() + 1
    hist_offsets_string = '{}{}'.format(
        dltr * (row.get_historical_offset() - 1),
        dltr.join('{}' for i in range(historical_values_count))
    )

    print(offsets_string.format(*row.get_titles()))
    for d in data:
        print(offsets_string.format(*d.get_values()))
        if not historical:
            continue
        for v in d.get_historical_values():
            print(hist_offsets_string.format(*v))
