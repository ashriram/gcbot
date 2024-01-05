#!/usr/bin/env python3

import os
import sys
import subprocess
from github import Github, GithubException
import configparser
import re
import shutil
import requests
import pathlib
from pathlib import Path
import datetime
import subprocess
import json

import argparse
# Try to get it from system environment variable (On Linux/macOS you have to create it on $HOME/.bash_profile or .bashrc)
_key = os.environ.get('GIT_TOKEN', None)
_parent = os.environ.get('PARENT_REPO', None)
_run_remote_password = ""
# If you are not using environment variable, then try to get GITHUB TOKEN KEY from config.ini file.
if _key is None:
    ''' On 'config.ini' file
    [DEFAULT]
    KEY = Your API KEY
    '''
    _config_parser = configparser.ConfigParser()
    _config_parser.read('config.ini')
    _key = _config_parser['DEFAULT']['KEY']
    if 'MOSS_FILES' in _config_parser['DEFAULT'].keys():
        _FILES = _config_parser['DEFAULT']['MOSS_FILES'].split(',')
    if 'PARENT_REPO' in _config_parser['DEFAULT'].keys():
        _parent = _config_parser['DEFAULT']['PARENT_REPO']
    if 'RUN_REMOTE_PASSWORD' in _config_parser['DEFAULT'].keys():
        _run_remote_password = _config_parser['DEFAULT']['RUN_REMOTE_PASSWORD']

GIT_CONFIG = {
    'key': _key,
    # Set name of owner and TAs,
    'owners': {
        "ashriram",
        "abdelrahmanhussein",
        "alaa",
        "fshok",
        "alaa-alameldeen",
        "DarkMarshal77",
        "SediRzm",
        "mhezarei",
        "marzieh-barkhordar"
    },

    'grading_file': "GRADING.md",

    'moss_files': _FILES,

    'passed': 'Result: PASS',

    'failed': 'Result: FAIL',

    'run_remote_password': _run_remote_password
}


def print_help():
    '''
    Print help describing the syntax for how to use the program.

    Parameters:
        - None

    Returns:
        - None
    '''
    usage = f"{sys.argv[0]} <action> [--organization/-o=<org>]"
    print(f"Usage: {usage}")
    print("Available actions:")
    print("    update-from-template (if starter repo is a template)")
    print("    update-from-fork (if starter repo is a fork)")
    print("    ls (list) ")
    print("    push-comment")
    print("    moss")
    print("    push-pass-fail")
    print("    clone")
    print("    cancel-remote")
    print("    set_readonly")
    print("    set_write")
    print("    set_remove")
    print("    push-grade-sheet")
    print("    run-local")
    print("    run-remote")
    print("    add-commit")
    print("    force-remove-runners")


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


def git_add_commit_push(result, cwd, commit_msg):
    '''
    Adds, commits and pushes file to remote.

    Parameters:
        - Result of the file to be added to the repo and pushed
        - Cwd is the directory path of the repo where the file is located

    Returns:
        - None
    '''
    commit_msg = commit_msg.format(result)
    subprocess.run(["git", "add", result], cwd=cwd)
    subprocess.run(["git", "commit", "-m", commit_msg], cwd=cwd)
    subprocess.run(["git", "push"], cwd=cwd)


def git_pull_template_commit(parent, cwd):
    '''
    Adds, commits and pushes file to remote.

    Parameters:
        - Result of the file to be added to the repo and pushed
        - Cwd is the directory path of the repo where the file is located

    Returns:
        - None
    '''
    subprocess.run(["git", "remote", "add", "template", parent], cwd=cwd)
    subprocess.run(
        ["git", "fetch", "--all"], cwd=cwd)
    subprocess.run(["git", "merge", "template/master",
                    "--allow-unrelated-histories"], cwd=cwd)
    subprocess.run(["git", "add", "."], cwd=cwd)
    subprocess.run(
        ["git", "commit", "-am", "Pulling changes from forked master"], cwd=cwd)
    subprocess.run(["git", "push"], cwd=cwd)


