# taf-trinity

`taf-trinity` packages Trinity `2.15.2-r2` for de novo RNA-seq transcriptome assembly.

Package identity:

- name: `trinity`
- command: `taf-trinity`
- kind: `tool`
- TAFFISH version: `2.15.2-r2`
- container image: `ghcr.io/taffish/trinity:2.15.2-r2`
- upstream release: `Trinity-v2.15.2`
- runtime version string: `Trinity version: Trinity-v2.15.2`
- source archive: `trinityrnaseq-v2.15.2.FULL.tar.gz`
- source SHA256: `baab87e4878ad097e265c46de121414629bf88fa9342022baae5cac12432a15c`

## What Is Included

This app builds Trinity from the official FULL release archive and includes the core Trinity assembly stack:

- `Trinity`
- Inchworm and Chrysalis binaries
- Butterfly Java jar from the upstream release archive
- Trinity utility scripts such as `TrinityStats.pl`, `insilico_read_normalization.pl`, `align_and_estimate_abundance.pl`, and `abundance_estimates_to_matrix.pl`
- built bundled helpers: `ParaFly`, `seqtk-trinity`, `bamsifter`, `slclust`, and `collectl`
- runtime tools required by the main Trinity path: Java, Perl, Python 3 with NumPy, Jellyfish 2, Bowtie2, Salmon, Samtools, and BLAST+

The default TAFFISH command runs the upstream `Trinity` script directly:

```sh
taf-trinity -- --seqType fq --max_memory 20G \
  --left reads_1.fq.gz \
  --right reads_2.fq.gz \
  --CPU 8 \
  --output trinity_out_dir
```

The output directory name must contain `trinity`, following Trinity's own safety check.

## Command Mode

`taf-trinity --help` prints this app's wrapper help. Use `--` to pass option-leading arguments to the default upstream command:

```sh
taf-trinity -- --help
taf-trinity -- --version
taf-trinity -- --seqType fq --single reads.fq.gz --max_memory 10G --CPU 4 --output trinity_single_out
```

Because this is a normal tool app with command mode enabled, helper commands can be run in the same container:

```sh
taf-trinity Trinity --version
taf-trinity TrinityStats.pl trinity_out_dir.Trinity.fasta
taf-trinity insilico_read_normalization.pl --help
taf-trinity salmon --version
taf-trinity bowtie2 --version
```

For upstream utilities, prefer command mode with the real utility name rather than trying to treat utility names as `Trinity` subcommands.

## Common Workflows

Paired-end de novo assembly:

```sh
taf-trinity -- --seqType fq --max_memory 50G \
  --left left.fq.gz \
  --right right.fq.gz \
  --CPU 16 \
  --output trinity_paired_out
```

Single-end de novo assembly:

```sh
taf-trinity -- --seqType fq --max_memory 20G \
  --single reads.fq.gz \
  --CPU 8 \
  --output trinity_single_out
```

Run Trinity statistics:

```sh
taf-trinity TrinityStats.pl trinity_paired_out.Trinity.fasta
```

In-silico read normalization:

```sh
taf-trinity insilico_read_normalization.pl --seqType fq --JM 20G \
  --left left.fq.gz \
  --right right.fq.gz \
  --pairs_together \
  --CPU 8 \
  --output trinity_norm
```

## Boundaries

This package is intended to cover Trinity's main de novo assembly path and the core helpers needed by that path. It does not attempt to reproduce the full upstream Docker image's large downstream analysis environment. In particular, R/Bioconductor packages, RSEM, kallisto, eXpress, STAR, HISAT2, GMAP, BLAT, Picard/GATK, FastQC, MultiQC, and differential-expression plotting/reporting stacks are not bundled here unless they are already listed above.

`align_and_estimate_abundance.pl` can use Salmon in this image. Modes that require RSEM, kallisto, eXpress, or extra aligners should be run with separate TAFFISH apps or a dedicated downstream workflow.

Genome-guided and long-read-assisted modes are partially covered by Samtools and BLAST+ in this image, but paths that require external alignments, Picard, GATK, site-specific grid schedulers, or large reference resources remain user-supplied workflow concerns.

Trinity's `--version` command performs an upstream network check when `curl` is available. This runtime image intentionally does not install `curl`; the command still prints `Trinity version: Trinity-v2.15.2` and then reports that it could not run the network check.

## Platform

The image is built from source on Ubuntu 24.04 and is intended for native `linux/amd64` and `linux/arm64` container platforms. Trinity jobs can be memory and CPU intensive; set `--max_memory` and `--CPU` explicitly for reproducible runs.

## License Boundary

The TAFFISH app packaging files are licensed under Apache-2.0. The packaged upstream Trinity software is covered by: BSD-3-Clause with bundled third-party components including ParaFly, seqtk-trinity, Trimmomatic, collectl, bamsifter/htslib, and Ubuntu-packaged runtime tools. Bundled third-party components, datasets, models, and external resources keep their own license terms.

## Upstream

- Upstream repository: <https://github.com/trinityrnaseq/trinityrnaseq>
- Upstream release: <https://github.com/trinityrnaseq/trinityrnaseq/releases/tag/Trinity-v2.15.2>
- Running Trinity manual: <https://github.com/trinityrnaseq/trinityrnaseq/wiki/Running-Trinity>
- Upstream license: BSD-3-Clause for Trinity itself, with additional bundled and Ubuntu-packaged third-party components under their respective licenses.

Primary citations:

- Grabherr et al. 2011. Full-length transcriptome assembly from RNA-Seq data without a reference genome. DOI: `10.1038/nbt.1883`, PMID: `21572440`.
- Haas et al. 2013. De novo transcript sequence reconstruction from RNA-seq using the Trinity platform for reference generation and analysis. DOI: `10.1038/nprot.2013.084`, PMID: `23845962`.
