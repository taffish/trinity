taf-trinity 2.15.2-r1

Trinity-v2.15.2 for de novo RNA-seq transcriptome assembly.
The default command runs the upstream Trinity script directly.

Usage:
  taf-trinity -- --seqType fq --max_memory 50G --left left.fq.gz --right right.fq.gz --CPU 16 --output trinity_out_dir
  taf-trinity -- --seqType fq --max_memory 20G --single reads.fq.gz --CPU 8 --output trinity_single_out

Wrapper options:
  taf-trinity --help       Show this TAFFISH help.
  taf-trinity --version    Show the TAFFISH package version.
  taf-trinity --compile    Print the generated runner.
  taf-trinity -- --help    Show upstream Trinity help.
  taf-trinity -- --version Show upstream Trinity version.

Default upstream command:
  Trinity

Command mode:
  taf-trinity Trinity --version
  taf-trinity TrinityStats.pl trinity_out_dir.Trinity.fasta
  taf-trinity insilico_read_normalization.pl --help
  taf-trinity salmon --version
  taf-trinity bowtie2 --version

Common Trinity options:
  --seqType fq|fa          Input read type.
  --max_memory 50G         Suggested maximum memory for Trinity.
  --left FILES             Left reads for paired-end data.
  --right FILES            Right reads for paired-end data.
  --single FILES           Single-end reads.
  --samples_file FILE      Tab-delimited sample file.
  --SS_lib_type STR        Strand-specific library type.
  --CPU N                  Number of worker threads.
  --output DIR             Output directory; Trinity requires "trinity" in the basename.
  --no_normalize_reads     Skip in-silico read normalization.
  --no_salmon              Skip final Salmon expression filtering.
  --genome_guided_bam BAM  Use genome-guided mode from a coordinate-sorted BAM.

Common workflows:
  Paired-end assembly:
    taf-trinity -- --seqType fq --max_memory 50G --left left.fq.gz --right right.fq.gz --CPU 16 --output trinity_paired_out

  Single-end assembly:
    taf-trinity -- --seqType fq --max_memory 20G --single reads.fq.gz --CPU 8 --output trinity_single_out

  Trinity assembly statistics:
    taf-trinity TrinityStats.pl trinity_paired_out.Trinity.fasta

  In-silico normalization:
    taf-trinity insilico_read_normalization.pl --seqType fq --JM 20G --left left.fq.gz --right right.fq.gz --pairs_together --CPU 8 --output trinity_norm

Packaged commands:
  Trinity, TrinityStats.pl, align_and_estimate_abundance.pl,
  abundance_estimates_to_matrix.pl, insilico_read_normalization.pl,
  ParaFly, seqtk-trinity, inchworm, Chrysalis, QuantifyGraph,
  GraphFromFasta, ReadsToTranscripts, bamsifter, slclust, collectl,
  bowtie2, bowtie2-build, jellyfish, samtools, salmon, blastn,
  makeblastdb, java, perl, python3.

Platform:
  Built from source on Ubuntu 24.04 for linux/amd64 and linux/arm64.
  Trinity jobs can be memory intensive; set --max_memory and --CPU explicitly.

Boundaries:
  This image targets the core Trinity de novo assembly path and its key helpers.
  It does not bundle the full upstream Docker image's heavy downstream analysis
  stack: R/Bioconductor packages, RSEM, kallisto, eXpress, STAR, HISAT2, GMAP,
  BLAT, Picard/GATK, FastQC, MultiQC, and plotting/reporting workflows are
  user-supplied or should be handled by separate TAFFISH apps/workflows.
  Salmon-based abundance utilities are available because Salmon is bundled.
  Trinity --version prints Trinity-v2.15.2 and may also note that the optional
  upstream network version check could not run in this offline-style container.
