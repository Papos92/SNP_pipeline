#!/usr/bin/env python

# Name:         vcf_samplename_editor.py
# Author:       Tom van Wijk
# Date:         16-06-2018
# Licence:      GNU General Public License v3.0, copy provided in repository

# Reads a .vcf file and .samplename file and replaces sample names in .vcf file
# and replaces sample names in .vcf file with names for .samplename file.
# This script is part of the SNP_pipeline.

# For detailed information and instruction on how to install and use this software
# please vieuw the included "README.md" file in this repository

# import python libraries
from argparse import ArgumentParser
import sys


# Function to parse the command-line arguments
# Returns a namespace with argument keys and values
def parse_arguments(args):
	parser = ArgumentParser(prog="vcf_samplename_editor.py")
	parser.add_argument("-i", "--infile", dest = "input_file",
		action = "store", default = None, type = str,
		help = "Location of input .vsf file (required)",
		required = True)
	parser.add_argument("-s", "--samplefile", dest = "sample_file",
		action = "store", default = None, type = str,
		help = "Location of input .sample (required)",
		required = True)
	return parser.parse_args()


# MAIN function
def main():
	# parse command line arguments
	args = parse_arguments(sys.argv)
	# read .samplefile and make dictionary of lines
	sample_names = {}
	with open(args.sample_file, "r") as sample_file:
		for line in sample_file:
			if line.split("\t")[0].startswith("Sample"):
				sample_names[line.split("\t")[0]] = line.split("\t")[1].replace("\n", "")
				#print line.split("\t")[0]+"\t"+line.split("\t")[1].replace("\n", "") #Testing code
	sample_file.close()
	#for key in sample_names.keys(): #Testing code
	#	print key+"\t"+sample_names.get(key) #Testing code
	with open(args.input_file, "r") as infile, open(args.input_file.replace(".vcf", "_renamed.vcf"), "w") as outfile:
		for line in infile:
			if line.startswith("#CHROM"):
				for key in sample_names.keys():
					line = line.replace(str(key), str(sample_names.get(key)))
				outfile.write(line)
			else:
				outfile.write(line)
	infile.close()
	outfile.close()

main()
