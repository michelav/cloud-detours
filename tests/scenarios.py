#!/usr/bin/env python3
from subprocess import call
from time import time
import yaml
import sys
from pathlib import Path
from os.path import normpath, join
from datetime import datetime
import csv


def print_as_markdown(the_file, msg, mark):
    if "title" == mark:
        length = len(msg)
        print(msg, file=the_file)
        print(msg)
        print("=" * length, file=the_file)
        print("=" * length)
    elif 'h2' == mark:
        out = "## {}".format(msg)
        print(out, file=the_file)
        print(out)
    elif 'h3' == mark:
        out = "### {}".format(msg)
        print(out, file=the_file)
        print(out)
    elif 'h5' == mark:
        out = "##### {}".format(msg)
        print(out, file=the_file)
        print(out)
    elif 'block' == mark:
        out = "> {}".format(msg)
        print(out, file=the_file)
        print(out)
    elif 'item' == mark:
        out = "* {}".format(msg)
        print(out, file=the_file)
        print(out)


def name_output(x, name, cl):
    return "{:0>2d}_{}_{}.txt".format(x, name, cl)


def execute_case(x, case, report_dir, rep, site):
    name = case['name']
    command = "%s %s download" % (case['command'], site)
    cl = case['class']
    print_as_markdown(rep, 'command', "h5")
    print_as_markdown(rep, command, "block")
    print_as_markdown(rep, "Type: {}".format(name), "item")
    print_as_markdown(rep, "Class: {}".format(cl), "item")

    out = normpath(join(report_dir, name_output(x, name, cl)))
    with open(out, 'w') as out_file:
        start = time()
        call([command], stdout=out_file, stderr=out_file, shell=True)
        end = time()

    elapsed = end - start
    print_as_markdown(rep, "Elapsed time: {:.2f} secs".format(elapsed), "item")
    return elapsed


def load_docs():
    docs = []
    with open('scenarios.yaml', 'r') as f:
        config = yaml.load_all(f)
        for item in config:
            doc = {'name': item['name'],
                   'command': item['command'], 'class': item['class']}
            docs.append(doc)
    return docs


def main(iterations, report_dir, site):
    rep_name = normpath(join(report_dir, 'report.md'))
    csv_name = normpath(join(report_dir, 'result.csv'))

    docs = load_docs()

    with open(rep_name, 'w') as rep_file, open(csv_name, 'w') as csv_file:
        print_as_markdown(rep_file, "Starting detours scenarios tests", "title")
        wr = csv.writer(csv_file, quoting=csv.QUOTE_MINIMAL)
        csv_header = []
        # Write csv header
        for doc in docs:
            csv_header.append('{}-{}'.format(doc['name'], doc['class']))

        wr.writerow(csv_header)

        for i in range(iterations):
            print_as_markdown(rep_file, "Iteration {}".format(i + 1), "h3")
            csv_line = []
            for doc in docs:
                elapsed = execute_case(i + 1, doc, report_dir, rep_file, site)
                csv_line.append("{:.2f}".format(elapsed))
            wr.writerow(csv_line)


if __name__ == '__main__':
    try:
        iterations = sys.argv[1]
        report = sys.argv[2]
        site = sys.argv[3]
    except Exception:
        print("Usage: scenarios <iterations> <report_dir> <site>")
        sys.exit(2)
    else:
        rep = '{}/{:%Y%m%d_%Hh%Mm%Ss}'.format(report, datetime.now())
        rep_dir = Path(rep)
        if not rep_dir.exists():
            rep_dir.mkdir(parents=True)
        main(int(iterations), rep, site)
