FROM debian:bookworm-slim AS builder

ENV DEBIAN_FRONTEND=noninteractive
ENV OPAMROOT=/root/.opam
ENV OPAMYES=1

# Install build prerequisites
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    git \
    build-essential \
    cmake \
    pkg-config \
    libgmp-dev \
    libsqlite3-dev \
    libev-dev \
    libssl-dev \
    libffi-dev \
    liblmdb-dev \
    m4 \
    patch \
    unzip \
    curl \
    python3 \
    opam \
    && rm -rf /var/lib/apt/lists/*

# Install Rust toolchain
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain 1.80.1
ENV PATH="/root/.cargo/bin:${PATH}"

# Clone Octra Lite Node source
WORKDIR /build/octra
RUN git clone --branch main --single-branch https://github.com/octra-labs/lite_node.git .

# Initialize OPAM, install OCaml 4.14.2 and all project dependencies
RUN opam init --disable-sandboxing --bare -a -y \
    && opam switch create ocaml-system 4.14.2 \
    && opam install -y . --deps-only

# Build MCL cryptography library (ensure obj and lib directories exist)
WORKDIR /build/octra/mcl
RUN mkdir -p obj lib \
    && make -j$(nproc) MCL_FP_BIT=256 MCL_FR_BIT=256 lib/libmcl.a

# Build Octra Node Binaries
WORKDIR /build/octra
RUN opam exec -- dune build --profile release \
    bin/octra_node.exe \
    bin/octra_pvac_worker.exe \
    bin/octra_state_sync_client.exe \
    bin/octra_state_sync_manifest.exe \
    bin/bft_control_tx.exe

# ==============================================================================
# Runtime Stage
# ==============================================================================
FROM debian:bookworm-slim AS runtime

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libgmp10 \
    libsqlite3-0 \
    libev4 \
    libssl3 \
    liblmdb0 \
    curl \
    python3 \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Create dedicated operator user and directories
RUN useradd -m -u 1000 -s /bin/bash octra \
    && mkdir -p /opt/octra/bin /opt/octra/config /var/lib/octra /opt/octra/dashboard \
    && chown -R octra:octra /opt/octra /var/lib/octra

WORKDIR /opt/octra

# Copy binaries from builder
COPY --from=builder /build/octra/_build/default/bin/*.exe /opt/octra/bin/
COPY --from=builder /build/octra/config /opt/octra/config/
COPY --from=builder /build/octra/controls /opt/octra/controls/

# Copy dashboard and entrypoint
COPY entrypoint.sh /opt/octra/entrypoint.sh
COPY dashboard /opt/octra/dashboard/

RUN chmod +x /opt/octra/entrypoint.sh /opt/octra/bin/*.exe /opt/octra/controls/*.sh

EXPOSE 8080 9000 19000

VOLUME ["/var/lib/octra"]

USER octra

ENTRYPOINT ["/opt/octra/entrypoint.sh"]
