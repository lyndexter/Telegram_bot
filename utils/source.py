import csv


def read_csv(file_path):
    with open(file_path, encoding='utf-8') as source:
        csv_reader = csv.reader(source, delimiter=",")

        csv_list = []
        for row in csv_reader:
            csv_list.append(row)
        return csv_list


def write_to_txt(file_path, lines):
    with open(file_path, encoding='utf-8') as source:
        for line in lines:
            source.write(line)
