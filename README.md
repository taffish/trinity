# taf-trinity

Trinity **2.16.1-r1** packages the official FULL source for de novo RNA-seq assembly.
The default command invokes upstream `Trinity` without an algorithm patch.

## Quick start

Run from a writable project directory with enough memory and scratch space:

```sh
taf-trinity -- --no_version_check --seqType fq --max_memory 20G \
  --left left.fq.gz --right right.fq.gz --CPU 8 --output trinity_paired
taf-trinity TrinityStats.pl trinity_paired.Trinity.fasta
```

The output directory must contain `trinity` in its name. Final FASTA and its
`.gene_trans_map` are **beside** that directory, not inside it. The directory
contains intermediate files, checkpoints and Salmon results. Read normalization
and final expression filtering are enabled by default; this image pins compatible
**Salmon 1.10.2** because Trinity 2.16.1 requires Salmon 1.x. This dependency does
not change or use the separately installed TAFFISH Salmon app.

Use `--SS_lib_type` only when the actual library strandedness is known. A single-end example:

```sh
taf-trinity -- --no_version_check --seqType fq --max_memory 10G \
  --single reads.fq.gz --CPU 4 --output trinity_single
```

`--max_memory` is an upstream job setting, not a hard container memory limit.
Allow additional RAM and disk for the process tree and temporary files.

## Commands and paths

```sh
taf-trinity --help
taf-trinity --version
taf-trinity -- --help
taf-trinity -- --version
taf-trinity salmon --version
```

`--help` before the separator is TAFFISH help; after `--` it belongs to Trinity.
Upstream help intentionally exits nonzero. Command mode runs helpers in the same
image; helper names are not Trinity subcommands. Supply input filenames, not a
stdin pipeline: Trinity's assembly is a multi-pass file workflow.

Use working, input and output paths without spaces or shell metacharacters.
Upstream scripts interpolate paths into internal shell commands, so outer shell
quotes alone cannot make such paths safe. Normal shell quoting remains necessary
when passing compound command-mode arguments; use one quoted argument per value.
Do not pass a whole command as one string.

`Trinity --version` always tries its optional update check, even with
`--no_version_check`. Runtime `curl` is intentionally absent; the version is
printed and a warning about the unavailable check is expected. For analysis,
`--no_version_check` suppresses this optional check. No runtime database download
or network connection is needed for the supported workflow.

## Input resources and recovery

Reads, transcript references, genome-guided BAMs and derived indexes are **project
data**, not a downloaded global database. No production database/model or download
helper is added to this image. Built-in small upstream examples are test fixtures.
No API key or account is required for local processing.

Place reads under the current working directory, or bind a shared input directory
read-only. Every parent directory and symlink target must be readable/traversable
by the container user. A symlink to an unmounted location is not a valid input.
For Docker, for example:

```sh
TAFFISH_DOCKER_RUN_ARGS='-v /srv/rnaseq/reads:/reads:ro' \
  taf-trinity -- --no_version_check --seqType fq --max_memory 20G \
  --left /reads/left.fq.gz --right /reads/right.fq.gz --CPU 8 --output trinity_shared
```

For Podman use `TAFFISH_PODMAN_RUN_ARGS` with the same bind; for Apptainer use
`TAFFISH_APPTAINER_RUN_ARGS='--bind /srv/rnaseq/reads:/reads:ro'`. Select the backend
with `TAFFISH_CONTAINER_BACKEND=docker`, `podman` or `apptainer`. Keep the output
in the writable current directory. Do not make shared inputs writable to fix an
output error; copy inputs into a private project directory if necessary.

These are optional per-run/site mounts, not mandatory app runtime flags:

| Shared-input capability | Backend selector | Additional run arguments | Verified boundary |
| --- | --- | --- | --- |
| Docker read-only directory | `TAFFISH_CONTAINER_BACKEND=docker` | `TAFFISH_DOCKER_RUN_ARGS='-v /srv/rnaseq/reads:/reads:ro'` | Ordinary-user reads, valid internal symlink, write denied |
| Podman read-only directory | `TAFFISH_CONTAINER_BACKEND=podman` | `TAFFISH_PODMAN_RUN_ARGS='-v /srv/rnaseq/reads:/reads:ro'` | Ordinary-user reads, valid internal symlink, write denied |
| Apptainer read-only directory | `TAFFISH_CONTAINER_BACKEND=apptainer` | `TAFFISH_APPTAINER_RUN_ARGS='--bind /srv/rnaseq/reads:/reads:ro'` | Actual read-only SIF, ordinary-user reads, write denied |

The installed `taf-trinity --help` includes a complete single-end invocation for
each row. Replace the host path with your prepared read directory; these examples
do not create a system-wide reference installation or change its ownership.

Trinity checkpoints support resuming **the same inputs and options**. They do not
fingerprint arbitrary changed inputs. Preserve logs and the work directory after
failure or interruption, correct the cause, then rerun the original command.
For changed reads/options use a new output directory. Do not delete an old shared
directory or reuse another user's output. Avoid `--full_cleanup` when you need
intermediates for recovery; it deliberately removes the assembly work tree.

