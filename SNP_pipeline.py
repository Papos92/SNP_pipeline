#!/usr/bin/env python

# Name:         SNP_pipeline.py
# Author:       Tom van Wijk - RIVM Bilthoven
# Date:         10-06-2018
# Licence:      GNU General Public License v3.0, copy provided in repository

# For detailed information and instruction on how to install and use this software
# please vieuw the included "README.md" file in this repository


# import python libraries
from argparse import ArgumentParser
import logging
import logging.handlers
import os
import sys
import random


# Function to parse the command-line arguments
# Returns a namespace with argument keys and values
def parse_arguments(args, log):
	log.info("Parsing command line arguments...")
	parser = ArgumentParser(prog="SNP_pipeline.py")
	parser.add_argument("-i", "--indir", dest = "input_dir",
		action = "store", default = None, type = str,
		help = "Location of input directory (required)",
		required = True)
	parser.add_argument("-o", "--outdir", dest = "output_dir",
		action = "store", default = "inputdir", type = str,
		help = "Location of output directory (default=inputdir)")
	parser.add_argument("-t", "--threads", dest = "threads",
		action = "store", default = 8, type = int,
		help = "Number of threads to be used (default=8)")
	parser.add_argument("-m", "--memory", dest = "ram",
		action = "store", default = 12, type = int,
		help = "Maximum amount of RAM (GB) to be used (default=12)")
	parser.add_argument("-x", "--savetemp", dest = "save_temp",
		action = "store", default = "false", type = str,
		help = "Option to save temporary files (default=false)")
	parser.add_argument("-r" "--reference", dest = "reference",
		action = "store", default = "NC_011205", type = str,
		help = "Reference genome (default=NC_011205)")
	return parser.parse_args()


# Function creates logger with handlers for both logfile and console output
# Returns logger
def create_logger(logid):
	# create logger
	log = logging.getLogger()
	log.setLevel(logging.INFO)
	# create file handler
	fh = logging.FileHandler(str(logid)+'_SNP_pipeline.log')
	fh.setLevel(logging.DEBUG)
	fh.setFormatter(logging.Formatter('%(message)s'))
	log.addHandler(fh)
	# create console handler
	ch = logging.StreamHandler()
	ch.setLevel(logging.INFO)
	ch.setFormatter(logging.Formatter('%(message)s'))
	log.addHandler(ch)
	return log


# Function for trimming reads at q=25 using erne-filter
def trim_reads(R1_file, R2_file, output_dir, threads, erne_log, log):
	log.info("\nTrimming "+R1_file+" and "+R2_file+" reads using enre-filter...")
	os.system("erne-filter --query1 %s --query2 %s --output-prefix %s --q 30 --threads %s | tee -a %s"
			% (R1_file, R2_file,output_dir, str(threads), erne_log))
	

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

		
# Funstion for creating temporary sub-directories
def create_subdirs(outdir):
	trimmed_reads_outdir = outdir+"/trimmed_reads"
	os.system("mkdir -p "+trimmed_reads_outdir)
	logs_outdir = outdir+"/logfiles"
	os.system("mkdir -p "+logs_outdir)
	sorted_reads_outdir = outdir+"/sorted_reads"
	os.system("mkdir -p "+sorted_reads_outdir)
	bwa_sam_outdir = outdir+"/bwa_sam"
	os.system("mkdir -p "+bwa_sam_outdir)
	bwa_bam_outdir = outdir+"/bwa_bam"
	os.system("mkdir -p "+bwa_bam_outdir)
	sorted_bam_outdir = outdir+"/sorted_bam"
	os.system("mkdir -p "+sorted_bam_outdir)
	sorted_rmdup_bam_outdir = outdir+"/sorted_rmdup_bam"
	os.system("mkdir -p "+sorted_rmdup_bam_outdir)
	#sorted_rmdup_realigner_bam_outdir = outdir+"/sorted_rmdup_realigned_bam"
	#os.system("mkdir -p "+sorted_rmdup_realigner_bam_outdir)
	return trimmed_reads_outdir, logs_outdir, sorted_reads_outdir, bwa_sam_outdir, bwa_bam_outdir, sorted_bam_outdir, sorted_rmdup_bam_outdir
		
		
# Function closes logger handlers
def close_logger(log):
        for handler in log.handlers:
                handler.close()
                log.removeFilter(handler)


