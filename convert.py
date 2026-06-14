import csv
import argparse
import re


def handle_fidelityhsa(args):
    with open(args.output_csv_file, 'w', newline='') as out_f:
        csv_writer = csv.writer(out_f)
        csv_writer.writerow([ 'Date', 'Payee', 'Note', 'Amount' ])

        for filename in args.input_csv_files:
            with open(filename, 'r') as inp_f:
                line_1 = inp_f.readline()
                if not line_1:
                    raise ValueError(f"First line wasn't empty in {filename}")
                line_2 = inp_f.readline()
                if not line_2:
                    raise ValueError(f"Second line wasn't empty in {filename}")
                csv_reader = csv.DictReader(inp_f)
                for row in csv_reader:
                    if row['Run Date'] and row['Action'] and row['Amount ($)']:
                        csv_writer.writerow([
                            row['Run Date'],
                            row['Action'].capitalize().replace(' (cash)', ''),
                            row['Description'].capitalize() if row['Description'] != 'No Description' else '',
                            row['Amount ($)'].replace('$', '')
                        ])



def handle_venmo(args):
    with open(args.output_csv_file, 'w', newline='') as out_f:
        csv_writer = csv.writer(out_f)
        csv_writer.writerow([ 'Date', 'Payee', 'Note', 'Amount' ])

        for filename in args.input_csv_files:
            with open(filename, 'r') as inp_f:
                line_1 = inp_f.readline()
                parsed_line_1 = re.match(r'^Account Statement - \(@(.*)\)', line_1)
                if not parsed_line_1:
                    raise ValueError(f'First line was not "Account Statement - " with a name in {filename}')
                person_name = parsed_line_1[1].replace('-', ' ')
                line_2 = inp_f.readline()
                if (not line_2.startswith('Account Activity')):
                    raise ValueError(f'Second line did not start with "Account Activity" in {filename}.')
                csv_reader = csv.DictReader(inp_f)
                for row in csv_reader:
                    if row['Datetime'] and row['Amount (total)']:
                        dt = row['Datetime']
                        csv_writer.writerow([
                            dt[0:10].replace('-', ' '),
                            row['To'] if row['From'] == person_name else row['From'],
                            row['Note'],
                            row['Amount (total)'].replace('$', '')
                        ])



parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

parser_fidelityhsa = subparsers.add_parser('fidelityhsa')
parser_fidelityhsa.add_argument("input_csv_files", nargs='+')
parser_fidelityhsa.add_argument("--output-csv-file", '-o', required=True)
parser_fidelityhsa.set_defaults(func=handle_fidelityhsa)

parser_venmo = subparsers.add_parser('venmo')
parser_venmo.add_argument("input_csv_files", nargs='+')
parser_venmo.add_argument("--output-csv-file", '-o', required=True)
parser_venmo.set_defaults(func=handle_venmo)


args = parser.parse_args()
try:
    args.func(args)
except ValueError as e:
    print(e.msg)
except KeyboardInterrupt:
    pass