Trinity can warn and retain an unfiltered assembly when Salmon filtering fails,
while still returning success. Inspect the log and `salmon_outdir/quant.sf`;
do not interpret a zero exit code alone as successful expression filtering.

## Normalization and abundance utilities

```sh
taf-trinity insilico_read_normalization.pl --seqType fq --JM 10G --max_cov 50 \
  --left left.fq.gz --right right.fq.gz --pairs_together --CPU 4 --output trinity_norm
taf-trinity align_and_estimate_abundance.pl --transcripts trinity_paired.Trinity.fasta \
  --seqType fq --left left.fq.gz --right right.fq.gz --est_method salmon \
  --thread_count 4 --prep_reference --output_dir sample_abundance
taf-trinity abundance_estimates_to_matrix.pl --est_method salmon \
  --cross_sample_norm none --name_sample_by_basedir --gene_trans_map trinity_paired.Trinity.fasta.gene_trans_map \
  --out_prefix abundance sample_abundance/quant.sf
```

`--cross_sample_norm none` is required here: default TMM normalization needs an
R/Bioconductor environment that this image does not supply. Counts and TPM matrices
are output data, not a bundled differential-expression analysis or report.

## Included components and boundaries

Included: Inchworm, Chrysalis, Butterfly, core Perl/Python utilities, ParaFly,
seqtk-trinity, bamsifter with bundled static HTSlib, slclust, collectl, Trimmomatic,
Java, NumPy, Jellyfish 2.3.1, Bowtie2 2.5.2, Samtools 1.19.2, BLAST+ and Salmon 1.10.2.
The former ARM64/bamsifter packaging edits are no longer needed: official 2.16.1
source contains the fixes. No upstream source or scientific algorithm is patched.

This is the core CLI environment, not the upstream project's much larger
downstream analysis Docker environment. R/Bioconductor, Glimma, GOplot, RSEM,
kallisto, eXpress, STAR, HISAT2, GMAP, BLAT, Picard/GATK, FastQC, MultiQC,
Trinotate and TransDecoder are not provided as supported workflows here.
Source helper files may be present without their optional dependencies.

Source inspection found independent Glimma/canvasXpress analysis reports and a
legacy GenomeView HTML/Java Web Start helper. They are not called by the supported
assembly workflow and are **not supported report/GUI entry points** in this image.
No GUI server, port or new report renderer is added. View or analyze exported
FASTA/matrices with separately installed downstream tools. Genome-guided and
long-read modes require appropriate user-supplied inputs and may need additional
tools; their full workflows are not implied by the core CLI scope.

## Build identity and maintenance

- Image: `ghcr.io/taffish/trinity:2.16.1-r1`; native `linux/amd64` and `linux/arm64`.
- Official tag: `Trinity-v2.16.1`, commit `815ce3f22869e12411babe6bd60b347c6327b084`.
- FULL SHA256: `5045c3e245b2a73578154737c4d18c7e2919e676746ef00ac16f2d61dfaff3b8`.
- Ubuntu 24.04 index digest: `9c7f200c07e3d4a03e7249d2c16bf66a51120fb876aa2242cf31451412543289`.
- Ubuntu repositories and transitive dependencies remain mutable; fixed package
  revisions can disappear. Hashes detect changed source, not perpetual download
  availability. A later rebuild may require a reviewed successor dependency update.
- The Action is copied unchanged from a fresh `taf 0.12.0 new` template. Build-time
  checks are lightweight identity/linkage checks; functional assembly tests run
  separately against the final image. Current acceptance is recorded by maintainers.

## Packaging validation

On 2026-11-21, the final native ARM64 Docker/Podman and xjp native x86_64
Docker/Podman/Apptainer routes passed. Each manifest command ran independently,
offline; Docker/Podman additionally used ordinary-user read-only-root containers,
and Apptainer used an actual read-only SIF from the same candidate OCI image.
Real wrappers separately verified default assembly and Salmon results, helpers,
shared reads, output ownership, missing-input failure and unchanged-input resume.
Synthetic command-stage interruption and empty-output recovery are tested; they
are not a claim of full production assembly interruption or scientific accuracy.
There is no backend exception. Release notes record sizes and the validation scope;
publication, subsequent Action builds and Index ingestion are separate steps.

## Licenses and citations

TAFFISH packaging is Apache-2.0. Trinity is BSD-3-Clause; bundled plugins and
Ubuntu packages retain their own licenses, including Salmon, Trimmomatic and
collectl GPL terms. Upstream license files and system package copyright notices
remain in the image. This is not an Apache-only redistribution of all components.

- [Official release](https://github.com/trinityrnaseq/trinityrnaseq/releases/tag/Trinity-v2.16.1)
- [Running Trinity](https://github.com/trinityrnaseq/trinityrnaseq/wiki/Running-Trinity)
- Grabherr et al. 2011: DOI `10.1038/nbt.1883`, PMID `21572440`.
- Haas et al. 2013: DOI `10.1038/nprot.2013.084`, PMID `23845962`.
