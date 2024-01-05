#!/usr/bin/env python3

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


github_sfu_dict = {}


def fillmap(csv_file):
    with open(csv_file) as studentcsv:
        csv_reader = csv.DictReader(studentcsv)
        for row in csv_reader:
            key = row.pop('GithubID')
            github_sfu_dict[key] = row


# Try to get it from system environment variable (On Linux/macOS you have to create it on $HOME/.bash_profile or .bashrc)
_key = os.environ.get('GIT_GUD_TOKEN', None)
_parent = os.environ.get('PARENT_REPO', None)

# If you are not using environment variable, then try to get GITHUB TOKEN KEY from config.ini file.
if _key is None:
    ''' On 'config.ini' file
    [DEFAULT]
    KEY = Your API KEY
    '''
    _config_parser = configparser.ConfigParser()
    _config_parser.read('config.ini')
    _key = _config_parser['DEFAULT']['KEY']

GIT_GUD_CONFIG = {
    'key': _key
}


def print_sfu_email(githubid):
    if (githubid in github_sfu_dict.keys()):
        print(github_sfu_dict[githubid]["SFUID"]+"@sfu.ca"+"," + githubid)
    else:
        print(bcolors.WARNING + githubid +
              " not found" + bcolors.ENDC)


def print_help():
    '''
    Print help describing the syntax for how to use the program.

    Parameters:
        - None

    Returns:
        - None
    '''
    usage = f"{sys.argv[0]} <action> [--organization/-o=<org>] <search string>"
    print(f"Usage: {usage}")
    print("Available actions:")
    print("    track-commits")


def is_matching(repo, project, organization):
    '''
    Check if a repo matches with a project and potential organization
    If an organization is provided, make sure the repo is owned by it,
    and that the project name is in the repo name. If an organization is
    not provided, simply make sure the project matches.

    Parameters:
        - Repo which is the repository queried from github
        - Project name to be queried (repo name should contain this)
        - Organization name which should own the repo

    Returns:
        - True if repo matches project and organization provided
        - False if otherwise
    '''
    if organization:
        if project in repo.name and organization == repo.owner.login:
            return True
    else:
        if project in repo.name:
            return True

    return False


def track_matching(project, organization):
    '''
    Lists the repositories matching the provided project and organization.

    Parameters:
        - Project name to be queried (repo name should contain this)
        - Organization name which should own the repo (if any)

    Returns:
        - None
    '''
    g = Github(GIT_GUD_CONFIG['key'])
    students_with_repos = set()
    students_with_LT5 = set()
    for repo in g.get_user().get_repos():
        if is_matching(repo, project, organization):
            #            print(repo.name, repo.get_commits().totalCount)
            githubid = repo.name.replace(project, "")
            students_with_repos.add(githubid)
            if (repo.get_commits().totalCount >= 5):
                students_with_LT5.add(githubid)
    allstudents = github_sfu_dict.keys()
    students_without_repos = set(
        allstudents).difference(students_with_repos)
    print("Students with lots of commits")
    [print_sfu_email(x) for x in students_with_LT5]


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print_help()
        sys.exit(1)

    action = sys.argv[1]
    studentfile = sys.argv[4]
    if "--organization=" in sys.argv[2] or "-o=" in sys.argv[2]:
        organization = sys.argv[2].split("=")[1]
        project = sys.argv[3]
    else:
        if len(sys.argv) > 3:
            print_help()
            sys.exit(1)
        project = sys.argv[2]
        organization = None

    fillmap(sys.argv[4])

    if action == "track-commits":
        track_matching(project, organization)
    else:
        print_help()
