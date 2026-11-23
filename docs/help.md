taf-trinity 2.16.1-r1

Assemble RNA-seq reads with upstream Trinity 2.16.1.

Usage:
  taf-trinity -- --no_version_check --seqType fq --max_memory 20G --left left.fq.gz --right right.fq.gz --CPU 8 --output trinity_paired
  taf-trinity -- --no_version_check --seqType fq --max_memory 10G --single reads.fq.gz --CPU 4 --output trinity_single

Help and version:
  taf-trinity --help             This usage help.
  taf-trinity --version          TAFFISH package version.
  taf-trinity -- --help          Upstream options (upstream exits nonzero).
  taf-trinity -- --version       Upstream version; an update-check warning is normal.

Key options:
  --seqType fq|fa                FASTQ or FASTA reads; gzip inputs are supported.
  --left FILES --right FILES     Paired reads; comma-separated lists must match.
  --single FILES                Single-end reads.
  --SS_lib_type RF|FR|F|R        Use the library's actual strandedness; omit if unstranded.
  --CPU N --max_memory SIZE      Set CPU and memory for the job.
  --output DIR                  Dedicated writable directory containing "trinity".
  --no_version_check            Disable the assembly's optional update check.

Outputs and utilities:
  Final sequences: trinity_paired.Trinity.fasta (beside the work directory).
  Transcript mapping: trinity_paired.Trinity.fasta.gene_trans_map.
  taf-trinity TrinityStats.pl trinity_paired.Trinity.fasta
  taf-trinity insilico_read_normalization.pl --seqType fq --JM 10G --max_cov 50 --left left.fq.gz --right right.fq.gz --pairs_together --CPU 4 --output trinity_norm
  taf-trinity salmon --version

Optional shared reads (replace /srv/rnaseq/reads; run from a writable project):
  Docker:
    TAFFISH_CONTAINER_BACKEND=docker TAFFISH_DOCKER_RUN_ARGS='-v /srv/rnaseq/reads:/reads:ro' taf-trinity -- --no_version_check --seqType fq --max_memory 1G --single /reads/left.fq --CPU 1 --output trinity_shared
  Podman:
    TAFFISH_CONTAINER_BACKEND=podman TAFFISH_PODMAN_RUN_ARGS='-v /srv/rnaseq/reads:/reads:ro' taf-trinity -- --no_version_check --seqType fq --max_memory 1G --single /reads/left.fq --CPU 1 --output trinity_shared
  Apptainer:
    TAFFISH_CONTAINER_BACKEND=apptainer TAFFISH_APPTAINER_RUN_ARGS='--bind /srv/rnaseq/reads:/reads:ro' taf-trinity -- --no_version_check --seqType fq --max_memory 1G --single /reads/left.fq --CPU 1 --output trinity_shared
  Increase CPU/memory for your data. Inputs stay read-only; outputs stay in the project.

Before running:
  Use file inputs, not stdin. Keep analysis/input/output paths free of spaces
  and shell metacharacters; quoting cannot repair upstream internal shell commands.
  Keep reads in the working tree or explicitly bind their parent directory.
  No production database download is needed; indexes and checkpoints belong
  to the writable project output, not the image or a shared reference directory.
  Normalization and Salmon 1.10.2 final filtering are enabled by default.
  Check logs for filtering failures even if Trinity returns success.
  Reuse a work directory only with identical inputs/options; otherwise use a new one.
  Avoid --full_cleanup if you need intermediate files for recovery.
  R/Bioconductor, differential-expression reports and independent viewers are
  not included. For abundance matrices use --cross_sample_norm none.
  Resource binding, downstream boundaries and licenses are described in README.
