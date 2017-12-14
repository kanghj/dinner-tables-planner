from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
import string
import itertools
import io


def make_workbook(persons, tables):
    wb = Workbook()
    ws = wb.active

    alphabet_first = [''] + [letter for letter in string.ascii_uppercase]
    column_names = [''.join(name)
                    for name in itertools.combinations_with_replacement(alphabet_first, 2)
                    ][1:]

    starting_col = 2
    for i, (table_name, members) in enumerate(tables.items()):
        column_name = column_names[i]
        ws[column_name + '1'] = table_name
        for j, member in enumerate(members):
            ws[column_name + str(j + 2)] = persons[int(member) - 1]

    return io.BytesIO(save_virtual_workbook(wb))



