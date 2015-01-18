#!/usr/bin/python

# A command-line interface for shortening links with LyLi.fi
# by Praash (ie)
# https://github.com/praashie/lyli-shell-client

# LyLi.fi by Felix Bade:
# http://lyli.fi
# https://github.com/felixbade/lyli

import sys;
import json;
import subprocess;
from subprocess import PIPE, STDOUT;
import os;

def printHelp():
	print "lyli.py - interface for shortening links via lyli.fi";
        print "Usage: lyli.py URL [NAME]";
        print "\tURL\t- url to shorten";
        print "\tNAME\t- optional name, replaced by letters if omitted";
        print "";
        print "Resulting shortlinks will be in the form of http://lyli.fi/NAME";

def shorten(a, verbose=False):
	params = [];
	
	#Add a proper http scheme if the given url does not supply a scheme
	if a[0].find("://") < 0:
		a[0] = "http://" + a[0];

	params.append( ('url', a[0]) );
	
	if len(a) > 1:
		params.append( ('name', a[1]) );

	message = json.dumps(dict(params));

	command = "curl --silent -H 'Content-Type: application/json' -X POST -d '" + message + "' api.lyli.fi";


	if verbose:
		print "Sending POST request:";
		print "Executing: " + str(command);
	try:
		#output = str(subprocess.check_output(command));
		output = str(subprocess.check_output(command, shell=True));

	except subprocess.CalledProcessError as err:
		print "Error in curl/api.lyli.fi: POST query failed";
		return 2;

	if verbose:
		print "Output from api.lyli.fi:";
		print output;
	try:
		outJSON = json.loads(output);
	except:
		print "Error in api.lyli.fi: output can't be parsed as JSON";
		
		return 2;

	if "error" in outJSON:
		print "Error in Lyli: " + outJSON["error"];
		return 1;
	elif not "short-url" in outJSON:
		print "Strange Error: api.lyli.fi returned no error, but no shortlink seems to have been made";
		return 3;
	elif "short-url" in outJSON:
		#Success

		#Check whether we can automatically copy the shortlink into the OS clipboard
		isClipboardAvailable = False;
		clipboardCommand = [];
	
		if os.name == "posix":	

			out = subprocess.check_output("which xsel || which pbcopy", shell=True)
			if len(out) > 1:
				out = out[:-1]
				clipboardCommand.append(out);
				if out[-4:] == "xsel":
					clipboardCommand.append("-bi");
				isClipboardAvailable = True;
			
			
		if isClipboardAvailable:
			process = subprocess.Popen(clipboardCommand, stdout=PIPE, stdin=PIPE, stderr=PIPE);
			process.communicate(input=(outJSON["short-url"]));

			if False:
				print "Shortlink: " + outJSON["short-url"];
				print "Error: link could not be copied to the clipboard, but OS seems to support it";
			else:
				print "Shortlink " + outJSON["short-url"] + " copied to clipboard"
		else:
			print "Shortlink: " + outJSON["short-url"];

			print "The shortlink could have been copied to the clipboard automatically,";
			print "but neither xsel nor pbcopy appear to be installed!";
	
		return 0;

def main():
	args = [];
	verbose = False;

	showHelp = False;

	for arg in sys.argv[1:]:
		if arg == '-v' or arg == '--verbose':
			verbose = True;
		elif arg == '-h' or arg == '--help':
			showHelp = True;
			break;
		else:
			args.append(arg);

	if len(args) < 1 or len(args) > 2:
		showHelp = True;

	if showHelp:
		printHelp();
		sys.exit(1);
	else:
		exitStatus = shorten(args, verbose);
		sys.exit(exitStatus);


if __name__ == "__main__":
	main();
