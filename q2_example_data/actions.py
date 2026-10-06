"""Action implementations for q2-example-data."""

from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from q2_types.per_sample_sequences import (
    PairedEndSequencesWithQuality,
    SingleLanePerSamplePairedEndFastqDirFmt,
)
from q2_types.sample_data import SampleData
from q2_types.feature_data import (FeatureData, Sequence, Taxonomy,
    TSVTaxonomyDirectoryFormat, DNASequencesDirectoryFormat)
from q2_types.feature_table import FeatureTable, Frequency, BIOMV210DirFmt
from qiime2 import Artifact, Metadata
from qiime2.metadata import MetadataFileError

from q2_example_data import __version__

GUT_TO_SOIL_METADATA_URL = (
    "https://gut-to-soil-tutorial.readthedocs.io/en/2026.4/"
    "data/gut-to-soil/sample-metadata.tsv"
)
GUT_TO_SOIL_METADATA_SHA256 = (
    "58ef2e8d198ce89e74c3a9b40f06d88066ec2f76918f857635dc4cd2a3f23a1a"
)
GUT_TO_SOIL_DEMUX_URL = (
    "https://gut-to-soil-tutorial.readthedocs.io/en/2026.4/data/gut-to-soil/demux.qza"
)
GUT_TO_SOIL_DEMUX_SHA256 = (
    "2e96e8a091e6b4ecf4635a10b18d3c4af2d2c4b98fd2772faeaf5bfe5f50b4a3"
)
GUT_TO_SOIL_FEATURE_TABLE_URL = (
    "https://gut-to-soil-tutorial.readthedocs.io/en/2026.4/data/gut-to-soil/asv-table.qza"
)
GUT_TO_SOIL_FEATURE_TABLE_SHA256 = (
    "98ebc5e3f3b784aa8283df68527aa132497fc4db6f5ae48fb4f89055ebbec63d"
)
GUT_TO_SOIL_FEATURE_DATA_SEQUENCE_URL = (
    "https://gut-to-soil-tutorial.readthedocs.io/en/2026.4/data/gut-to-soil/asv-seqs.qza"
)
GUT_TO_SOIL_FEATURE_DATA_SEQUENCE_SHA256 = (
    "bc7d1a9baf81eeea82444e7960d074e5ca08592efbf039e4dc0dbfa1119c10d7"
)
GUT_TO_SOIL_FEATURE_DATA_TAXONOMY_URL = (
    "https://gut-to-soil-tutorial.readthedocs.io/en/2026.4/data/gut-to-soil/taxonomy.qza"
)
GUT_TO_SOIL_FEATURE_DATA_TAXONOMY_SHA256 = (
    "6db1255c386c967878b67915c444593ce75ad61be6de6cc6ff7a080c1677eab9"
)

_DOWNLOAD_TIMEOUT_SECONDS = 60
_MAX_METADATA_DOWNLOAD_BYTES = 10 * 1024 * 1024
_MAX_DEMUX_DOWNLOAD_BYTES = 100 * 1024 * 1024
_USER_AGENT = f"q2-example-data/{__version__}"


def _download_pinned_file(
    *, url: str, expected_sha256: str, description: str, max_bytes: int
) -> bytes:
    request = Request(
        url,
        headers={"User-Agent": _USER_AGENT},
    )

    try:
        with urlopen(request, timeout=_DOWNLOAD_TIMEOUT_SECONDS) as response:
            payload = response.read(max_bytes + 1)
    except (HTTPError, URLError, TimeoutError) as error:
        raise RuntimeError(f"Failed to download the {description}.") from error

    if len(payload) > max_bytes:
        raise RuntimeError(
            f"The {description} download exceeded the "
            f"{max_bytes // (1024 * 1024)} MiB limit."
        )

    observed_sha256 = sha256(payload).hexdigest()
    if observed_sha256 != expected_sha256:
        raise RuntimeError(
            f"The {description} checksum did not match the "
            "version pinned by this plugin. "
            f"Expected {expected_sha256}, observed {observed_sha256}."
        )

    return payload


