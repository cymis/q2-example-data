"""Action implementations for q2-example-data."""

from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from qiime2 import Artifact, Metadata
from qiime2.metadata import MetadataFileError
from q2_types.per_sample_sequences import (
    PairedEndSequencesWithQuality,
    SingleLanePerSamplePairedEndFastqDirFmt,
)
from q2_types.sample_data import SampleData

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
    """Download and validate the Gut-to-Soil tutorial sample metadata."""
    payload = _download_pinned_file(
        url=GUT_TO_SOIL_METADATA_URL,
        expected_sha256=GUT_TO_SOIL_METADATA_SHA256,
        description="Gut-to-Soil sample metadata",
        max_bytes=_MAX_METADATA_DOWNLOAD_BYTES,
    )

    with TemporaryDirectory() as temp_dir:
        metadata_path = Path(temp_dir) / "sample-metadata.tsv"
        metadata_path.write_bytes(payload)
        try:
            return Metadata.load(metadata_path)
        except MetadataFileError as error:
            raise RuntimeError(
                "The downloaded Gut-to-Soil file is not valid QIIME 2 metadata."
            ) from error


def get_gut_to_soil_demux() -> SingleLanePerSamplePairedEndFastqDirFmt:
    """Download and validate the Gut-to-Soil demultiplexed sequences."""
    payload = _download_pinned_file(
        url=GUT_TO_SOIL_DEMUX_URL,
        expected_sha256=GUT_TO_SOIL_DEMUX_SHA256,
        description="Gut-to-Soil demultiplexed sequences",
        max_bytes=_MAX_DEMUX_DOWNLOAD_BYTES,
    )

    with TemporaryDirectory() as temp_dir:
        archive_path = Path(temp_dir) / "demux.qza"
        archive_path.write_bytes(payload)
        try:
            artifact = Artifact.load(archive_path)
        except (TypeError, ValueError, OSError) as error:
            raise RuntimeError(
                "The downloaded Gut-to-Soil demux file is not a valid QIIME 2 artifact."
            ) from error

        expected_type = SampleData[PairedEndSequencesWithQuality]
        if artifact.type != expected_type:
            raise RuntimeError(
                "The downloaded Gut-to-Soil demux artifact has type "
                f"{artifact.type}; expected {expected_type}."
            )

        return artifact.view(SingleLanePerSamplePairedEndFastqDirFmt)
