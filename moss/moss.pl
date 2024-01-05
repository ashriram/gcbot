#!/usr/bin/perl
#
# Please read all the comments down to the line that says "STOP".
# These comments are divided into three sections:
#
#     1. usage instructions
#     2. installation instructions
#     3. standard copyright
#
# IMPORTANT: This is a Linux distribution.  
#

#
#  Section 1. Usage instructions
#
#  moss should be run in the directory where the moss binary is unpacked.  This is necessary so that moss
#  can locate various files in the subdirectories of that directory.  Moss also makes use of temporary
#  files in /tmp.

#  moss.pl [-l language] [-o output directory] [-d] [-b basefile1] ... [-b basefilen] [-m #] [-n #] [-c "string"] file1 file2 file3 ...
#
# The -l option specifies the source language of the tested programs.
# Moss supports many different languages; see the variable "languages" below for the
# full list.
#
# Example: Compare the lisp programs foo.lisp and bar.lisp:
#
#    moss.pl -l lisp foo.lisp bar.lisp
#
# The -o option specifies a directory for output.  The default is html/ in the directory in which moss is run.
# If you don't want to use the default, pick a simple directory name, like html2, javaout, not ../something or /home/...something/.
# A simple name will create a subdirectory of that name in the directory where moss is run, for example: 
# e.g.,
#       moss.pl -l java -o java_results /home/me/submissions/*.java
#
# creates an output directory java_results in the directory where you run moss.  You can actually supply relative and absolute
# pathnames on the command line and this will generate usable output, but some of the links (to documentation and thermometer icons)
# will be broken.
#
# The -d option specifies that submissions are by directory, not by file.
# That is, files in a directory are taken to be part of the same program,
# and reported matches are organized accordingly by directory.
#
# Example: Compare the programs foo and bar, which consist of .c and .h
# files in the directories foo and bar respectively.
#
#    moss.pl -d foo/*.c foo/*.h bar/*.c bar/*.h
#   
# Example: Each program consists of the *.c and *.h files in a directory under
# the directory "assignment1."
#
#    moss.pl -d assignment1/*/*.h assignment1/*/*.c
#
#
# The -b option names a "base file".  Moss normally reports all code
# that matches in pairs of files.  When a base file is supplied,
# program code that also appears in the base file is not counted in matches.
# A typical base file will include, for example, the instructor-supplied 
# code for an assignment.  Multiple -b options are allowed.  You should 
# use a base file if it is convenient; base files improve results, but 
# are not usually necessary for obtaining useful information. 
#
# IMPORTANT: Unlike previous versions of moss, the -b option *always*
# takes a single filename, even if the -d option is also used.
#
# Examples:
#
#  Submit all of the C++ files in the current directory, using skeleton.cc
#  as the base file:
#
#    moss.pl -l cc -b skeleton.cc *.cc
#
#  Submit all of the ML programs in directories asn1.96/* and asn1.97/*, where
#  asn1.97/instructor/example.ml and asn1.96/instructor/example.ml contain the base files.
#
#    moss.pl -l ml -b asn1.97/instructor/example.ml -b asn1.96/instructor/example.ml -d asn1.97/*/*.ml asn1.96/*/*.ml 
#
# The -m option sets the maximum number of times a given passage may appear
# before it is ignored.  A passage of code that appears in many programs
# is probably legitimate sharing and not the result of plagiarism.  With -m N,
# any passage appearing in more than N programs is treated as if it appeared in 
# a base file (i.e., it is never reported).  Option -m can be used to control
# moss' sensitivity.  With -m 2, moss reports only passages that appear
# in exactly two programs.  If one expects many very similar solutions
# (e.g., the short first assignments typical of introductory programming
# courses) then using -m 3 or -m 4 is a good way to eliminate all but
# truly unusual matches between programs while still being able to detect
# 3-way or 4-way plagiarism.  With -m 1000000 (or any very 
# large number), moss reports all matches, no matter how often they appear.  
# The -m setting is most useful for large assignments where one also a base file 
# expected to hold all legitimately shared code.  The default for -m is 10.
#
# Examples:
#
#   moss.pl -l pascal -m 2 *.pascal 
#   moss.pl -l cc -m 1000000 -b mycode.cc asn1/*.cc
#
# 
# The -c option supplies a comment string that is attached to the generated
# report.  This option facilitates matching queries submitted with replies
# received, especially when several queries are submitted at once.
#
# Example:
#
#   moss.pl -l scheme -c "Scheme programs" *.sch
#
# The -n option determines the number of matching files to show in the results.
# The default is 250.
#
# Example:
#   moss.pl -c java -n 200 *.java

