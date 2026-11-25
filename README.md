# taf-trinity

Trinity **2.16.3-r1** packages the official FULL source for de novo RNA-seq assembly.
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
**Salmon 2.12.0** because Trinity 2.16.2 and later require Salmon 2.x (at least 2.9). This dependency does
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

Salmon 1.x indexes are incompatible with Salmon 2.x. The abundance helper rejects
their `versionInfo.json` marker without deleting the index. Keep the old project
intact and copy the same transcript FASTA to a new writable project, then run
`align_and_estimate_abundance.pl --prep_reference` there. The helper writes its
`TRANSCRIPTS.salmon.idx` next to the transcript file, not in `--output_dir`.
Do not try to build an index next to a read-only shared reference. Index creation
does not automatically repair a partial directory: preserve diagnostics and use
a fresh project path after an interrupted index build. Reusing completed
`quant.sf` skips quantification; this is safe only with unchanged inputs/options.
Failed preparation (including a missing reference) can leave an empty index
directory. Its existence does not indicate success; preserve the failure log.

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
For single-end abundance estimation, `--fragment_length` (default 200) and
`--fragment_std` (default 80) are forwarded to Salmon; set them to appropriate
values for your library. They are distinct from Trinity's final-filter defaults.
Quantification files combined into a matrix must use exactly the same transcript
reference. A mismatch fails explicitly; use a new `--out_prefix` so a failed run
cannot truncate previously produced matrices.

## Included components and boundaries

Included: Inchworm, Chrysalis, Butterfly, core Perl/Python utilities, ParaFly,
seqtk-trinity, bamsifter with bundled static HTSlib, slclust, collectl, Trimmomatic,
Java, NumPy, Jellyfish 2.3.1, Bowtie2 2.5.2, Samtools 1.19.2, BLAST+ and Salmon 2.12.0.
The former ARM64/bamsifter packaging edits are no longer needed: official
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

- Image: `ghcr.io/taffish/trinity:2.16.3-r1`; native `linux/amd64` and `linux/arm64`.
- Official tag: `Trinity-v2.16.3`, commit `d30a36be9cd21697ec2abcc2744a01096ff6fc0a`.
- FULL SHA256: `4d6db75052bbedf1cc01967ba4418f37fd5a895bfb4145d747bc396b1ac951d3`.
- Unmodified official Salmon 2.12.0 binaries: amd64 archive SHA256
  `44f02f8cca063f68ffd978e948912e942716f37cb59acbce85de39e1e1f38f95`,
  ARM64 archive SHA256 `c7d10d11a6246c8d33a25e28ad0848485338ba45576b2e94374a8efd62334e19`.
- Ubuntu 24.04 index digest: `9c7f200c07e3d4a03e7249d2c16bf66a51120fb876aa2242cf31451412543289`.
- Ubuntu repositories and transitive dependencies remain mutable; fixed package
  revisions can disappear. Hashes detect changed source, not perpetual download
  availability. A later rebuild may require a reviewed successor dependency update.
- The Action is copied unchanged from a fresh `taf 0.12.0 new` template. Build-time
  checks are lightweight identity/linkage checks; functional assembly tests run
  separately against the final image. Current acceptance is recorded by maintainers.

## Packaging validation

On 2026-11-24, native ARM64 Docker/Podman and xjp native amd64
Docker/Podman/Apptainer passed current-candidate validation. Each of the 51 exact
manifest checks ran independently offline; Docker/Podman also passed ordinary-user,
cap-drop-all, read-only-root checks. Apptainer used a real read-only SIF from the
same candidate OCI image. Real wrappers verified default paired/single-end assembly,
normalization, nonzero Salmon assignment, matrices, shared reads and output ownership.
Legacy/partial indexes, unreadable parents, dangling references, recovery in a new
project and unchanged-input idempotence were checked without deleting old resources.
Empty-output recovery and synthetic Pipeliner-stage interruption were also tested;
this is not full production assembly interruption or scientific accuracy validation.
Inspected image sizes are 684.78 MiB (ARM64) and 670.54 MiB (amd64), not compressed
download sizes. Publication, subsequent Action builds and Index ingestion remain
separate maintainer actions. Release notes describe the complete validation scope.

## Licenses and citations

TAFFISH packaging is Apache-2.0. Trinity is BSD-3-Clause; bundled plugins and
Ubuntu packages retain their own licenses. The included Salmon 2.12.0 release
uses BSD-3-Clause; its license is preserved at `/opt/salmon/LICENSE`.
Trimmomatic and collectl retain their GPL terms. Upstream license files and system package copyright notices
remain in the image. This is not an Apache-only redistribution of all components.

- [Official release](https://github.com/trinityrnaseq/trinityrnaseq/releases/tag/Trinity-v2.16.3)
- [Running Trinity](https://github.com/trinityrnaseq/trinityrnaseq/wiki/Running-Trinity)
- Grabherr et al. 2011: DOI `10.1038/nbt.1883`, PMID `21572440`.
- Haas et al. 2013: DOI `10.1038/nprot.2013.084`, PMID `23845962`.
