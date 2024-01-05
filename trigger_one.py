import os
import sys
import subprocess
from github import Github, GithubException, Repository
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
    repo = g.get_repo("SFU-CMPT-300/TestCI")
    repo.create_repository_dispatch("grading")
    print(repo.name)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print_help()
        sys.exit(1)

    action = sys.argv[1]
    if "--organization=" in sys.argv[2] or "-o=" in sys.argv[2]:
        organization = sys.argv[2].split("=")[1]
        project = sys.argv[3]
    else:
        if len(sys.argv) > 3:
            print_help()
            sys.exit(1)
        project = sys.argv[2]
        organization = None

    if action == "run-remote":
        track_matching(project, organization)
    else:
        print_help()