#
# Section 2.  Installation instructions.
#     
# You may need to change the very first line of this script
# if perl is not in /usr/bin on your system.  Just replace /usr/bin
# with the pathname of the directory where perl resides.
# 
# Wherever you unpack the mosslocal distribution, be sure run moss.pl
# from the mosslocal directory.  See comments about under -o if you want
# to change the location of the output.
#

#
#  3. Standard Copyright
#
# 
# Copyright (c) 2001-2009 Similix Corporation.
#
# Portions of this software rely on a library that is copyright University of California 
# Regents, which requires the following notice:
#
#Permission to use, copy, modify, and distribute this software for any
#purpose, without fee, and without written agreement is hereby granted,
#provided that the above copyright notice and the following two
#paragraphs appear in all copies of this software.
#
#IN NO EVENT SHALL THE UNIVERSITY OF CALIFORNIA BE LIABLE TO ANY PARTY FOR
#DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING OUT
#OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF THE UNIVERSITY OF
#CALIFORNIA HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#THE UNIVERSITY OF CALIFORNIA SPECIFICALLY DISCLAIMS ANY WARRANTIES,
#INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
#AND FITNESS FOR A PARTICULAR PURPOSE.  THE SOFTWARE PROVIDED HEREUNDER IS
#ON AN "AS IS" BASIS, AND THE UNIVERSITY OF CALIFORNIA HAS NO OBLIGATION TO
#PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.
#
#
# STOP.  It should not be necessary to change anything below this line
# to use the script.
#

#
# As of the date this script was written, the following languages were supported.  This script will work with 
# languages added later however.  Check the moss website for the full list of supported languages.
#
$DEBUG = 0;
$basefileset = 0;

#require "ctime.pl";

$HOME = $ENV{'HOME'};


$nextfile = 0;       # unique filenames are generated by a counter
 
#
# The following arguments are required.  The "normal values" are
# given above, but particularly for controlled testing these values
# can be changed.
#

$HTMLDIR = "html";
$errfile = "errors";
$TMP = "/tmp/mosstmp";
$gap = 10;
$windowsize = 5;
$tilesize = 26;
$maxopt = 10;
$nummatch = 250;
$comment = '';
$language = "c";   # default language is c
$diropt = 0;

use File::Basename;

#
# stuff for web pages
#

$GENERALADDR = "../general";
$BITMAPS = "../bitmaps";

#
# an array of colors
#
$colors[0] = "#FF0000";
$colors[1] = "#00FF00";
$colors[2] = "#0000FF";
$colors[3] = "#00FFFF";
$colors[4] = "#FF00FF";
$colmod = 5;

@languages = ("c", "cc", "java", "ml", "ocaml", "ruby", "pascal", "ada", "lisp", "scheme", "haskell", "fortran", "ascii", "vhdl", "perl", "matlab", "python", "mips", "prolog", "spice", "vb", "csharp", "modula2", "a8086", "javascript", "plsql", "verilog", "tcl", "hc12", "asm");

$usage = "usage: moss [-l language] [-o output directory] [-d] [-b basefile1] ... [-b basefilen] [-m #] [-n #] [-c \"string\"] file1 file2 file3 ...";

#
# Process the command line options.  This is done in a non-standard
# way to allow multiple -b's.
#

$bindex = 0;    # this becomes non-zero if we have any base files

