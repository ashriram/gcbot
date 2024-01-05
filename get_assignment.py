import github2sfuid.sfuid2githubid as gs
import argparse


contents = []

parser = argparse.ArgumentParser()

parser.add_argument("-C", dest="sfuid",
                    help="CSV file containing map from github id to sfuid", required=True)

parser.add_argument("-A", dest="assignment",
                    help="Assignment", required=True)

opts = parser.parse_args()
id_file = opts.sfuid
gs.fillmap(id_file)
id = 0
while id != -1:
    id = input("Enter sfu id: ")
    if gs.getgithubid(id):
        githubid = gs.getgithubid(id)["GithubID"]
        print(f"https://github.com/CMPT-295-SFU/{opts.assignment}-{githubid}/actions/")
    else:
        print("Not found")



