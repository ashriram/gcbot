#!/usr/bin/env python3

import os
import sys
import subprocess
import configparser
import re
import shutil
import csv

github_sfu_dict = {}


def fillmap(csv_file):
    with open(csv_file) as studentcsv:
        csv_reader = csv.DictReader(studentcsv)
        for row in csv_reader:
            key = row.pop('GithubID')
            github_sfu_dict[key] = row


def getsfuid(githubid):
    if githubid in github_sfu_dict:
        return github_sfu_dict[githubid]

    return None
