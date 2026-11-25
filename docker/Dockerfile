FROM ubuntu:24.04@sha256:9c7f200c07e3d4a03e7249d2c16bf66a51120fb876aa2242cf31451412543289 AS build

ARG TRINITY_VERSION=2.16.3
ARG TRINITY_SHA256=4d6db75052bbedf1cc01967ba4418f37fd5a895bfb4145d747bc396b1ac951d3
ARG TARGETARCH
ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# The base and FULL source are pinned. Ubuntu repositories and transitive
# packages remain mutable: removed packages can require a reviewed successor.
# These checks detect drift; they do not promise permanent upstream availability.
RUN apt-get -o Acquire::Retries=3 update \
 && apt-get install -y --no-install-recommends \
      ca-certificates curl build-essential autoconf automake cmake git libtool \
      pkg-config zlib1g-dev libbz2-dev liblzma-dev libncurses-dev perl python3 xz-utils \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp/trinity-build
RUN curl --fail --location --retry 4 --connect-timeout 30 \
      -o trinity.tar.gz "https://github.com/trinityrnaseq/trinityrnaseq/releases/download/Trinity-v${TRINITY_VERSION}/trinityrnaseq-v${TRINITY_VERSION}.FULL.tar.gz" \
 && echo "${TRINITY_SHA256}  trinity.tar.gz" | sha256sum -c - \
 && tar -xzf trinity.tar.gz \
 && mv "trinityrnaseq-v${TRINITY_VERSION}" /opt/trinity \
 && rm /tmp/trinity-build/trinity.tar.gz

# Trinity >=2.16.2 requires Salmon >=2.9. Use the official, architecture-specific
# 2.12.0 binaries unchanged; preserve their BSD license and provenance files.
# Fixed URLs and hashes detect drift but cannot guarantee future availability.
RUN case "$TARGETARCH" in \
      amd64) target=x86_64; checksum=44f02f8cca063f68ffd978e948912e942716f37cb59acbce85de39e1e1f38f95 ;; \
      arm64) target=aarch64; checksum=c7d10d11a6246c8d33a25e28ad0848485338ba45576b2e94374a8efd62334e19 ;; \
      *) echo "Unsupported architecture: $TARGETARCH" >&2; exit 1 ;; \
    esac \
 && curl --fail --location --retry 4 --connect-timeout 30 -o salmon.tar.xz \
      "https://github.com/COMBINE-lab/salmon/releases/download/v2.12.0/salmon-cli-${target}-unknown-linux-gnu.tar.xz" \
 && echo "${checksum}  salmon.tar.xz" | sha256sum -c - \
 && mkdir /opt/salmon \
 && tar -xJf salmon.tar.xz --strip-components=1 -C /opt/salmon \
 && chmod 0755 /opt/salmon /opt/salmon/salmon \
 && chmod 0644 /opt/salmon/LICENSE /opt/salmon/README.md \
 && rm salmon.tar.xz

# Native ARM64 support and bundled HTSlib are fixed upstream in this release.
# Do not retain the old -m64/bamsifter source edits or run scientific fixtures
# during image construction. Full functional tests run against the final image.
WORKDIR /opt/trinity
RUN make && make plugins \
 && for binary in Inchworm/bin/inchworm Chrysalis/bin/Chrysalis \
      Chrysalis/bin/QuantifyGraph Chrysalis/bin/GraphFromFasta \
      Chrysalis/bin/ReadsToTranscripts trinity-plugins/BIN/ParaFly \
      trinity-plugins/BIN/seqtk-trinity trinity-plugins/bamsifter/_sift_bam_max_cov \
      trinity-plugins/slclust/bin/slclust; do test -x "$binary" || exit 1; done \
 && rm -rf /opt/trinity/Inchworm/build /opt/trinity/Chrysalis/build \
 && find /opt/trinity/trinity-plugins -type f \( -name '*.o' -o -name '*.pico' -o -name '*.a' \) -delete

FROM ubuntu:24.04@sha256:9c7f200c07e3d4a03e7249d2c16bf66a51120fb876aa2242cf31451412543289
ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# The compatible Salmon binary is copied from the verified build stage.
# Runtime APT revisions and
# unpinned transitive packages may drift or disappear from the live repository.
# Runtime curl is deliberately absent: assembly examples disable update checks.
RUN apt-get -o Acquire::Retries=3 update \
 && apt-get install -y --no-install-recommends \
      bash bzip2 ca-certificates default-jre-headless findutils gawk gzip \
      libgcc-s1 libgomp1 liburi-perl ncbi-blast+ perl procps python3 python3-numpy \
      samtools=1.19.2-1build2 \
      bowtie2=2.5.2-1 jellyfish=2.3.1-3build1 xz-utils \
 && rm -rf /var/lib/apt/lists/*

COPY --from=build /opt/trinity /opt/trinity
COPY --from=build /opt/salmon /opt/salmon
COPY docker/trinity-check.py /usr/local/libexec/trinity-check.py

ENV TRINITY_HOME=/opt/trinity
ENV PATH=/opt/salmon:/opt/trinity:/opt/trinity/util:/opt/trinity/Inchworm/bin:/opt/trinity/Chrysalis/bin:/opt/trinity/trinity-plugins/BIN:/opt/trinity/trinity-plugins/bamsifter:/opt/trinity/trinity-plugins/slclust/bin:/opt/trinity/trinity-plugins/COLLECTL/collectl:${PATH}
ENV LC_ALL=C.UTF-8
ENV TAFFISH_ENV=TAFFISH
ENV TAFFISH_NAME=trinity
ENV TAFFISH_VERSION=2.16.3
ENV TAFFISH_RELEASE=1
WORKDIR /tmp

# A small offline identity/linkage gate, not a fragile architecture-dependent
# assembly benchmark. Preserve command exit codes and exact version identity.
RUN python3 /usr/local/libexec/trinity-check.py identity
