import argparse
import csv
from os.path import join

import pandas as pd
import xlrd


def excel_to_csv(excel_fname):
    workbook = xlrd.open_workbook(excel_fname)
    worksheet = workbook.sheet_by_index(0)
    csv_fname = excel_fname.replace('xlsx', 'csv')
    with open(csv_fname, 'w') as f:
        writer = csv.writer(f)
        for row in worksheet.get_rows():
            writer.writerow(row)
    return csv_fname


def create_yearly_csvs(filename, out_dir, date_col_label=u'DispatchDate'):
    if '.xlsx' in filename:
        filename = excel_to_csv(filename)

    df = pd.read_csv(filename)
    columns = df.columns.values
    c = ''
    if date_col_label not in columns:
        resp = ''
        while resp != 'y':
            print '{} column not found. Which of the following are the dispatch date?: '
            for i, col in enumerate(columns):
                print str(i) + ": " + col
            idx = int(raw_input("Input column number to rename: "))
            c = columns[idx]
            resp = raw_input("You selected {}. Are you sure? (y/n) ".format(c))

        df.rename(columns={c: date_col_label}, inplace=True)

    all_years = sorted(list(set(df[date_col_label].str[-4:].tolist())))
    for year in all_years:
        year_df = df[df[date_col_label].apply(lambda x: True if year in x else False)]
        if '01/01/' in year_df[date_col_label].head(1).to_string() and \
                        '12/31/' in year_df[date_col_label].tail(1).to_string():
            new_file = join(out_dir, 'INC{}.csv'.format(year))
            print "Creating {}".format(new_file)
            year_df.to_csv(new_file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", metavar='N', type=str,
                        help="The excel or csv file to transform")
    # parser.add_argument("-c", "--county", type=str,
    #                     help="The county code (note this is a string and may have a leading 0)")
    # parser.add_argument("-n", "--nocheck", action="store_true",
    #                     help="Do not ask for confirmation before generating shapefile")
    # parser.add_argument("-l", "--level", type=str,
    #                     help="Define the level of granularity ('tract', or 'bg' for block group).")

    args = parser.parse_args()
    big_file = args.file
    out_dir = join('North Carolina', 'Charlotte', 'Yearly')

    create_yearly_csvs(big_file, out_dir=out_dir)


if __name__ == '__main__':
    main()
