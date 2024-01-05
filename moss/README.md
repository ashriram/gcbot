See comments at the beginning of moss.pl for instructions on running moss.

## Dependencies 
Perl 5.10, Perlbrew, Ctime.pl (only present in perl 5.10)

```
sudo apt-get install perlbrew
perlbrew init
source ~/perl5/perlbrew/etc/bashrc
perlbrew install perl-5.10.1
# Might complain about error, but that's ok. 
cd ~/perl5/perlbrew/build/perl-5.10.1/perl-5.10.1; make install
perlbrew switch perl-5.10.1
```


## Running on entire directory

Steps for creating moss directory using gitgud tool

```
python3.6 ./git_gud.py clone -o=CMPT-431-SFU ass0-git-tutorial # clones all students
python3.6 ./git_gud.py moss -o=CMPT-431-SFU ass0-git-tutorial # iterates over cloned folders and creates moss folder
mv moss moss-ass0 # Sets up moss directory for next step
```

```
chmod +x moss.pl
perl ./moss.pl -d moss-ass0/*/*
```
