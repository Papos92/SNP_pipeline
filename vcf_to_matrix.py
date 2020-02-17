#!/usr/bin/env python

# Name:         vcf_to_matrix.py
# Author:       Tom van Wijk
# Date:         16-06-2018
# Licence:      GNU General Public License v3.0, copy provided in repository

# Reads a .vcf file converst to matrix . txt file to be used with statistical packages.
# This script is part of the SNP_pipeline.

# For detailed information and instruction on how to install and use this software
# please vieuw the included "README.md" file in this repository

# import python libraries
from argparse import ArgumentParser
import sys


# Function to parse the command-line arguments
# Returns a namespace with argument keys and values
def parse_arguments(args):
	parser = ArgumentParser(prog="vcf_to_matrix.py")
	parser.add_argument("-i", "--infile", dest = "input_file",
		action = "store", default = None, type = str,
		help = "Location of input .vsf file (required)",
		required = True)
	return parser.parse_args()


# MAIN function
def main():
	# parse command line arguments
	args = parse_arguments(sys.argv)
	with open(args.input_file, "r") as infile, open(args.input_file.replace(".vcf", "_matrix.txt"), "w") as outfile:
		write_to_out = False
		for line in infile:
			if line.startswith("#CHROM"):
				write_to_out = True
			if write_to_out == True:
				tab = 0
				for x in line.split("\t")[:-1]:
					if tab == 1:
						outfile.write(str(x)+"\t")
					if tab > 8:
						outfile.write(str(x.split("/")[0])+"\t")
					tab +=1
				if line.startswith("#CHROM"):
					outfile.write(line.split("\t")[-1])
				else:
					outfile.write(str(line.split("\t")[-1].split("/")[0])+"\n")
	infile.close()
	outfile.close()

main()
