import csv


def iterate(data_path):
    with open(data_path, mode="rb") as data_file:
        reader = csv.DictReader(data_file)
        for line in reader:
            yield line


def data_count(data_path):
    with open(data_path) as data_file:
        return len(data_file.readlines())-1