def git_pull_fork_commit(parent, cwd):
    '''
    Adds, commits and pushes file to remote.

    Parameters:
        - Result of the file to be added to the repo and pushed
        - Cwd is the directory path of the repo where the file is located

    Returns:
        - None
    '''
    subprocess.run(["git", "pull", parent, "master"], cwd=cwd)
    subprocess.run(["git", "add", "."], cwd=cwd)
    subprocess.run(
        ["git", "commit", "-am", "Pulling changes from forked master"], cwd=cwd)
    subprocess.run(["git", "push"], cwd=cwd)


def parse_markdown_grading_sheeet(filename):
    '''
    Parses a markdown file for names and matches them with comments.

    Parameters:
        - Filename of the markdown file to be parsed

    Returns:
        - Dictionary where keys are student names and values are comments
        - None if a non-markdown file was provided

    '''
    if ".md" not in filename:
        return None

    grading_sheet = dict()
    student_name = None
    student_content = ""

    with open(filename, "r") as markdown_file:
        for line in markdown_file:
            # New student, so add previous student to dict
            if line.startswith("### "):
                if student_name is not None:
                    grading_sheet[student_name] = student_content
                student_name = line.strip("# \n")
                student_content = line
            # Same student, concatenate content
            else:
                student_content = student_content + line

        grading_sheet[student_name] = student_content

    return grading_sheet


def add_commit_push_grading_sheet():
    '''
    Parses a markdown file for names, matches them to the specific students,
    writes the comment to a file, adds and commits it to the repo before
    pushing it to remote.

    Promts the user for the filename of the grading sheet.
    Can only be used to parse a markdown file where the comments are on the
    following format:

    # student-github-name
    - comments
    - more comments

    # new-student-name

    The important thing is not the format of the comments, though they should
    be markdown as well, but that each student name, and only student names
    start with ### and that no comments contain ###.

    Parameters:
        - None

    Returns:
        - None
    '''
    filename = input("Enter path to sheet filename: ")
    grading_sheet = parse_markdown_grading_sheeet(filename)
    if grading_sheet is None:
        print(f"{filename} is not a markdown file: it must end in .md")

    project_dir = "{}/{}".format(os.getcwd(), project)
    repos = os.listdir(project_dir)
    result = GIT_CONFIG['grading_file']

    for repo in repos:
        repo_dir = "{}/{}".format(project_dir, repo)
        if os.path.isdir(repo_dir):
            # Try and find a student name matching the repo name
            found_student = False
            for student_name in grading_sheet.keys():
                if repo.endswith(student_name):
                    found_student = True
                    print(f"Assuming {repo} belongs to {student_name}: "
                          "adding grading comment")
                    with open(f"{repo_dir}/{result}", "w+") as f:
                        f.write(grading_sheet[student_name])
                    break

            if found_student:
                git_add_commit_push(
                    result, repo_dir, 'Graded project, see the {}-file in the root directory'.format(result))
                print("Pushed changes to github")
            else:
                print(f"Found no student matching repo name {repo}")


def add_commit_push(project, comment):
    '''
    Adds a file, commits it and pushed to the git repos
    which are present in a project directory.

    Can be used to specify if a student has passed or failed, or to provide
    a comment interactively.

    Parameters:
        - Project which should match the name of the sub-directory containing
          the git repositories which should be added, committed and pushed to.
        - Comment parameter determines if the commit should be a comment or not

    Returns:
        - None
    '''
    if not comment:
        passed = GIT_CONFIG['passed']
        failed = GIT_CONFIG['failed']

    project_dir = "{}/{}".format(os.getcwd(), project)
    repos = os.listdir(project_dir)
    for repo in repos:
        repo_dir = "{}/{}".format(project_dir, repo)
        if os.path.isdir(repo_dir):
            if not comment:
                inp = input(f"Did {repo} 'pass' or 'fail'? [Default: pass]: ")
                if inp == "fail":
                    result = failed
                elif inp == "skip":
                    continue
                else:
                    result = passed
                text = ""
            else:
                result = GIT_CONFIG['grading_file']
                print(f"\nGrading {repo} - enter grading comment:")
                text = sys.stdin.read()

            with open(f"{repo_dir}/{result}", "w+") as f:
                f.write(text)

            git_add_commit_push(
                result, repo_dir, 'Graded project, see the {}-file in the root directory'.format(result))
            print("Pushed changes to github")
        else:
            print(f"\n{repo} is not a directory, and can't be a repo")


