###################################
# Data Engineering Coding Challenge
# Parse Fixed Width File
# By Aleksandar Pasquini
###################################

import json
import csv
from collections import OrderedDict

# Please change this to where your json file is located
IN_FILE = "spec.json"

# I assumed that this fields are always required for every file
# There probably should be a row field for values that go under the Column Names
# The code can be changed very easily to accommodate a row field
REQUIRED_FIELDS = ["ColumnNames", "Offsets", "FixedWidthEncoding", "IncludeHeader", "DelimitedEncoding"]


def number_checker(number_list):
    bad_numbers = []
    for element in number_list:
        # Having negative offsets does not make sense and therefore they should be removed
        if element < 0:
            bad_numbers.append(element)
        # I was not sure where to set the upper boundary but I decided to set it at 2^32 to avoid any overflow errors
        # However, the boundary probably should be set at a more reasonable number
        if element >= (2 ^ 32):
            print("WARNING: %s is very big and might cause issues" % str(element))
    return bad_numbers


def convert(in_file, out_file, header):
    line = in_file.readline().split()
    if header.lower() == "true":
        empty_dict = OrderedDict.fromkeys(line)
        writer = csv.DictWriter(out_file, fieldnames=line)
        writer.writeheader()
        # This would continue if there where the values for the rows
    else:
        writer = csv.writer(out_file)
        writer.writerow(line)
        # This would continue if there where the values for the rows


def open_file_extract_info(path):
    spec_dict = {}
    # I make the assumption that all the input files are json files and those file are written in valid json
    # If it is not valid, json.decoder.JSONDecodeError provides a better error message than one I could write
    try:
        with open(path) as json_data:
            data = json.load(json_data, strict=False)
    except OSError:
        raise SystemExit("Could not read/find from %s" % path)
    # I extract the information from the json file to make sure that it is valid and makes sense
    for field in REQUIRED_FIELDS:
        try:
            if field != "Offsets":
                spec_dict[field] = data[field]
            else:
                try:
                    numbers = list(map(int, data[field]))
                    # Offsets with negative or big numbers will cause issues with formatting the file
                    bad_numbers = number_checker(numbers)
                    if bad_numbers:
                        print("%s needs values that are positive. These numbers are bad:" % field)
                        raise SystemExit(*bad_numbers)
                    else:
                        spec_dict[field] = numbers
                # I assume that the offsets are always written in string format or an int
                except ValueError:
                    raise SystemExit("%s needs values that can be turned into an int" % field)
        except KeyError:
            raise SystemExit("%s field is missing in the json file" % field)
    # I can not generate the file if the fields are empty
    for key, value in spec_dict.items():
        if value is None or value == [] or value == "":
            raise SystemExit("%s is missing values" % key)
    # There needs to be an offset for each column
    if len(spec_dict['ColumnNames']) != len(spec_dict['Offsets']):
        raise SystemExit("ColumnNames is not the same length as Offsets")
    # The value for IncludeHeader can only be true or false and I assume that it is in string format
    if type(spec_dict['IncludeHeader']) != str or spec_dict['IncludeHeader'].lower() not in ("true", "false"):
        raise SystemExit("IncludeHeader needs to be True or False (in string form)")
    return spec_dict


def generate_file(column_names, offsets, file):
    index = 0
    # This is where if there was a row field it should replace column_names here
    # The index would keep track of what row has been added but currently there is only one row (ColumnNames)
    while index < int(len(column_names) / len(offsets)):
        file.write("".join("%*s" % i for i in zip(offsets, column_names)))
        file.write('\n')
        index += 1


###
# 1. Generate a fixed width file
###
info = open_file_extract_info(IN_FILE)
try:
    FIXED_WIDTH_FILE = open("Fixed_Width_File", "w", encoding=info["FixedWidthEncoding"])
except LookupError:
    raise SystemExit("unknown encoding: %s" % info["FixedWidthEncoding"])
generate_file(info["ColumnNames"], info["Offsets"], FIXED_WIDTH_FILE)
FIXED_WIDTH_FILE.close()

###
# 2. Implement a parser that can parse the fixed width file and generate a delimited file
###
try:
    READING_FILE = open("FIXED_WIDTH_FILE", "r", encoding=info["FixedWidthEncoding"])
except LookupError:
    raise SystemExit("unknown encoding: %s" % info["FixedWidthEncoding"])
except OSError:
    raise SystemExit("Could not read FIXED_WIDTH_FILE")
try:
    CSV_FILE = open("CSV_FILE.csv", "w", encoding=info["DelimitedEncoding"])
except LookupError:
    raise SystemExit("unknown encoding: %s" % info["DelimitedEncoding"])
convert(READING_FILE, CSV_FILE, info["IncludeHeader"])
READING_FILE.close()
CSV_FILE.close()