# MAIN function
def main():
	# create logger
	logid = random.randint(99999, 9999999)
	log = create_logger(logid)
	# parse command line arguments
	args = parse_arguments(sys.argv, log)
	# creating output directory
	if args.output_dir == 'inputdir':
		outdir = os.path.abspath(args.input_dir+"/SNP_pipeline_output")
	else:
		outdir = os.path.abspath(args.output_dir)
	log.info("Creating output direory: "+outdir)
	os.system("mkdir -p "+outdir)
	# Generating output directories for dules
	trimmed_reads_outdir, logs_outdir, sorted_reads_outdir,	bwa_sam_outdir, bwa_bam_outdir,	sorted_bam_outdir, sorted_rmdup_bam_outdir = create_subdirs(outdir)
	# Iterate over filepairs
	sample_no = 1
	with open(outdir+"/samplenames.txt", "w") as sample_file:
		filelist = list_directory(args.input_dir, 'files', 1)
		for file in filelist:
			if '_R1' in file and file.replace('_R1', '_R2') in filelist:
				file_prefix = file.split("_R1")[0].replace(".","_").replace(" ","_")
				R1_file = os.path.abspath(args.input_dir)+"/"+file
				R2_file = os.path.abspath(args.input_dir)+"/"+file.replace('_R1', '_R2')
				if sample_no > 1:
					sample_file.write("\n")
				sample_file.write("Sample"+str(sample_no)+"\t"+os.path.dirname(args.input_dir)+"_"+file_prefix)
				sample_no +=1
				# Quality trim the reads
				trim_reads(str(R1_file), str(R2_file),
						   trimmed_reads_outdir+"/"+file_prefix+"_trimmed",
						   args.threads, logs_outdir+"/erne-filter.log", log)
				# Sort files to match order of paired reads and remove orphaned reads caused by quality trim
				os.system("fastq_pair_mapper.py "+trimmed_reads_outdir+"/"+file_prefix+"_trimmed_1.fastq "
						+trimmed_reads_outdir+"/"+file_prefix+"_trimmed_2.fastq ")
				os.system("mv "+trimmed_reads_outdir+"/*_pairs_R1.fastq "+sorted_reads_outdir+"/.")
				os.system("mv "+trimmed_reads_outdir+"/*_pairs_R2.fastq "+sorted_reads_outdir+"/.")
				os.system("rename 's/_trimmed_1.fastq_pairs_R1.fastq/_R1_sorted.fastq/' "+sorted_reads_outdir+"/*")
				os.system("rename 's/_trimmed_2.fastq_pairs_R2.fastq/_R2_sorted.fastq/' "+sorted_reads_outdir+"/*")
				os.system("rm "+trimmed_reads_outdir+"/*.fastq_singles.fastq")
				# Align trimmed, sorted .fatq files to reference with BWA aligner
				os.system("bwa mem -M -t %s %s %s %s > %s"
						  % (str(args.threads), os.environ['SNP_REF']+"/"+args.reference,
							sorted_reads_outdir+"/"+file_prefix+"_R1_sorted.fastq",
							sorted_reads_outdir+"/"+file_prefix+"_R2_sorted.fastq",
							bwa_sam_outdir+"/"+file_prefix+".sam"))
				# Convert sam to bam file
				os.system("samtools view -Sb %s > %s"
						  % (bwa_sam_outdir+"/"+file_prefix+".sam",
							bwa_bam_outdir+"/"+file_prefix+".bam"))
				# Sort bam file
				os.system("samtools sort %s %s"
						  % (bwa_bam_outdir+"/"+file_prefix+".bam",
						  	sorted_bam_outdir+"/"+file_prefix+"_sorted"))
				# Remove duplicates with Picard
				os.system("java -jar $PICARD MarkDuplicates I=%s O=%s M=%s REMOVE_DUPLICATES=true"
						  % (sorted_bam_outdir+"/"+file_prefix+"_sorted.bam",
							sorted_rmdup_bam_outdir+"/"+file_prefix+"_sorted_rmdup.bam",
							sorted_rmdup_bam_outdir+"/"+file_prefix+"_sorted_duplicatematrix.txt"))
				os.system("samtools index %s"
						  % (sorted_rmdup_bam_outdir+"/"+file_prefix+"_sorted_rmdup.bam"))
				#os.system("java -jar $PICARD AddOrReplaceReadGroups I=%s O=%s RGLB=lib1 RGPL=illumina RGPU=unit RGSM=20"
				#		  % (sorted_rmdup_bam_outdir+"/"+file_prefix+"_sorted_rmdup.bam",
				#			sorted_rmdup_bam_outdir+"/"+file_prefix+"_sorted_rmdup_addgp.bam"))
				#os.system("samtools index %s"
				#		  % (sorted_rmdup_bam_outdir+"/"+file_prefix+"_sorted_rmdup_addgp.bam"))
	
				# Remove subdirs to spare storage capacity
				if args.save_temp == "false":
					for dir in [trimmed_reads_outdir, sorted_reads_outdir,	bwa_sam_outdir, bwa_bam_outdir,	sorted_bam_outdir]:
						os.system("rm -rf "+dir)
					trimmed_reads_outdir, logs_outdir, sorted_reads_outdir,	bwa_sam_outdir, bwa_bam_outdir,	sorted_bam_outdir, sorted_rmdup_bam_outdir = create_subdirs(outdir)

