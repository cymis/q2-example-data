ARG BASE_IMAGE="quay.io/qiime2/tiny:2026.7"
FROM ${BASE_IMAGE}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

LABEL org.opencontainers.image.title="qiime2-plugin-example-data"
LABEL org.opencontainers.image.description="Curated example datasets for learning Adagio with QIIME 2."
LABEL org.opencontainers.image.source="https://github.com/cymis/q2-example-data"
LABEL org.opencontainers.image.licenses="MIT"
LABEL io.qiime.release="2026.7"
LABEL io.qiime.plugin.name="example-data"
LABEL io.qiime.plugin.package="q2-example-data"

COPY . /tmp/q2-example-data

RUN conda run --name rachis-tiny-2026.7 \
      python -m pip install /tmp/q2-example-data --no-deps --no-build-isolation \
    && conda run --name rachis-tiny-2026.7 qiime dev refresh-cache \
    && conda run --name rachis-tiny-2026.7 qiime example-data --help \
    && rm -rf /tmp/q2-example-data \
    && conda clean -afy

ENV PATH="/opt/conda/envs/rachis-tiny-2026.7/bin:${PATH}"

CMD ["qiime", "example-data", "--help"]
