import os
import sys
import subprocess
from github import Github, GithubException
import configparser
import re
import shutil
import csv


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_help():
    '''
    Print help describing the syntax for how to use the program.

    Parameters:
        - None

    Returns:
        - None
    '''
    usage = f"""\n python3 log2gradingtemplate.py [PATH] [classroom PREFIX] [CSV FILE]
    [PATH]: Grade box. 
    Needs to have two folders [PATH]/PASS, [PATH]/FAIL with log files
    [assignment prefix] assignment name in classroom (e.g., assignment-1-) 
    [CSV] Student CSV file collected from google forms >"""

    print(f"Usage: {usage}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print_help()
        sys.exit(1)

    project = sys.argv[1]
    githubprefix = sys.argv[2]
    studentcsv = sys.argv[3]
    project_dir = "{}".format(project)
    PASS_dir = "{}/PASS".format(project)
    FAIL_dir = "{}/FAIL".format(project)

    PASSFILE = open("PASS.md", "w")
    FAILFILE = open("FAIL.md", "w")

    if os.path.isdir(PASS_dir):
        for filename in os.listdir(PASS_dir):
            if filename.endswith(".log"):
                githubid = filename.replace(
                    githubprefix, "").replace(".log", "")
                with open(studentcsv) as csv_file:
                    result = {}
                    csv_reader = csv.DictReader(csv_file)
                    for row in csv_reader:
                        key = row.pop('GithubID')
                        result[key] = row
                    if githubid in result.keys():
                        entry = "### " + githubid + "\n" + " - Fill in feedback for SFUID {}".format(
                                result[githubid]['SFUID'])+"\n"
                        PASSFILE.write(entry)
                    else:
                        print(bcolors.WARNING + githubid +
                              " not found" + bcolors.ENDC)
    if os.path.isdir(FAIL_dir):
        for filename in os.listdir(FAIL_dir):
            if filename.endswith(".log"):
                githubid = filename.replace(
                    githubprefix, "").replace(".log", "")
                with open(studentcsv) as csv_file:
                    result = {}
                    csv_reader = csv.DictReader(csv_file)
                    for row in csv_reader:
                        key = row.pop('GithubID')
                        result[key] = row
                    if githubid in result.keys():
                        entry = "### " + githubid + "\n" + " - Fill in feedback for SFUID {}".format(
                                result[githubid]['SFUID'])+"\n"
                        FAILFILE.write(entry)
                    else:
                        print(bcolors.WARNING + githubid +
                              " not found" + bcolors.ENDC)

    PASSFILE.close()
    FAILFILE.close()
