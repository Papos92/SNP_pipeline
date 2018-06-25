#!/usr/bin/env python

# Name:         snp_bamfiles.py
# Author:       Tom van Wijk - RIVM Bilthoven
# Date:         16-06-2018
# Licence:      GNU General Public License v3.0, copy provided in repository

# Creates mpileup of directory of indexed .bam (and .bai) files and snips using VarScan
# This script is part of the SNP_pipeline.

# For detailed information and instruction on how to install and use this software
# please vieuw the included "README.md" file in this repository

# import python libraries
from argparse import ArgumentParser
import sys
import os


# Function to parse the command-line arguments
# Returns a namespace with argument keys and values
def parse_arguments(args):
	parser = ArgumentParser(prog="snip_bams.py")
	parser.add_argument("-i", "--indir", dest = "input_dir",
		action = "store", default = None, type = str,
		help = "Location of input directory (required)",
		required = True)
	parser.add_argument("-r" "--reference", dest = "reference",
		action = "store", default = "NC_011205", type = str,
		help = "Reference genome (default=NC_011205)")
	return parser.parse_args()


# Function creates a list of files or directories in <inputdir>
# on the specified directory depth
def list_directory(input_dir, obj_type, depth):
	dir_depth = 1
	for root, dirs, files in os.walk(input_dir):
		if dir_depth == depth:
			if obj_type ==  'files':
				return files
			elif obj_type == 'dirs':
				return dirs
		dir_depth += 1


# MAIN function
def main():
	# parse command line arguments
	args = parse_arguments(sys.argv)
	# creating output directory
	outdir = os.path.abspath(args.input_dir+"/snip_bams_output")
	os.system("mkdir -p "+outdir)	
	# read .samplefile and make dictionary of lines
	sample_no = 1
	with open(outdir+"/samplenames.txt", "w") as sample_file:
		# Align sample bam files together
		mpileup_command = ("samtools mpileup -f %s" % (os.environ['SNP_REF']+"/"+args.reference+".fasta"))
		for file in list_directory(args.input_dir, 'files', 1):
			if file.endswith(".bam"):
				mpileup_command += (" "+args.input_dir+"/"+file)
				if sample_no > 1:
					sample_file.write("\n")
				sample_file.write("Sample"+str(sample_no)+"\t"+file.replace("_sorted_rmdup.bam",""))
				sample_no +=1
		mpileup_command += (" > "+outdir+"/"+"total.mpileup")
		print mpileup_command
		os.system(mpileup_command)
	sample_file.close()
	# Call SNP's using VarScan
	os.system("java -jar $VARSCAN mpileup2snp %s --min-coverage 2 --min-var-freq 0.8 --p-value 0.005 --variants --output-vcf > %s"
			  % (outdir+"/"+"total.mpileup",
				outdir+"/"+"total_variants.vcf"))

main()
