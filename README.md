# Github Classroom Assistant

## Author

Arrvindh Shriraman. 
Tool was derived from  **_ Nikolai Magnussen _**


## Dependencies (miniconda)

```bash
pip3 install --user -r pygithub
```

- A GitHub Personal Access Token
- Python3
- GitHub library for Python3


### Generating GitHub Token

To use the GitHub Classroom Assistant, you need to generate a personal access token on GitHub. Follow these steps:

1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens).
2. Click on "Generate new token".
3. Give your token a descriptive name and select the necessary scopes.
4. Click on "Generate token" to create the token.
5. Copy the generated token and paste it into the `config.ini` file.

### Student CSV File

The Student CSV file is collected using a Google Form to match GitHub IDs with SFU IDs. It contains the following columns:

- First: First name
- Last: Last name
- SFUID: SFU ID (username)
- SFUNUMBER: SFU Number
- GithubID: GitHub ID
- Slot: [Optional]. For managing multi-slot midterm exams

```bash
$ cat Students.csv
First,Last,SFUID,SFUNUMBER,GithubID,Slot
John,Doe,123456789,123456789,johndoe,1%
First - First name
Last - Last name
SFUID - SFU ID (username)
SFUNUMBER - SFU Number
GithubID - Github ID
Slot - [Optional]. For managing multi-slot midterm exams
```


## Features

