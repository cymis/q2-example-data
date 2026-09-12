# q2-example-data

Curated example datasets for learning Adagio with QIIME 2.

This repository contains typed source actions for the datasets used by Adagio
tutorial pipelines.

The `get-gut-to-soil-metadata` action downloads the versioned
Gut-to-Soil sample metadata, verifies its checksum, validates it as QIIME 2
metadata, and returns an `ImmutableMetadata` artifact.

The `get-gut-to-soil-demux` action downloads the versioned demultiplexed
paired-end reads, verifies and validates the QIIME 2 archive, and returns a
`SampleData[PairedEndSequencesWithQuality]` artifact.

## Planned action boundary

Each future action will expose a fixed QIIME 2 output signature. A dataset
choice parameter may select among multiple datasets only when every choice has
the same output types. URLs and checksums will live in a versioned registry
rather than in user-authored pipelines.

No new semantic types or formats are planned for the initial actions. They will
reuse standard QIIME 2 types such as `SampleData[SequencesWithQuality]`,
`SampleData[PairedEndSequencesWithQuality]`, and `ImmutableMetadata`.

## Development environment

Run the test suite inside the same QIIME 2 base container used for publishing.

```bash
docker run --rm -v "$PWD:/work" -w /work quay.io/qiime2/tiny:2026.7 \
  bash -lc 'conda run -n rachis-tiny-2026.7 python -m pip install pytest ruff && \
  conda run -n rachis-tiny-2026.7 python -m pip install -e . --no-deps --no-build-isolation && \
  conda run -n rachis-tiny-2026.7 python -m pytest && \
  conda run -n rachis-tiny-2026.7 ruff check .'
```

## Current status

- Modern `pyproject.toml` packaging with a `qiime2.plugins` entry point
- Versioning through `versioningit`, with a source-tree fallback version
- Reproducible development and release container based on QIIME 2 2026.7
- Pytest, Ruff, Pyright, coverage, nox, and GitHub Actions scaffolding
- Two fixed, checksum-verified Gut-to-Soil source actions
- No custom transformers or new semantic types

The project is available under the MIT License.