while (@ARGV && ($_ = $ARGV[0]) =~ /^-(.)(.*)/) {
    ($first,$rest) = ($1,$2);	
    
    shift(@ARGV);
    if ($first eq "o") {
	if ($rest eq '') {
	    die "No argument for option -o.\n" unless @ARGV;
	    $rest = shift(@ARGV);
	}
	$HTMLDIR = $rest;
	next;
    }
    if ($first eq "d") {
	$diropt = 1;
	next;
    }
    if ($first eq "b") {
	if($rest eq '') {
	    die "No argument for option -b.\n" unless @ARGV;
	    $rest = shift(@ARGV);
	}
	$opt_b[$bindex++] = $rest;
	next;
    }
    if ($first eq "l") {
	if ($rest eq '') {
	    die "No argument for option -l.\n" unless @ARGV;
	    $rest = shift(@ARGV);
	}
	$language = $rest;
	$answer = "no";
	foreach $l (@languages) {
	    if ($l eq $language) {
		$answer = "yes"
		}
	}
	die "Unrecognized language $language." unless ($answer eq "yes");
	next;
    }
    if ($first eq "m") {
	if($rest eq '') {
	    die "No argument for option -m.\n" unless @ARGV;
	    $rest = shift(@ARGV);
	}
	$maxopt = $rest;
	next;
    }
    if ($first eq "c") {
	if($rest eq '') {
	    die "No argument for option -c.\n" unless @ARGV;
	    $rest = shift(@ARGV);
	}
	$comment = $rest;
	next;
    }
    if ($first eq "n") {
	if($rest eq '') {
	    die "No argument for option -n.\n" unless @ARGV;
	    $rest = shift(@ARGV);
	}
	$nummatch = $rest;
	next;
    }
    die "Unrecognized option -$first.  $usage\n"; 
}

#
# Ensure the various directories we use exist.
#
if (!(-e "$TMP")) {
    system("mkdir $TMP");
    die "Could not create temporary directory $TMP." unless (-e "$TMP");
}
system("rm -f $TMP/*"); 
if (!(-e "$HTMLDIR")) {
    system("mkdir $HTMLDIR");
    die "Could not create output directory $HTMLDIR." unless (-e "$HTMLDIR");
} 
system("rm -f $HTMLDIR/*");
system("rm $errfile"); 



#
# Check a bunch of things first to ensure that the
# script will be able to run to completion.
#

#
# Make sure all the argument files exist and are readable.
#
print "Checking files . . . \n";
$i = 0;
while($i < $bindex)
{
    die "Base file $opt_b[$i] does not exist. $noreq\n" unless -e "$opt_b[$i]";
    die "Base file $opt_b[$i] is not readable. $noreq\n" unless -r "$opt_b[$i]";
    die "Base file $opt_b is not a text file. $noreq\n" unless -T "$opt_b[$i]";
    $i++;
}
foreach $file (@ARGV)
{
    die "File $file does not exist. $noreq\n" unless -e "$file";
    die "File $file is not readable. $noreq\n" unless -r "$file";
    die "File $file is not a text file. $noreq\n" unless -T "$file";
}

if ("@ARGV" eq '') {
    die "No files submitted.\n $usage";
}
print "OK\n";

#
# Build the manifest.
#

# file with the local file and its properties.  Format of an entry is:
#
# local_filename  set language actual_filename
#
# The true filename must go at the end, as it is not under our control and may contain
# characters that would mess up simple parsing of the rest of the line.
#
$manifestfile = "$TMP/manifest";
open(F,">$manifestfile") or die "Could not open manifest file $manifestfile for writing."; 
$i = 0; 
$namecounter = 0;     # for generating unique filenams
while($i < $bindex)
{
    print F "$TMP/$namecounter $basefileset $language $opt_b[$i]\n";
    system("cp $opt_b[$i] $TMP/$namecounter");
    $namecounter++;
    $i++;
}
$setid = $basefileset+1;         # any id that is not the base file id . . .
%man = ();                       # Terrible things will happen if this hash table has stray values in it.
foreach $file (@ARGV)
{
    if ($diropt) {
	($shortname,$dir,$suffix) = fileparse($file);
	$filename = $shortname . $suffix;
	    if (!($combined_file = $man{$dir})) {
		$combined_file = "$TMP/$namecounter.all";
		if (-e $combined_file) { unlink($combined_file); }  # not really a good idea, but the most expedient
		$man{$dir} = $combined_file;
		print F "$combined_file $setid $language $dir\n";
		$setid++;
		$namecounter++;
	    }
	    system("echo \">>>> file: $file\" >> $combined_file");
	    system("cat $file >> $combined_file");
    }
    else
    {
	print F "$TMP/$namecounter $setid $language $file\n";
	system("cp $file $TMP/$namecounter");
	$namecounter++;
	$setid++;
    }
}
close(F);

