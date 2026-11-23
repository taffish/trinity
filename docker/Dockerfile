FROM ubuntu:24.04@sha256:9c7f200c07e3d4a03e7249d2c16bf66a51120fb876aa2242cf31451412543289 AS build

ARG TRINITY_VERSION=2.16.1
ARG TRINITY_SHA256=5045c3e245b2a73578154737c4d18c7e2919e676746ef00ac16f2d61dfaff3b8
ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# The base and FULL source are pinned. Ubuntu repositories and transitive
# packages remain mutable: removed packages can require a reviewed successor.
# These checks detect drift; they do not promise permanent upstream availability.
RUN apt-get -o Acquire::Retries=3 update \
 && apt-get install -y --no-install-recommends \
      ca-certificates curl build-essential autoconf automake cmake git libtool \
      pkg-config zlib1g-dev libbz2-dev liblzma-dev libncurses-dev perl python3 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp/trinity-build
RUN curl --fail --location --retry 4 --connect-timeout 30 \
      -o trinity.tar.gz "https://github.com/trinityrnaseq/trinityrnaseq/releases/download/Trinity-v${TRINITY_VERSION}/trinityrnaseq-v${TRINITY_VERSION}.FULL.tar.gz" \
 && echo "${TRINITY_SHA256}  trinity.tar.gz" | sha256sum -c - \
 && tar -xzf trinity.tar.gz \
 && mv "trinityrnaseq-v${TRINITY_VERSION}" /opt/trinity \
 && rm /tmp/trinity-build/trinity.tar.gz

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

# Trinity 2.16.1 requires Salmon 1.x, not the independent Salmon app's 2.x.
# Pin this compatible package on both native architectures. APT revisions and
# unpinned transitive packages may drift or disappear from the live repository.
# Runtime curl is deliberately absent: assembly examples disable update checks.
RUN apt-get -o Acquire::Retries=3 update \
 && apt-get install -y --no-install-recommends \
      bash bzip2 ca-certificates default-jre-headless findutils gawk gzip \
      libgomp1 liburi-perl ncbi-blast+ perl procps python3 python3-numpy \
      salmon=1.10.2+ds1-1build2 samtools=1.19.2-1build2 \
      bowtie2=2.5.2-1 jellyfish=2.3.1-3build1 xz-utils \
 && rm -rf /var/lib/apt/lists/*

COPY --from=build /opt/trinity /opt/trinity
COPY docker/trinity-check.py /usr/local/libexec/trinity-check.py

ENV TRINITY_HOME=/opt/trinity
ENV PATH=/opt/trinity:/opt/trinity/util:/opt/trinity/Inchworm/bin:/opt/trinity/Chrysalis/bin:/opt/trinity/trinity-plugins/BIN:/opt/trinity/trinity-plugins/bamsifter:/opt/trinity/trinity-plugins/slclust/bin:/opt/trinity/trinity-plugins/COLLECTL/collectl:${PATH}
ENV LC_ALL=C.UTF-8
ENV TAFFISH_ENV=TAFFISH
ENV TAFFISH_NAME=trinity
ENV TAFFISH_VERSION=2.16.1
ENV TAFFISH_RELEASE=1
WORKDIR /tmp

# A small offline identity/linkage gate, not a fragile architecture-dependent
# assembly benchmark. Preserve command exit codes and exact version identity.
RUN python3 /usr/local/libexec/trinity-check.py identity
