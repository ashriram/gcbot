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
            key = row.pop('SFUID')
            github_sfu_dict[key] = row


def getgithubid(sfuid):
    if sfuid in github_sfu_dict:
        return github_sfu_dict[sfuid]

    return None
