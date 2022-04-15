"""Prepare data for Plotly Dash."""
import re
import numpy as np
import pandas as pd
from datetime import datetime, timezone


def erase_file(file_name):
    f = open(file_name, "w+")
    f.close()

def init_output_file():
    file_name = "data/output.csv"
    erase_file(file_name)
    with open(file_name, 'w+') as f:
        f.write('created;constituency_name;party_code;votes')
        f.write("\n")


def init_warnings_file():
    file_name = "data/warnings.csv"
    erase_file(file_name)


def init_parties_file():
    parties_list = [
                        {"party_code": "C","party_name": "Conservative"},
                        {"party_code": "L","party_name": "Labour"},
                        {"party_code": "SNP","party_name": "Scottish National Party"},
                        {"party_code": "LD","party_name": "Liberal Democrats"},
                        {"party_code": "G","party_name": "Green Party"},
                        {"party_code": "Ind","party_name": "Independent"},
                    ]

    file_name = "data/parties.csv"
    erase_file(file_name)
    with open(file_name, 'w+') as f:
        f.write('party_code;party_name')
        for party in parties_list:
            f.write("\n")
            party_code = party['party_code']
            party_name = party['party_name']
            f.write(party_code + ';' + party_name)


def init_files():
    init_output_file()
    init_warnings_file()
    init_parties_file()


def transform_csv(input_file_name):
    init_files()

    file = open("data/" + input_file_name, 'r')
    warning_messages = []
    line_count = 0
    while True:
        line_count += 1
        line_str = file.readline()
        if not line_str:
            break
        line = re.split("(?<!\\\\),", line_str)
        constituency_name = line[0]
        line = line[1:]

        pair_num_for_split = 2
        pairs = [line[i:i + pair_num_for_split] for i in range(0, len(line), pair_num_for_split)]
        pair_count = 0

        for pair in pairs:
            pair_count += 1
            try:
                result_error = False
                votes = int(pair[0].strip())
                party_code = str(pair[1].strip())
                if not isinstance(party_code, str):
                    result_error = True
                    warning_messages.append(
                        'error Party name is not string type in line ' + str(line_count) + ' in elem: ' + str(
                            pair_count) + '. Please, check line: ' + line_str)
                if not isinstance(votes, int) or votes < 0:
                    result_error = True
                    warning_messages.append('error votes count is not integer type in line ' + str(line_count) + 'in '
                                                                                                                 'elem: '
                                            + str(pair_count) + '. Please, check line: ' + line_str)
                if not result_error:
                    with open('data/output.csv', 'a') as f:
                        constituency_name = constituency_name.replace('\,', ',')
                        f.write(str(datetime.now(timezone.utc).strftime(
                            "%Y-%m-%d %H:%M:%S")) + ';' + constituency_name + ';' + party_code + ';' + str(votes))
                        f.write("\n")
            except Exception as e:
                print('error')
                print(e)
                warning_messages.append(
                    'error in line ' + str(line_count) + ' in elem: ' + str(pair_count) + '. Incorrect '
                                                                                          'pair vote '
                                                                                          'and/or '
                                                                                          'party. '
                                                                                          'Please, '
                                                                                          'check line: '
                                                                                          '' + line_str)
    for warning_message in warning_messages:
        with open('data/warnings.csv', 'a') as f:
            f.write(warning_message)
            f.write("\n")


def create_dataframe(input_file_name):
    """Create Pandas DataFrame from local CSV."""
    transform_csv(input_file_name)
    df = pd.read_csv("data/output.csv", parse_dates=["created"], sep=';')
    df['created'] = pd.to_datetime(df["created"], format='%Y-%m-%d %H:%M:%S')
    df['votes'] = df['votes'].astype('int')

    return df