#remove duplicates
#for i in $(ls -d sample*/);
#	java -jar $(which MarkDuplicates.jar)
#		INPUT= $(basename ${i}).bam
#		OUTPUT= $(basename ${i}).rmdup.bam
#		METRICS_FILE= duplicateMatrix
#		REMOVE_DUPLICATES=true;
#	java -jar $(which AddOrReplaceReadGroups.jar) # THIS is required fot GATK only
#		I=$(basename ${i}).rmdup.bam
#		O=$(basename $i).rmdup.addgp.bam
#		LB=whatever PL=illumina PU=whatever SM=whatever;
#	samtools index $(basename ${i}).rmdup.addgp.bam; 

# reallign indels
#samtools faidx Cdiff078.fa
#java -jar $(which CreateSequenceDictionary.jar) R=Cdiff078.fa O=Cdiff078.dict; fi
#for i in $(ls -d sample*/);
#	java -Xmx2g -jar $(which GenomeAnalysisTK.jar)
#		-T RealignerTargetCreator
#		-R ../Cdiff078.fa
#		-I $(basename ${i}).rmdup.addgp.bam
#		-o $(basename ${i}).rmdup.addgp.intervals
#	java -Xmx4g -jar $(which GenomeAnalysisTK.jar)
#		-I $(basename ${i}).rmdup.addgp.bam
#		-R ../Cdiff078.fa
#		-T IndelRealigner
#		-targetIntervals $(basename ${i}).rmdup.addgp.intervals
#		-o $(basename ${i}).realigned.bam;
	
	sample_file.close()

	# Align sample bam files together
	mpileup_command = ("samtools mpileup -f %s" % (os.environ['SNP_REF']+"/"+args.reference+".fasta"))
	for file in list_directory(sorted_rmdup_bam_outdir, 'files', 1):
		if file.endswith(".bam"):
			mpileup_command += (" "+sorted_rmdup_bam_outdir+"/"+file)
	mpileup_command += (" > "+outdir+"/"+"total.mpileup")
	print mpileup_command
	os.system(mpileup_command)
	# Call SNP's using VarScan
	os.system("java -jar $VARSCAN mpileup2snp %s --min-coverage 2 --min-var-freq 0.8 --p-value 0.005 --variants --output-vcf > %s"
			  % (outdir+"/"+"total.mpileup",
				outdir+"/"+"total_variants.vcf"))
		
#samtools mpileup -B -f Cdiff078.fa  sample1/sample1.realigned.bam sample2/sample2.realigned.bam sample3/sample3.realigned.bam
#java -jar VarScan.v2.3.7.jar mpileup2cns --min-coverage 2 --min-var-freq 0.8 --p-value 0.005 --variants --output-vcf > variants.vcf
			
	#Remove the temp directory if temp parameter is not set to anything but false
	if args.save_temp == "false":
		log.info("save_temp parameter is false (default). Removing temporary files and directories...")
		for dir in [trimmed_reads_outdir, sorted_reads_outdir,	bwa_sam_outdir, bwa_bam_outdir,	sorted_bam_outdir]:
			os.system("rm -rf "+dir)
	else:
		log.info("save_temp parameter is not false (set in input parameter). Keeping temporary files and directories...")

	# close logger handlers
	log.info("\nClosing logger and finalising SNP_pipeline.py")
	close_logger(log)
	# move logfile to output directory
	os.system("mv "+str(logid)+"_SNP_pipeline.log "+logs_outdir+"/SNP_pipeline.log")


main()
