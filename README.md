# SNP_pipeline
Pipeline for reference-based variant (SNP/indels) calling from raw data to phylogeny.

https://icb.med.cornell.edu/wiki/index.php/Elementolab/BWA_tutorial

Introduction

BWA (Burrows-Wheeler Aligner)is a program that aligns short deep-sequencing reads to long reference sequences. Here is a short tutorial on the installation and steps needed to perform alignments. You can align the short reads to the genome or the transcriptome depending on the experiment/application.
[edit]
Installation
[edit]
Download and install BWA on a Linux/Mac machine

NOTE: You need to do this only once!!

Download: http://sourceforge.net/projects/bio-bwa/files/

Then:

bunzip2 bwa-0.5.9.tar.bz2 
tar xvf bwa-0.5.9.tar
cd bwa-0.5.9
make

Add bwa to your PATH by editing ~/.bashrc and adding

export PATH=$PATH:/path/to/bwa-0.5.9    # /path/to is an example ! replace with real path on your machine

Then execute the command in using source.

source ~/.bashrc

(in some systems, ~/.bash_profile is used in place of ~/.bashrc)

Then, to test if the installation was successful, just type:

bwa

If Unix can find bwa, the 'bwa' command alone will show you all of the options available.
[edit]
Download the reference genome

NOTE: You need to do this only once !

wget provides an easy way to do so, but you can also download the file manually.

wget http://hgdownload.cse.ucsc.edu/goldenPath/hg19/bigZips/chromFa.tar.gz

Unzip it and concatenate the chromosome files

tar zvfx chromFa.tar.gz
cat *.fa > wg.fa

Then erase chromosome files:

rm chr*.fa

[edit]
Download the mRNA sequences (RefSeq)

    Download SNVseeqer's http://physiology.med.cornell.edu/faculty/elemento/lab/files/refGene.txt.07Jun2010.fa (they represent the genomic counterparts of RefSeq mRNAs, i.e. transcription start site to end site with all introns removed). Pleas do not use the mRNA transcripts from the RefSeq Web site directly. 

    The latest RefGene FASTA file can be generated from the RefSeq definition file using SNVseeqer/Adding a new annotation database. 


NOTE: You need to do this only once!!
[edit]
Index the references
[edit]
Create the index for the reference genome (assuming your reference sequences are in wg.fa)

bwa index -p hg19bwaidx -a bwtsw wg.fa

Note 1: index creation only needs to be performed once (the index does not have to be recreated for every alignment job).

Note 2: for small genomes, use -a is instead
[edit]
Create the index for RefSeq transcript sequences (assuming your reference sequences are in refGene.txt.07Jun2010.fa)

bwa index -p RefSeqbwaidx -a bwtsw refGene.txt.07Jun2010.fa

Note: index creation only needs to be performed once (the index does not have to be recreated for every alignment job).
[edit]
Alignment of short reads
[edit]
Mapping short reads to the reference genome, eg hg19

1. Align sequences using multiple threads (eg 4 CPUs). We assume your short reads are in the s_3_sequence.txt.gz file.

bwa aln -t 4 hg19bwaidx s_3_sequence.txt.gz >  s_3_sequence.txt.bwa

Notes: 
(1) BWA can also take a compressed read file as input. So you can leave your read files compressed to save disk space.
(2) Problematic SAM output has been observed when aligning with more than 10 CPUs.

2. Create alignment in the SAM format (a generic format for storing large nucleotide sequence alignments):

bwa samse hg19bwaidx s_3_sequence.txt.bwa s_3_sequence.txt.gz > s_3_sequence.txt.sam

Note 1: BWA is capable of aligning reads stored in the compressed format (*.gz). You can gzip your reads to save disk space.

Note 2: for paired end reads, you need to align each end (R1 and R2) separarely:

bwa aln -t 4 hg19bwaidx s_3_1_sequence.txt.gz >  s_3_1_sequence.txt.bwa
bwa aln -t 4 hg19bwaidx s_3_2_sequence.txt.gz >  s_3_2_sequence.txt.bwa
bwa sampe hg19bwaidx s_3_1_sequence.txt.bwa s_3_2_sequence.txt.bwa s_3_1_sequence.txt.gz s_3_2_sequence.txt.gz > s_3_sequence.txt.sam

Typically, after this step, you can split the reads using our split_samfile tool, or convert SAM to BAM
[edit]
Mapping short reads to RefSeq mRNAs

1. Align sequences using multiple threads (eg 4). We assume your short reads are in the s_3_sequence.txt file.

bwa aln -t 4 RefSeqbwaidx s_3_sequence.txt >  s_3_sequence.txt.bwa

2. Create alignment in the SAM format (a generic format for storing large nucleotide sequence alignments):

bwa samse RefSeqbwaidx s_3_sequence.txt.bwa s_3_sequence.txt > s_3_sequence.txt.sam

[edit]
Mapping long reads (454)

You can align 454 long reads using the bwasw command:

bwa bwasw hg19bwaidx 454seqs.txt > 454seqs.sam