def get_gut_to_soil_metadata() -> Metadata:
    """Download and validate the gut-to-soil tutorial sample metadata."""
    payload = _download_pinned_file(
        url=GUT_TO_SOIL_METADATA_URL,
        expected_sha256=GUT_TO_SOIL_METADATA_SHA256,
        description="gut-to-soil sample metadata",
        max_bytes=_MAX_METADATA_DOWNLOAD_BYTES,
    )

    with TemporaryDirectory() as temp_dir:
        metadata_path = Path(temp_dir) / "sample-metadata.tsv"
        metadata_path.write_bytes(payload)
        try:
            return Metadata.load(metadata_path)
        except MetadataFileError as error:
            raise RuntimeError(
                "The downloaded gut-to-soil file is not valid QIIME 2 metadata."
            ) from error


def get_gut_to_soil_demux() -> SingleLanePerSamplePairedEndFastqDirFmt:
    """Download and validate the gut-to-soil demultiplexed sequences."""
    payload = _download_pinned_file(
        url=GUT_TO_SOIL_DEMUX_URL,
        expected_sha256=GUT_TO_SOIL_DEMUX_SHA256,
        description="gut-to-soil demultiplexed sequences",
        max_bytes=_MAX_DEMUX_DOWNLOAD_BYTES,
    )

    with TemporaryDirectory() as temp_dir:
        archive_path = Path(temp_dir) / "demux.qza"
        archive_path.write_bytes(payload)
        try:
            artifact = Artifact.load(archive_path)
        except (TypeError, ValueError, OSError) as error:
            raise RuntimeError(
                "The downloaded gut-to-soil demux file is not a valid QIIME 2 artifact."
            ) from error

        expected_type = SampleData[PairedEndSequencesWithQuality]
        if artifact.type != expected_type:
            raise RuntimeError(
                "The downloaded gut-to-soil demux artifact has type "
                f"{artifact.type}; expected {expected_type}."
            )

        return artifact.view(SingleLanePerSamplePairedEndFastqDirFmt)

def get_gut_to_soil_upstream_artifacts() -> (
    BIOMV210DirFmt, DNASequencesDirectoryFormat, TSVTaxonomyDirectoryFormat):
    payload_table = _download_pinned_file(
        url=GUT_TO_SOIL_FEATURE_TABLE_URL,
        expected_sha256=GUT_TO_SOIL_FEATURE_TABLE_SHA256,
        description="gut-to-soil asv table",
        max_bytes=_MAX_DEMUX_DOWNLOAD_BYTES,
    )
    payload_table_expected_type = FeatureTable[Frequency]
    payload_table_target_dirfmt = BIOMV210DirFmt

    payload_sequences = _download_pinned_file(
        url=GUT_TO_SOIL_FEATURE_DATA_SEQUENCE_URL,
        expected_sha256=GUT_TO_SOIL_FEATURE_DATA_SEQUENCE_SHA256,
        description="gut-to-soil asv sequences",
        max_bytes=_MAX_DEMUX_DOWNLOAD_BYTES,
    )
    payload_sequences_expected_type = FeatureData[Sequence]
    payload_sequences_target_dirfmt = DNASequencesDirectoryFormat

    payload_taxonomy = _download_pinned_file(
        url=GUT_TO_SOIL_FEATURE_DATA_TAXONOMY_URL,
        expected_sha256=GUT_TO_SOIL_FEATURE_DATA_TAXONOMY_SHA256,
        description="gut-to-soil asv taxonomy",
        max_bytes=_MAX_DEMUX_DOWNLOAD_BYTES,
    )
    payload_taxonomy_expected_type = FeatureData[Taxonomy]
    payload_taxonomy_target_dirfmt = TSVTaxonomyDirectoryFormat

    results = []
    for payload, expected_type, target_dirfmt in (
        [payload_table, payload_table_expected_type, payload_table_target_dirfmt],
        [payload_sequences, payload_sequences_expected_type, payload_sequences_target_dirfmt],
        [payload_taxonomy, payload_taxonomy_expected_type, payload_taxonomy_target_dirfmt]):
        with TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "artifact.qza"
            archive_path.write_bytes(payload)
            try:
                artifact = Artifact.load(archive_path)
            except (TypeError, ValueError, OSError) as error:
                raise RuntimeError(
                    "The downloaded file is not a valid QIIME 2 artifact."
                ) from error

            if artifact.type != expected_type:
                raise RuntimeError(
                    "The downloaded artifact has type "
                    f"{artifact.type}; {expected_type} was expected."
                )

            results.append(artifact.view(target_dirfmt))

    return tuple(results)