# web page processing routines

sub match_header {
    print MATCH "<HTML>\n";
    print MATCH "<HEAD>\n";
    print MATCH "<TITLE>$name0</TITLE>\n";
    print MATCH "</HEAD>\n";
    print MATCH "<BODY BGCOLOR=white>\n";
}

sub match_footer {
    print MATCH "</PRE>\n";	    
    print MATCH "</BODY>\n";	    
    print MATCH "</HTML>\n";	    
    close(MATCH);
}


sub match_process {		
#
# At this point $mstart, $mend hold the matches

    $line = 0;
    $index = 0;
#
# The only tricky thing here is that the matches are not necessarily
# stored in program order.  Whenever we find a match, we search for the
# start of the next larger match.
#	
# Start with the match listed first in the program.
#
    for($j = 0; $j < $m; $j++) {
	if ($mstart[$j] < $mstart[$index]) {
	    $index = $j;
	}
    }
    $nextstart = $mstart[$index];
    $nextend = $mend[$index];

    print MATCH "<PRE>\n";
    while(<M1>) {
	$line++;
	if ($line == $nextstart) {
	    $colorindex = $mpos[$index] % $colmod;
	    print MATCH "<A NAME=\"$mpos[$index]\"></A><FONT color = $colors[$colorindex]><A HREF=\"$otherfile#$mpos[$index]\" TARGET=\"$target\"><IMG SRC=\"" . $BITMAPS . "/tm_" . $colorindex . "_" . $mtmsize[$index] . ".gif\" ALT=\"other\" BORDER=\"0\" ALIGN=left></A>\n\n";
	}
	$_ =~ s/</&lt\;/g;
	$_ =~ s/>/&gt\;/g;
	print MATCH $_;
	if ($line == $nextend) {
	    print MATCH "</FONT>";
	    $lastindex = $index;
	    for($j = 0; $j < $m; $j++) {
		if ($mstart[$j] > $mstart[$lastindex]) {
		    if ($index == $lastindex) { $index = $j; } # make sure we get a new index
		    if ($mstart[$j] < $mstart[$index]) { $index = $j; } # make sure we get the min
		}
	    }
	    $nextstart = $mstart[$index];
	    $nextend = $mend[$index];
	    if ($nextstart == $line) { 
		$nextstart++; # hack
		if ($nextend == $line) { $nextend++ }; 
	    }
	}
    }
    print MATCH "</PRE>\n";
}

sub getlocalname {
    local ($name) = @_;
    $localname = $map{$name};
    return $localname;
}


sub gen_menu {
    local ($fh) = @_;
    print $fh "[ <A HREF=\"$GENERALADDR/format.html\" TARGET=\"_top\"> How to Read the Results</A> | <A HREF=\"$GENERALADDR/tips.html\" TARGET=\"_top\"> Tips</A> | <A HREF=\"$GENERALADDR/faq.html\"> FAQ</A> | <A HREF=\"mailto:aiken\@similix.com\">Contact</A> | <A HREF=\"$GENERALADDR/scripts.html\">Submission Scripts</A> | <A HREF=\"$GENERALADDR/credits.html\" TARGET=\"_top\"> Credits</A> ]\n";
}

