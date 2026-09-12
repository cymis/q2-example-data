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

Create the QIIME environment, then install this checkout into that environment.

```bash
conda env create -f environment-files/q2-example-data-tiny-dev.yml
conda activate q2-example-data-tiny-stable-dev
python -m pip install -e . --no-deps --no-build-isolation
python -m pytest
```

Configured local runtime hint: `conda activate qiime2-tiny-2026.1`.

The MCP server itself uses uv; plugin runtime checks intentionally execute with the conda environment's Python.

## Current status

- Modern `pyproject.toml` packaging with a `qiime2.plugins` entry point
- Versioning through `versioningit`, with a source-tree fallback version
- Development and release conda environment definitions
- Pytest, Ruff, Pyright, coverage, nox, and GitHub Actions scaffolding
- Two fixed, checksum-verified Gut-to-Soil source actions
- No custom transformers or new semantic types

The project is available under the MIT License.
