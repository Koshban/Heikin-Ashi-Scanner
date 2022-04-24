from prettytable import PrettyTable
from util import get_logger

my_logger = get_logger(__name__)
bear_rev_table = PrettyTable()
free_fall_table = PrettyTable()
ema_table = PrettyTable()
bollinger_table = PrettyTable()
bear_rev_field_names = [
    'Sym',
    'BearRevAfter',
    'vol_T/50',
    'Close',
    'EMA9/21',
    'PriceVsEMA9',
    'RSI14',
    'Sources'
    ]
free_fall_field_names = [
    'Sym',
    'FreeFallDays',
    'vol_T/50',
    'Close',
    'EMA9/21',
    'PriceVsEMA9',
    'RSI14',
    'Sources'
    ]
ema_field_names = [
    'Sym',
    'vol_T/50',
    'Close',
    'Comment',
    'MA100',
    'MA200',
    'RSI14',
    'Sources'
    ]
bollinger_field_names = [
    'Sym',
    'Comment',
    'vol_T/50',
    'Close',
    'EMA9/21',
    'RSI14',
    'Sources'
    ]
bear_rev_table.field_names =  bear_rev_field_names
ema_table.field_names =  ema_field_names
free_fall_table.field_names = free_fall_field_names
bollinger_table.field_names = bollinger_field_names


def add_to_output(row):
    bear_rev_table.add_row(row)


def add_to_freefall(row):
    free_fall_table.add_row(row)


def add_to_emax(row):
    ema_table.add_row(row)


def add_to_bollinger(row):
    bollinger_table.add_row(row)


def get_signal_tables():
    bear_signal = get_bear_rev_table()
    free_fall_signal = get_free_fall_table()
    emax_signal = get_ema_table()
    bollinger_signal = get_bollinger_table()
    return [bear_signal, emax_signal, bollinger_signal, free_fall_signal]


def get_bear_rev_table():
    my_logger.debug(bear_rev_table)
    signal = bear_rev_table.get_html_string(attributes={"border":"1px", "cellspacing":"1", "white-space":"nowrap"})
    signal = table_hack(signal)
    return signal


def get_free_fall_table():
    my_logger.debug(free_fall_table)
    html_table = free_fall_table.get_html_string(attributes={"border":"1px", "cellspacing":"1", "white-space":"nowrap"})
    html_table = table_hack(html_table)
    return html_table


def get_ema_table():
    my_logger.debug(ema_table)
    html_table = ema_table.get_html_string(attributes={"border":"1px", "cellspacing":"1", "white-space":"nowrap"})
    html_table = table_hack(html_table)
    return html_table

def get_bollinger_table():
    my_logger.debug(bollinger_table)
    html_table = bollinger_table.get_html_string(attributes={"border":"1px", "cellspacing":"1", "white-space":"nowrap"})
    html_table = table_hack(html_table)
    return html_table


def table_hack(signal):
    to_red_str = "<td bgcolor=\"#ffb3b3\">{0}</td>"
    from_red_str = "<td>{0}XR</td>"
    to_green_str = "<td bgcolor=\"#c2f0c2\">{0}</td>"
    from_green_str = "<td>{0}XG</td>"
    for count in range(30):
        signal = signal.replace( from_red_str.format(count), to_red_str.format(count))
        signal = signal.replace( from_green_str.format(count), to_green_str.format(count))
    signal = signal.replace("<td>GREEN", "<td bgcolor=\"#c2f0c2\">")
    signal = signal.replace("<td>RED", "<td bgcolor=\"#ffb3b3\">")

    final_signal = ""
    import re
    pattern = '<td>(.*)XG</td>'
    for line in iter(signal.splitlines()):
        if "XG</td>" in line:
            result = re.search(pattern, line)
            if result and result.group and len(result.group()) > 0:
                value = result.group(1)
                new_line = to_green_str.format(value)
                final_signal = "{0}\n{1}".format(final_signal, new_line)
                continue
        final_signal = "{0}\n{1}".format(final_signal, line)
    return final_signal
