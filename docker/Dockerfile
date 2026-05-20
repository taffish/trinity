FROM ubuntu:24.04 AS build

ARG TRINITY_VERSION=2.15.2
ARG TRINITY_TAG=Trinity-v2.15.2
ARG TRINITY_SHA256=baab87e4878ad097e265c46de121414629bf88fa9342022baae5cac12432a15c

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ca-certificates \
      curl \
      build-essential \
      autoconf \
      automake \
      cmake \
      git \
      libtool \
      pkg-config \
      zlib1g-dev \
      libbz2-dev \
      liblzma-dev \
      libcurl4-openssl-dev \
      libssl-dev \
      libncurses-dev \
      default-jdk-headless \
      perl \
      python3 \
      rsync \
      file \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp/build

RUN curl -fsSL -o trinityrnaseq.tar.gz \
      "https://github.com/trinityrnaseq/trinityrnaseq/releases/download/${TRINITY_TAG}/trinityrnaseq-v${TRINITY_VERSION}.FULL.tar.gz" \
 && echo "${TRINITY_SHA256}  trinityrnaseq.tar.gz" | sha256sum -c - \
 && tar -xzf trinityrnaseq.tar.gz \
 && mv "trinityrnaseq-v${TRINITY_VERSION}" /opt/trinity \
 && rm -rf /tmp/build

RUN sed -i 's/-m64 //g; s/ -m64//g' \
      /opt/trinity/Inchworm/CMakeLists.txt \
      /opt/trinity/Chrysalis/CMakeLists.txt \
      /opt/trinity/trinity-plugins/ParaFly/configure \
      /opt/trinity/trinity-plugins/ParaFly/Makefile.in \
      /opt/trinity/trinity-plugins/ParaFly/src/Makefile.in \
 && perl -0pi -e 's/git submodule init && git submodule update/if [ -d .git ]; then git submodule init && git submodule update; fi/' \
      /opt/trinity/trinity-plugins/bamsifter/build_htslib.sh \
 && sed -i 's#autoheader#autoreconf -i#; /autoconf/d' \
      /opt/trinity/trinity-plugins/bamsifter/build_htslib.sh \
 && echo '#define HTSCODECS_VERSION_TEXT "1.1.1"' \
      > /opt/trinity/trinity-plugins/bamsifter/htslib/htscodecs/htscodecs/version.h

WORKDIR /opt/trinity

RUN make \
 && make plugins \
 && sh ./util/support_scripts/trinity_install_tests.sh \
 && sh ./util/support_scripts/plugin_install_tests.sh

RUN ./Trinity --version 2>&1 | grep -F "Trinity version: ${TRINITY_TAG}" >/dev/null \
 && (./Trinity --help 2>&1 || true) | grep -F "Trinity --seqType" >/dev/null \
 && test -x /opt/trinity/Inchworm/bin/inchworm \
 && test -x /opt/trinity/Chrysalis/bin/Chrysalis \
 && test -x /opt/trinity/trinity-plugins/BIN/ParaFly \
 && test -x /opt/trinity/trinity-plugins/BIN/seqtk-trinity \
 && test -x /opt/trinity/trinity-plugins/bamsifter/_sift_bam_max_cov

FROM ubuntu:24.04

ARG TRINITY_VERSION=2.15.2
ARG TRINITY_TAG=Trinity-v2.15.2

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      bash \
      bzip2 \
      default-jre-headless \
      findutils \
      gawk \
      gzip \
      libgomp1 \
      liburi-perl \
      ncbi-blast+ \
      perl \
      procps \
      python3 \
      python3-numpy \
      salmon \
      samtools \
      bowtie2 \
      jellyfish \
      xz-utils \
 && rm -rf /var/lib/apt/lists/*

COPY --from=build /opt/trinity /opt/trinity

ENV TRINITY_HOME=/opt/trinity
ENV PATH=/opt/trinity:/opt/trinity/util:/opt/trinity/Inchworm/bin:/opt/trinity/Chrysalis/bin:/opt/trinity/trinity-plugins/BIN:/opt/trinity/trinity-plugins/bamsifter:/opt/trinity/trinity-plugins/slclust/bin:/opt/trinity/trinity-plugins/COLLECTL/collectl:${PATH}
ENV LC_ALL=C.UTF-8
WORKDIR /root

ENV TAFFISH_ENV=TAFFISH
ENV TAFFISH_NAME=trinity

RUN Trinity --version 2>&1 | grep -F "Trinity version: ${TRINITY_TAG}" >/dev/null \
 && (Trinity --help 2>&1 || true) | grep -F "Trinity --seqType" >/dev/null \
 && perl -MDB_File -MURI::Escape -e1 \
 && python3 -c 'import numpy' \
 && for tool in Trinity TrinityStats.pl align_and_estimate_abundance.pl insilico_read_normalization.pl ParaFly seqtk-trinity inchworm Chrysalis QuantifyGraph GraphFromFasta ReadsToTranscripts bamsifter slclust collectl bowtie2 bowtie2-build jellyfish samtools salmon blastn makeblastdb java perl python3 bash gzip bzip2 xz; do command -v "$tool" >/dev/null; done \
 && ! ldd /opt/trinity/Inchworm/bin/inchworm 2>&1 | grep -F "not found" >/dev/null \
 && ! ldd /opt/trinity/Chrysalis/bin/Chrysalis 2>&1 | grep -F "not found" >/dev/null \
 && ! ldd /opt/trinity/trinity-plugins/BIN/ParaFly 2>&1 | grep -F "not found" >/dev/null \
 && ! ldd /opt/trinity/trinity-plugins/bamsifter/_sift_bam_max_cov 2>&1 | grep -F "not found" >/dev/null