- [Github Classroom Assistant](#github-classroom-assistant)
  - [Author](#author)
  - [Dependencies (miniconda)](#dependencies-miniconda)
    - [Generating GitHub Token](#generating-github-token)
    - [Student CSV File](#student-csv-file)
  - [Features](#features)
    - [Repository Search (ls)](#repository-search-ls)
    - [Mass Clone (clone)](#mass-clone-clone)
    - [Set Student Access Read Only or Write (set\_readonly or set\_write)](#set-student-access-read-only-or-write-set_readonly-or-set_write)
    - [Interactive PASS/FAIL grading without comment (push-pass-fail)](#interactive-passfail-grading-without-comment-push-pass-fail)
    - [Interactive comments (push-comment)](#interactive-comments-push-comment)
    - [Batch comments using a Markdown document (push-grade-sheet)](#batch-comments-using-a-markdown-document-push-grade-sheet)
    - [Add commit](#add-commit)
    - [Set up Moss (moss)](#set-up-moss-moss)
      - [Clone all repos](#clone-all-repos)
      - [Create moss config.](#create-moss-config)
      - [Run Moss and create html](#run-moss-and-create-html)
    - [run-local (requires scipts/run.sh in the repository)](#run-local-requires-sciptsrunsh-in-the-repository)
    - [add-commit-push](#add-commit-push)
  - [Update from template or fork](#update-from-template-or-fork)
  - [Notes:](#notes)
    - [Interaction with remote github actions](#interaction-with-remote-github-actions)
- [Git Student Tracker](#git-student-tracker)
  - [Dependencies](#dependencies)

### Repository Search (ls)

Github classroom repository prefixes are set by the instructor. They are typically of the form assignment-x-githubid. This tool allows you to search for repositories that match a pattern. For example, if you want to search for all repositories that start with assignment-x- and are in the organization CMPT-295-SFU, you would run the following command:

```
python3.6 ./gcassist.py ls -o=CMPT-295-SFU sfu431-assignment-x-
```

- Fuzzy matching on repository names
- Ability to specify a GitHub organization if you have multiple assignments that are named the same, but in different organizations and you don’t want both
- Is very practical to use before cloning to make sure you do not clone repositories that should not be cloned

### Mass Clone (clone)

- Fuzzy matching on repository names
- Ability to specify a GitHub organization if you have multiple assignments that are named the same, but in different organizations and you don’t want both
- Clones all matching repositories into a directory matching the search string used when specifying which repositories to clone

```
python3 ./gcassist.py clone -o=CMPT-295-SFU assignment-x-
```

### Set Student Access Read Only or Write (set_readonly or set_write)

- It will go through all student repositories and set their access to read only or write
- This is useful if you want to prevent students from pushing to their repositories after a deadline
- It will set access to readonly for all users not listed in the script
- It will set access to write for user listed as owning the assignment assignment-x-[githubid]

```bash
python3 ./gcassist.py set_readonly -o=CMPT-295-SFU assignment-x-
python3 ./gcassist.py set_write -o=CMPT-295-SFU assignment-x-
```

### Interactive PASS/FAIL grading without comment (push-pass-fail)

- Uses the local directory of previously mass cloned repositories
- It will go through all student repositories and prompt you for PASS or FAIL, with PASS being default
- After specifying whether the submission is PASSED or FAILED, it will automatically add, commit and push the grading file to remote (probably GitHub Classroom)

```bash
python3 ./gcassist.py ls -o=CMPT-295-SFU  assignment-x--
python3 ./gcassist.py clone -o=CMPT-295-SFU  assignment-x--
# Create grading.md
python3 ./gcassist.py push-pass-fail -o=CMPT-295-SFU assignment-x--
```

### Interactive comments (push-comment)

- Uses the local directory of previously mass cloned repositories
- It will go through all student repositories and prompt you for the feedback that should be provided, writing to the grading file until EOF is intered, allowing for multi-line feedback.
- After providing feedback to the student, it will automatically add, commit and push the grading file to remote (probably GitHub Classroom)

```bash
python3 ./gcassist.py ls -o=CMPT-295-SFU  assignment-x--
python3 ./gcassist.py clone -o=CMPT-295-SFU  assignment-x--
python3 ./gcassist.py push-comment -o=CMPT-295-SFU  assignment-x--
```

### Batch comments using a Markdown document (push-grade-sheet)

- Uses the local directory of previously mass cloned repositories as well as your feedback to all students in a Markdown document
- It will parse the markdown file, matching students with their feedback, and then match it with the repositories in the directory.
- The matched feedback is added to the student repository, committed and pushed to remote (probably GitHub Classroom)

Comment file

```markdown
 ### student-github-name
    - comments
    - more comments
    - comments can be any markdown (NO ### tags)
 ### Another student github-name
```

** STEP 1 : To generate a templated comment file AND FILL IT **

```bash
python3 log2gradingtemplate.py ./ASSX assignment-x-- Students.csv
# First parameter . Relative path to current directory assignment log files generated by CI scripts
# Second parameter - prefix used to name the assignment in github. Student repos will be of type prefix+githubid. The "-" at the end of the prefix is important
Student CSV file from Github reponse sheet.
```

This will create two files: PASS.md and FAIL.md. PASS.md contains template for all students that passed. FAIL.md is the template for all students that failed Fill these as you read the log files.

** STEP 2 : PUSH GRADING SHEETS INTO REPO (Fill coursys json entry as you do this) **

```
python3 ./gcassist.py ls -o=CMPT-295-SFU assignment-x--
python3 ./gcassist.py clone -o=CMPT-295-SFU assignment-x--
# For Pass.md. Fill comments in Pass.md. Every entry is student who passed. Includes both SFUID and GITHUB ID. Use SFU ID to access report from coursys. Assign scores for code and report.
# This will push GRADING.md
python3 ./gcassist.py push-grade-sheet -o=CMPT-295-SFU assignment-x--
# Fill comments in fail.md. Includes both SFUID and GITHUB ID. Use GITHUB ID to access log file in $ASS/FAIL. Use SFU ID to access report from coursys. Assign scores for code and report.
mv FAIL.md GRADING.md
python3 ./gcassist.py push-grade-sheet -o=CMPT-295-SFU assignment-x--
```

### Add commit

- Uses the local directory of previously mass cloned repositories
- It will go through all student repositories and add, commit and push changes to all repos.
- Useful when you want to manually propagate changes

```bash
$ python3 ./gcassist.py ls -o=CMPT-295-SFU assignment-x-
$ python3 ./gcassist.py clone -o=CMPT-295-SFU assignment-x-
$ python3 ./gcassist.py add-commit -o=CMPT-295-SFU assignment-x-
```

### Set up Moss (moss)

- Uses the local directory of previously mass cloned repositories
- It will go through all student repositories and pick up files specified in
  MOSS_FILES in config.ini (e.g., MOSS_FILES = overview.txt,PASS)

#### Clone all repos

`This is an interactive process.`
`You have to select the classroom and assignment`

- Replace ASS with assignment number e.g., assignment-x-


```bash
cd ~/TA/TA-tools
ORG=CMPT-295-SFU; ASS=assignment-[1-6]-; python3 ./gcassist.py clone $ASS -o=$ORG
```

#### Create moss config.

`WARNING: SET MOSS_FILES in config.ini to the contents of ASSX.moss" 

```bash
cd ~/TA/TA-tools
rm -rf Mossbox # Pay attention to case.
# Replace [1-6] with assignment number e.g., 1 (note no assignment)
python3 config.py config.ini [1-6]; mv config.ini.new config.ini
ORG=CMPT-295-SFU; ASS=assignment-[1-6]-; python3 ./gcassist.py moss $ASS -o=$ORG 
ls Moss/*
```

This will create a Mossbox/ (with a capital M)

#### Run Moss and create html

```bash
cd ~/TA/TA-tools
cd ../moss
perlbrew switch perl-5.10.1 # DO NOT RUN COMMAND IF ON cs-arch-srv03.cmpt.sfu.ca
# This will create a new shell if things worked ok.
perl ./moss.pl -d ../TA-tools/Mossbox/*/*
# If you see any errors wit CTime; ensure you have the appropriate perl dependencies installed.
# If you see any folder related errors. Check if TA-tools/Moss/[Repo]/ has any files
# If there are no files. Check if you set the file list in config.ini before running
# the previous step.
```



### run-local (requires scipts/run.sh in the repository)

- Uses the local directory of previously mass cloned repositories
- It will go through all student repositories and invoke scripts/run.sh using the repository as the current working directory
- generates a repo-name.success.log or repo-name.fail.log

**_ Dependencies ( repo/scripts/run.sh has to exist) _**

```bash
python3 ./gcassist.py clone -o=CMPT-295-SFU AssX-Graph- # all repos AssX-Graph*
python3 ./gcassist.py run -o=CMPT-295-SFU AssX-Graph- # Assumes AssX-Graph/ folder exists with repos in it
python3 ./gcassist.py add-commit-push -o=CMPT-295-SFU AssX-Graph- #  Pushes everything in that repo
python3 ./gcassist.py add-commit-push -o=CMPT-295-SFU AssX-Graph-
```

Each repo/ under AssX-Graph- will contain either a repo.log.success or repo.log.failed.files.
Lookover these files and then fill scores for coursys.

### add-commit-push

- Uses the local directory of previously mass cloned repositories
- Typically used after a run when logs have been generated

e.g., see above

## Update from template or fork

- Uses the local directory of previously mass cloned repositories
- Updates these repos with changes from PARENT_REPO

```
PARENT_REPO="[The release repo)]" python3 ./gcassist.py update-from-fork -o=CMPT-295-SFU assignment-x-
PARENT_REPO="[The release repo (has to be a template)]" python3 ./gcassist.py update-from-template -o=CMPT-295-SFU assignment-x-
```

## Notes:

- If a student has not been graded in the Markdown document, you will simply be notified that the student has not been provided any feedback in the Markdown document, and if you have graded students that are not cloned, their feedback will simply be ignored.
- The only rule for writing the feedback document is that heading the feedback for student “John Doe”, you must write the username of the student like so: “### JohnDoe” (assuming John Doe uses JohnDoe as is GitHub username).

### Interaction with remote github actions

You can set up custom self-hosted instances of github actions runners. These can be used to run tests on student code. The following commands are useful for managing these runners.


```bash
# Cancel remote github action runners triggered for a specific assignment.
$ python3 ./gcassist.py cancel-remote -o=CMPT-295-SFU assignment-x-
# run remote github action runners triggered for a specific assignment.
$ python3 ./gcassist.py run-remote -o=CMPT-295-SFU assignment-x-
# Force remove all runners. This is useful if you have a lot of runners that are stuck.
$ python3 ./gcassist.py force-remove-runners -o=CMPT-295-SFU assignment-x-
```

 

---

# Git Student Tracker

## Dependencies

Student list from google form.

```
python3 git_student_tracker.py track-commits -o=CMPT-295-SFU Students.csv
```