sub genwebpages {
    local ($manifest) = @_;
    open(M,"<$manifest") or die "Could not open file $manifest for reading.\n";
    while (<M>) {
	($localname,$set,$language,$remotename) = split(' ',$_,4);
	chop($remotename);
	$map{$remotename} = $localname;
    }
    
#
# The index.html file holds links to everything else.
#
    open(INDEX,">>$HTMLDIR/index.html") or die "Could not open file $HTMLDIR/index.html for writing.\n";
    print INDEX "<HTML>\n";
    print INDEX "<HEAD>\n";
    print INDEX "<TITLE>Moss Results</TITLE>\n";

    print INDEX "</HEAD>\n";
    print INDEX "<BODY>\n";
    print INDEX "<TABLE>\n";
    print INDEX "<h3>$comment</h3><p>\n";
    print INDEX "<TR><TH>File 1<TH>File 2<TH>Lines Matched\n";
    
#
# Each line of the report will add a row to the table in index.html
# as well as generate several pages for the associated marked-up source.
#
    open (MOSSIN,"<$TMP/mossout3") or die "Could not open file $TMP/mossout3 for reading.\n";
    $count = 0;
    while(<MOSSIN>)
    {
	if (/\+/) {
	    $arg = $_;
	    if (/(.*) \+ (.*)\: tokens ([0-9]*)   lines ([0-9]*).*percentage matched ([0-9]*\%) \+ ([0-9]*\%)/)
	    {
		$name0 = $1;
		$name1 = $2;
		$ntokens = $3;
		$nlines = $4;
		$percent0 = $5;
		$percent1 = $6;
		$p0 = $percent0;
		chop($p0);
		$p1 = $percent1;
		chop($p1);
	    }
	    print INDEX "<TR><TD><A HREF=\"match$count.html\">$name0 ($percent0)</A>\n";
	    print INDEX "    <TD><A HREF=\"match$count.html\">$name1 ($percent1)</A>\n";
	    print INDEX "<TD ALIGN=right>$nlines\n";
	    open(HEAD,">$HTMLDIR/match$count.html");
	    print HEAD "<HTML>\n";
	    print HEAD "<TITLE>Matches for $name0 and $name1</TITLE>\n";
	    print HEAD "</HEAD>";
	    print HEAD "<FRAMESET ROWS=\"150,*\">";
	    print HEAD "<FRAMESET COLS=\"1000,*\">";
	    print HEAD "<FRAME SRC=\"match$count-top.html\" NAME=\"top\" FRAMEBORDER=0>";
	    print HEAD "</FRAMESET>";
	    print HEAD "<FRAMESET COLS=\"50%,50%\">";
	    print HEAD "<FRAME SRC=\"match$count\-0.html\" NAME=\"0\">";
	    print HEAD "<FRAME SRC=\"match$count\-1.html\" NAME=\"1\">";
	    print HEAD "</FRAMESET>";
	    print HEAD "</FRAMESET>";
	    print HEAD "</HTML>";
	    close(HEAD);
	    
	    open(TOP,">$HTMLDIR/match$count\-top.html");
	    print TOP "<HTML>\n";
	    print TOP "<HEAD>\n";
	    print TOP "<TITLE>Top</TITLE>\n";
	    print TOP "</HEAD>";
	    print TOP "<BODY BGCOLOR=white>";
	    print TOP "<CENTER>";
	    gen_menu(TOP);
	    print TOP "<HR>\n";
	    print TOP "<TABLE BORDER=\"1\" CELLSPACING=\"0\" BGCOLOR=\"#d0d0d0\">";
	    print TOP "<TR><TH>$name0 ($percent0)<TH><IMG SRC=\"$BITMAPS/tm_0_$p0.gif\" BORDER=\"0\" ALIGN=left><TH>$name1 ($percent1)<TH><IMG SRC=\"$BITMAPS/tm_0_$p1.gif\" BORDER=\"0\" ALIGN=left><TH>\n";
	    
#
# This is clunky.  We print the list of matches out to a file
# and then read it back in, one match at a time.
#
	    $mlist = $arg;
	    $mlist =~ s/#/\n/g;
	    unlink("$TMP/matchlist");
	    open(MLIST,">$TMP/matchlist");
	    print MLIST "$mlist";
	    close(MLIST);
	    open(MLIST,"<$TMP/matchlist");
	    <MLIST>;     # first match is just the filenames again
	    $mindex = 0;
	    while(<MLIST>) {
#
# each entry has the format
#      ddd-ddd, ddd-ddd: dddd
#
		if (/([0-9]*)-([0-9]*), ([0-9]*)-([0-9]*): ([0-9]*)/) {
		    $colorindex = $mindex % $colmod;
		    $x1 =   int(($5 / $ntokens) * $p0);
		    $x2 =   int(($5 / $ntokens) * $p1);
		    print TOP "<TR><TD><A HREF=\"match$count\-0.html#$mindex\" NAME=\"$mindex\" TARGET=\"0\">$1-$2</A>\n";
		    print TOP "<TD><A HREF=\"match$count\-0.html#$mindex\" NAME=\"$mindex\" TARGET=\"0\"><IMG SRC=\"". $BITMAPS ."/tm_" . $colorindex . "_$x1.gif\" ALT=\"link\" BORDER=\"0\" ALIGN=left></A>\n";
		    print TOP "<TD><A HREF=\"match$count\-1.html#$mindex\" NAME=\"$mindex\" TARGET=\"1\">$3-$4</A>\n";
		    print TOP "<TD><A HREF=\"match$count\-1.html#$mindex\" NAME=\"$mindex\" TARGET=\"1\"><IMG SRC=\"". $BITMAPS ."/tm_" . $colorindex . "_$x2.gif\" ALT=\"link\" BORDER=\"0\" ALIGN=left></A>\n";

		    $m0start[$mindex] = $1;
		    $m0end[$mindex] = $2;
		    $m0tmsize[$mindex] = $x1;
		    $m1start[$mindex] = $3;
		    $m1end[$mindex] = $4;
		    $m1tmsize[$mindex] = $x2;
		    $mindex++;
		}
	    }
	    close(MLIST);
	    print TOP "</TABLE>";
	    print TOP "</CENTER>";
	    print TOP "</BODY>";
	    print TOP "</BODY>";
	    print TOP "</HTML>";
	    close(TOP);
#  
# loop over both source files, generating the marked-up versions using the m* arrays.
#
	    $otherfile = "match$count\-1.html";
	    $target = 1;
	    open(MATCH,">$HTMLDIR/match$count\-0.html");
	    &match_header();

	    print MATCH "<HR>\n";
	    print MATCH "$name0<p>";
	    $localname = &getlocalname($name0);
	    open(M1,"<$localname");
#
# gather all of the matches for this file into one array
#
	    for($j = 0; $j < $mindex; $j++) {
		$mstart[$j] = $m0start[$j];
		$mend[$j] = $m0end[$j];
		$mtmsize[$j] = $m0tmsize[$j];
		$mpos[$j] = $j;
		$m = $mindex;
	    }
	    &match_process();
	    &match_footer();
#
# second file
#
	    $otherfile = "match$count\-0.html";
	    $target = 0;
	    open(MATCH,">$HTMLDIR/match$count\-1.html");
	    &match_header();
#
# Build a list of all files in the program.
#
	    print MATCH "<HR>\n";
	    print MATCH "$name1<p>";
	    $localname = &getlocalname($name1);
	    open(M1,"<$localname");
#
# gather all of the matches for this file into one array
#
	    for($j = 0; $j < $mindex; $j++) {
		$mstart[$j] = $m1start[$j];
		$mend[$j] = $m1end[$j];
		$mtmsize[$j] = $m1tmsize[$j];
		$mpos[$j] = $j;
		$m = $mindex;
	    }
	    &match_process();
	    close(M1);
	    &match_footer();
	    $count++;
	}
    }

    close(MOSSIN);
    print INDEX "</TABLE>\n";
    if ($count == 0) {
	print INDEX "No matches were found in your submission.<p>";
    }
    print INDEX "<HR>\n";
    print INDEX "Any errors are listed below.<p>";
    open(EFILE,"$errfile");
    while (<EFILE>) {
	print INDEX "$_<p>";
    }
    close(EFILE);

    print INDEX "</BODY>\n";
    print INDEX "</HTML>\n";
    close(INDEX);

}

#
# Sort matches by size and throw out all but the largest.
#
sub filter_matches {
    system("echo >> $TMP/mossout"); # some versions of sort want a blank line
    system("sort -n -r -k5 $TMP/mossout > $TMP/mossout2");
#
# filter out all but the top matches
#
    open(MATCHIN,"<$TMP/mossout2");
    open(MATCHOUT,">$TMP/mossout3");
    while(<MATCHIN>) {
	print MATCHOUT "$_";
	if (--$nummatch == 0) { last; }
    }
    close(MATCHIN);
    close(MATCHOUT);
}



die "Could not fine manifest file $manifestfile" unless (-e "$manifestfile");
$doit = "./moss -p 24 -t $tilesize -w $windowsize -n $maxopt -e $errfile -g $gap -a $manifestfile -o $TMP/mossout";
system("$doit");
&filter_matches();
$url=&genwebpages($manifestfile);