def moss(project, comment):
    '''
    Obtain a file, and set it up in the appropriate student directory

    Parameters:
        - Project which should match the name of the sub-directory containing
          the git repositories which should be added, committed and pushed to.
        - Comment parameter determines if the commit should be a comment or not

    Returns:
        - None
    '''
    os.mkdir("Mossbox")
    project_dir = "{}/{}".format(os.getcwd(), project)
    repos = os.listdir(project_dir)
    for repo in repos:
        repo_dir = "{}/{}".format(project_dir, repo)
        print(repo_dir)
        if os.path.isdir(repo_dir):
            githubid = repo.replace(project+"-", "")
            studentdir = os.path.join(os.getcwd()+"/Mossbox/"+githubid)
            os.mkdir(studentdir)
            for root, dir, files in os.walk(repo_dir):
                for file in files:
                    if file in _FILES:
                        shutil.copy(os.path.join(root, file), studentdir)
                        print(file)
        else:
            print(f"\n{repo} is not a directory, and can't be a repo")


def getmarks(json_dict):
    points = 0
    for k,v in json_dict.items():
        if k != "userid":
            points += int(v['mark'])
    return points

def compile_check(project):
    '''
    Obtain a file, and set it up in the appropriate student directory

    Parameters:
        - Project which should match the name of the sub-directory containing
          the git repositories which should be added, committed and pushed to.
        - Comment parameter determines if the commit should be a comment or not

    Returns:
        - None
    '''
    project_dir = "{}/{}".format(os.getcwd(), project)
    repos = os.listdir(project_dir)
    check_file = open("compile_check.txt", "w")
    for repo in repos:
        repo_dir = "{}/{}".format(project_dir, repo)
        print(repo_dir)
        if os.path.isdir(repo_dir):
            githubid = repo.replace(project+"-", "")
            #studentdir = os.path.join(os.getcwd()+"/Mossbox/"+githubid)
            # os.mkdir(studentdir)
            points = 0
            ASS = "{}/{}".format(os.getcwd(), "ASS1")
            if os.path.exists(ASS+f"/FAIL/{repo}_Grade.json"):
                f = open(ASS+f"/FAIL/{repo}_Grade.json")
                points = getmarks(json.load(f))
            if os.path.exists("ASS1/PASS/"+repo+"_Grade.json"):
                f = open(ASS+f"/PASS/{repo}_Grade.json")
                points = getmarks(json.load(f))
            for root, dir, files in os.walk(repo_dir):
                Errors = ""
                for file in files:
                    if file in _FILES:
                        ppath = os.path.join(root,"")
                        p = subprocess.Popen(f"clang -Wall -c -I include/ -I ../include -o /tmp/1.o {file}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=ppath)
                        out, err = p.communicate()
                        lines = err.decode("utf-8")
                        list = lines.split("\n")
                        for l in list:
                            # Check their score. If score greater than x then validate.
                            if "non-void function does not return a value" in l:
                                if points >= 0:
                                    links = l.split(":")
                                    relpath = os.path.relpath(ppath+file, repo_dir)
                                    url = f"https://github.com/CMPT-295-SFU/{repo}/blob/master/{relpath}?plain=1#L{links[1]}"
                                    #Errors += f"\n{repo}:{l}"
                                    Errors += f"\n{url}"
                        #shutil.copy(os.path.join(root, file), studentdir)
  #                              print(file)
                if Errors != "":
                    print(f"\n############### {repo} {points} ###############", file=check_file)
                    print(Errors, file = check_file)
                    print("\n############### END ###############", file = check_file)
        else:
            print(f"\n{repo} is not a directory, and can't be a repo")




def run(project):
    '''
    Obtain a file, and set it up in the appropriate student directory.
    Run project.
    Parameters:
        - Project which should match the name of the sub-directory containing
          the git repositories which should be added, committed and pushed to.

    Returns:
        - None
    '''
    if os.path.exists("./ASS_ROOT") and os.path.isdir("./ASS_ROOT"):
        print("Removing ASS_ROOT")
        shutil.rmtree("./ASS_ROOT")

    pathlib.Path('./ASS_ROOT/PASS').mkdir(parents=True)
    pathlib.Path('./ASS_ROOT/FAIL').mkdir(parents=True, exist_ok=True)
    PASS_DIR = "{}/{}".format(os.getcwd(), "ASS_ROOT/PASS")
    FAIL_DIR = "{}/{}".format(os.getcwd(), "ASS_ROOT/FAIL")

    project_dir = "{}/{}".format(os.getcwd(), project)
    repos = os.listdir(project_dir)
    for repo in repos:
        repo_dir = "{}/{}".format(project_dir, repo)
#        print(repo_dir)
        if os.path.isdir(repo_dir):
            if (os.path.isfile(repo_dir + "/scripts/localci.sh")):
                subprocess.run(
                    ["bash", repo_dir + "/scripts/localci.sh"], cwd=repo_dir)
                # Check for success of failure
                if (os.path.isfile(repo_dir+"/FAILED")):
                    shutil.copy(repo_dir+"/"+os.path.basename(repo_dir) +
                                ".log.failed", FAIL_DIR + "/" + os.path.basename(repo_dir) + ".log")
                    shutil.copy(repo_dir+"/"+os.path.basename(repo_dir) +
                                "_Grade.json", FAIL_DIR+"/"+os.path.basename(repo_dir) +
                                "_Grade.json")
                if (os.path.isfile(repo_dir+"/SUCCESS")):
                    shutil.copy(repo_dir+"/"+os.path.basename(repo_dir) +
                                ".log.success", PASS_DIR + "/" + os.path.basename(repo_dir) + ".log")
                    shutil.copy(repo_dir+"/"+os.path.basename(repo_dir) +
                                "_Grade.json", PASS_DIR+"/"+os.path.basename(repo_dir) +
                                "_Grade.json")
            else:
                print("localci.sh does not exist in repo")
        else:
            print(f"\n{repo} is not a directory, and can't be a repo")


def add_commit_push_all(project):
    '''
    To be used in conjunction with run
    Adds all files, commits it and pushed to the git repos
    which are present in a project directory.

    Parameters:
        - Project which should match the name of the sub-directory containing
          the git repositories which should be added, committed and pushed to.
        - Comment parameter determines if the commit should be a comment or not

    Returns:
        - None
    '''

    project_dir = "{}/{}".format(os.getcwd(), project)
    repos = os.listdir(project_dir)
    for repo in repos:
        repo_dir = "{}/{}".format(project_dir, repo)
        if os.path.isdir(repo_dir):
            git_add_commit_push(
                "*", repo_dir, 'Added everything. Typically after a local run.')
            print("Pushed changes to github")
        else:
            print(f"\n{repo} is not a directory, and can't be a repo")


def pull_template_commit(project, parent, istemplate):
    '''
    ***WARNING*** Works only if there are no merge conflicts
    Pulls updates from parent fork commits it and pushed to the git repos
    which are present in a project directory.

    Can be used to push updates to the assignment.

    Parameters:
        - Project which should match the name of the sub-directory containing
          the git repositories which should be added, committed and pushed to.

    Returns:
        - None
    '''

    project_dir = "{}/{}".format(os.getcwd(), project)
    repos = os.listdir(project_dir)
    for repo in repos:
        repo_dir = "{}/{}".format(project_dir, repo)
        if os.path.isdir(repo_dir):
            if (istemplate):
                git_pull_template_commit(parent, repo_dir)
            else:
                git_pull_fork_commit(parent, repo_dir)
            print("Pushed changes to github")
        else:
            print(f"\n{repo} is not a directory, and can't be a repo")


def list_matching(project, organization):
    '''
    Lists the repositories matching the provided project and organization.

    Parameters:
        - Project name to be queried (repo name should contain this)
        - Organization name which should own the repo (if any)

    Returns:
        - None
    '''
    g = Github(GIT_CONFIG['key'])
    for repo in g.get_user().get_repos():
        if is_matching(repo, project, organization):
            print(repo.name)


def set_matching_readonly(project, organization, push_or_pull):
    '''
    Sets the matching repositories to read-only for all non-owners.
    Can be used to revoke students' write permissions.

    PS: Will ONLY work if the github library is modified.
        See github.com/NikolaiMagnussen/pygithub.

    Parameters:
        - Project name to be queried (repo name should contain this)
        - Organization name which should own the repo (if any)

    Returns:
        - None
    '''
    g = Github(GIT_CONFIG['key'])
    for repo in g.get_user().get_repos():
        if is_matching(repo, project, organization):
            print("Changing permissions for {}".format(repo.name))
            for collab in repo.get_collaborators():
                if collab.login not in GIT_CONFIG['owners']:
                    # Student found. change permissions from push to pull
                    # repo.remove_from_collaborators(collab)
                    try:
                        repo.add_to_collaborators(collab, push_or_pull)
                        print(f"{format(collab.login)} can only {push_or_pull}")
                    except GithubException as e:
                        print(e)
                        repo.add_to_collaborators(collab)
                        print("    {} can still write because readonly is only"
                              " possible in orgs".format(collab.login))
                else:
                    print("    Owner: {}".format(collab.login))


def set_matching_remove(project, organization, push_or_pull):
    '''
    Sets the matching repositories to read-only for all non-owners.
    Can be used to revoke students' write permissions.

    PS: Will ONLY work if the github library is modified.
        See github.com/NikolaiMagnussen/pygithub.

    Parameters:
        - Project name to be queried (repo name should contain this)
        - Organization name which should own the repo (if any)

    Returns:
        - None
    '''
    g = Github(GIT_CONFIG['key'])
    for repo in g.get_user().get_repos():
        if is_matching(repo, project, organization):
            print("Changing permissions for {}".format(repo.name))
            for collab in repo.get_collaborators():
                if collab.login not in GIT_CONFIG['owners']:
                    # Student found. change permissions from push to pull
                    try:
                        repo.remove_from_collaborators(collab)
                        print(f"{format(collab.login)} can no longer access")
                    except GithubException as e:
                        print(e)
                        repo.add_to_collaborators(collab)
                        print("    {} can still write because readonly is only"
                              " possible in orgs".format(collab.login))
                else:
                    print("    Owner: {}".format(collab.login))


def clone_matching(project, organization):
    '''
    Clone the matching repositories to a project directory.

    Parameters:
        - Project name to be queried (repo name should contain this)
        - Organization name which should own the repo (if any)

    Returns:
        - None
    '''
    project_dir = "{}/{}".format(os.getcwd(), project)
    g = Github(GIT_CONFIG['key'])
    for repo in g.get_user().get_repos():
        if is_matching(repo, project, organization):
            if not os.path.isdir(project_dir):
                os.mkdir(project_dir)
            split_idx = repo.clone_url.find("github.com")
            repo_url = "{}{}@{}".format(repo.clone_url[:split_idx],
                                        GIT_CONFIG['key'],
                                        repo.clone_url[split_idx:])
            subprocess.run(["git", "clone", "--depth", "1", repo_url], cwd=project_dir)


def run_remote(project, organization):
    '''
    Trigger remote run of repository.
    Parameters:
        - Project name to be queried (repo name should contain this)
        - Organization name which should own the repo (if any)

    Returns:
        - None
    '''
    project_dir = "{}/{}".format(os.getcwd(), project)
    g = Github(GIT_CONFIG['key'])
    for repo in g.get_user().get_repos():
        if is_matching(repo, project, organization):
            print(repo.name)
            client_payload = {}
            client_payload["password"] = GIT_CONFIG["run_remote_password"]
            repo.create_repository_dispatch("grading", client_payload)


def cancel_remote(project, organization):
    '''
    Trigger remote run of repository.
    Parameters:
        - Project name to be queried (repo name should contain this)
        - Organization name which should own the repo (if any)

    Returns:
        - None
    '''
    project_dir = "{}/{}".format(os.getcwd(), project)
    g = Github(GIT_CONFIG['key'])
    for repo in g.get_user().get_repos():
        if is_matching(repo, project, organization):
            runs = repo.get_workflow_runs()
            for run in runs:
                if (run.status != "completed"):
                    if run.cancel():
                        print(f"Cancelled run {repo.name}")


def run_remote_status(project, organization):
    '''
    Get status of latest remote runs
    Parameters:
        - Project name to be queried (repo name should contain this)
        - Organization name which should own the repo (if any)

    Returns:
        - None
    '''
    project_dir = "{}/{}".format(os.getcwd(), project)
    g = Github(GIT_CONFIG['key'])
    all_jobs = 0
    for repo in g.get_user().get_repos():
        if is_matching(repo, project, organization):
            print(repo.name)
            runs = repo.get_workflow_runs()
            push_runs = [item for item in runs if item.event == "push"]
            repository_runs = [
                item for item in runs if item.event == "repository_dispatch"]
#            push_runs.sort(key=lambda x: x.created_at)
#            repository_runs.sort(key=lambda x: x.created_at)
            queued = 0
            if push_runs:
                latest_run = max(push_runs, key=lambda x: x.created_at)
                print(latest_run.event, latest_run.created_at,
                      latest_run.conclusion, latest_run.status)

            if repository_runs:
                latest_run = max(repository_runs, key=lambda x: x.created_at)
                print(
                    latest_run.event, latest_run.created_at, latest_run.conclusion, latest_run.status)
            incomplete = [x for x in push_runs if x.status != "completed"]
            incomplete.extend(
                [x for x in repository_runs if x.status != "completed"])

            if incomplete:
                number_of_incomplete_jobs = len(incomplete)
                all_jobs = all_jobs + number_of_incomplete_jobs
                print(f"{number_of_incomplete_jobs} jobs pending")
            else:
                print("0 jobs pending")
    print(f"Total:{all_jobs} pending")

def force_remove_runners(organization):
    '''
    Removes runners forcibly; stop docker instances before invoking.
    Parameters
        - Organization name which should own the repo (if any)
    Returns:
        - None
    '''

    auth_token = format(GIT_CONFIG['key'])
    headers = {
    'accept': 'application/vnd.github.everest-preview+json',
    'authorization': f'token {auth_token}',
    }
    params = (
    ('per_page', '100'),
    )

    response = requests.get(f'https://api.github.com/orgs/{organization}/actions/runners', headers=headers, params=params)

    for r in response.json()['runners']:
        print("Removing runner:" + r['name'] + " with id:" + str(r['id']))
        headers = {
        'authorization': f'token {auth_token}',
        }
        runner_id = r['id']
        response = requests.delete(f'https://api.github.com/orgs/{organization}/actions/runners/{runner_id}', headers=headers, params=params)

 #   print(response.json())
    
#    curl -s -X DELETE ${base_api_url}/${runner_scope}/actions/runners/${runner_id} -H "authorization: token ${RUNNER_CFG_PAT}"

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices =    ["update-from-template",
    "update-from-fork",
    "ls",
    "push-comment",
    "push-pass-fail",
    "clone",
    "cancel-remote",
    "set_readonly",
    "set_write",
    "set_remove",
    "push-grade-sheet",
    "moss",
    "run-local",
    "run-remote",
    "run-remote-status",
    "add-commit",
    "force-remove-runners",
    "compile-check"
    ], help= "")
    parser.add_argument('assignment', help= "Github classroom assignment prefix (e.g., assignment-1- . Pay attention to the - at the end)")
    parser.add_argument('-o','--organization', help= "github organization", required=True)

    args = parser.parse_args()
    action = args.action
    project = args.assignment
    organization = args.organization
    # if len(sys.argv) < 3:
    #     print_help()
    #     sys.exit(1)

    # action = sys.argv[1]
    # if "--organization=" in sys.argv[2] or "-o=" in sys.argv[2]:
    #     organization = sys.argv[2].split("=")[1]
    #     project = sys.argv[3]
    # else:
    #     if len(sys.argv) > 3:
    #         print_help()
    #         sys.exit(1)
    #     project = sys.argv[2]
    #     organization = None
    # if organization is None:
    #     print("Set organization -o=<organization>")
    #     sys.exit(0)

    if action == "ls":
        list_matching(project, organization)
    elif action == "clone":
        clone_matching(project, organization)
    elif action == "run-remote":
        print("Are you sure you trigger remote runs for respositories. This may dump data to remote folder. Make sure you clean folder before running.")
        print("Type 'YES' to confirm")
        ans = input()
        if ans == "YES":
            run_remote(project, organization)
    elif action == "cancel-remote":
        print("Are you sure you want to CANCEL all remote runs for repositories. THIS WILL STOP ALL RUNS")
        print("Type 'YES' to confirm")
        ans = input()
        if ans == "YES":
            cancel_remote(project, organization)
    elif action == "run-remote-status":
        run_remote_status(project, organization)
    elif action == "set_readonly":
        print("Are you sure you want to set all non-owners of the matching "
              "repos to read-only?" + "Assignment: " + project + "Organization:" + organization)
        print("Type 'YES' to confirm")
        ans = input()
        if ans == "YES":
            set_matching_readonly(project, organization, "pull")
    elif action == "set_write":
        print("Are you sure you want to set all non-owners of the matching "
              "repos to write?")
        print("Type 'YES' to confirm")
        ans = input()
        if ans == "YES":
            set_matching_readonly(project, organization, "push")
    elif action == "set_remove":
        print(
            "WARNING: Are you sure you want to remove all non-owners of the matching. YOU CANNOT RECOVER FROM THIS")
        print("Type 'YES' to confirm")
        ans = input()
        if ans == "YES":
            set_matching_remove(project, organization, "remove")
    elif action == "push-pass-fail":
        if organization is not None:
            print("Organization does not affect pushing")
        add_commit_push(project, comment=False)
    elif action == "push-comment":
        if organization is not None:
            print("Organization does not affect pushing")
        add_commit_push(project, comment=True)
    elif action == "moss":
        if organization is not None:
            print("Organization does not affect mossing")
        moss(project, comment=True)
    elif action == "compile-check":
        compile_check(project)
    elif action == "update-from-template":
        if organization is not None:
            print("Organization does not affect pushing")
        pull_template_commit(project, _parent, True)
    elif action == "update-from-fork":
        if organization is not None:
            print("Organization does not affect pushing")
        pull_template_commit(project, _parent, False)
    elif action == "push-grade-sheet":
        if organization is not None:
            print("Organization does not affect pushing")
        add_commit_push_grading_sheet()
    elif action == "run-local":
        if organization is not None:
            print("Organization does not affect mossing")
        run(project)
    elif action == "add-commit":
        if organization is not None:
            print("Organization does not affect commit")
        add_commit_push_all(project)
    elif action == "force-remove-runners":
        print("Are you sure you want force remove runners for" + "Organization:" + organization + " (YES/NO)")
        ans = input()
        if ans == "YES":
            force_remove_runners(organization)
    else:
        print_help()
