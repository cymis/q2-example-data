"""Tests for the Gut-to-Soil demultiplexed-sequences source action."""

import gzip
from hashlib import sha256
from unittest.mock import MagicMock, patch
from urllib.error import URLError

import pytest
from qiime2 import Artifact
from q2_types.per_sample_sequences import (
    PairedEndSequencesWithQuality,
    SingleLanePerSamplePairedEndFastqDirFmt,
)
from q2_types.sample_data import SampleData

from q2_example_data import actions


def _mock_response(payload: bytes) -> MagicMock:
    response = MagicMock()
    response.__enter__.return_value = response
    response.read.return_value = payload
    return response


@pytest.fixture
def archive_payload(tmp_path) -> bytes:
    reads_dir = tmp_path / "reads"
    reads_dir.mkdir()
    records = {
        "sample_S1_L001_R1_001.fastq.gz": (
            b"@M00176:17:000000000-A3JHG:1:1101:15305:1388 1:N:0:1\nACGT\n+\nIIII\n"
        ),
        "sample_S1_L001_R2_001.fastq.gz": (
            b"@M00176:17:000000000-A3JHG:1:1101:15305:1388 2:N:0:1\nTGCA\n+\nIIII\n"
        ),
    }
    for filename, record in records.items():
        with gzip.open(reads_dir / filename, "wb") as fastq:
            fastq.write(record)

    artifact = Artifact.import_data(
        SampleData[PairedEndSequencesWithQuality],
        reads_dir,
        view_type="CasavaOneEightSingleLanePerSampleDirFmt",
    )
    archive_path = tmp_path / "demux.qza"
    artifact.save(archive_path)
    return archive_path.read_bytes()


def test_get_gut_to_soil_demux_returns_paired_end_format(archive_payload):
    expected_sha256 = sha256(archive_payload).hexdigest()
    response = _mock_response(archive_payload)

    with (
        patch.object(actions, "urlopen", return_value=response) as mocked_urlopen,
        patch.object(actions, "GUT_TO_SOIL_DEMUX_SHA256", expected_sha256),
    ):
        demux = actions.get_gut_to_soil_demux()

    assert isinstance(demux, SingleLanePerSamplePairedEndFastqDirFmt)
    request = mocked_urlopen.call_args.args[0]
    assert request.full_url == actions.GUT_TO_SOIL_DEMUX_URL
    assert request.get_header("User-agent") == actions._USER_AGENT
    response.read.assert_called_once_with(actions._MAX_DEMUX_DOWNLOAD_BYTES + 1)


def test_registered_method_returns_paired_end_artifact(archive_payload):
    from q2_example_data.plugin_setup import plugin

    expected_sha256 = sha256(archive_payload).hexdigest()

    with (
        patch.object(actions, "urlopen", return_value=_mock_response(archive_payload)),
        patch.object(actions, "GUT_TO_SOIL_DEMUX_SHA256", expected_sha256),
    ):
        results = plugin.methods["get_gut_to_soil_demux"]()

    assert results.demux.type == SampleData[PairedEndSequencesWithQuality]


def test_get_gut_to_soil_demux_rejects_changed_content(archive_payload):
    with patch.object(actions, "urlopen", return_value=_mock_response(archive_payload)):
        with pytest.raises(RuntimeError, match="checksum did not match"):
            actions.get_gut_to_soil_demux()


def test_get_gut_to_soil_demux_reports_network_failure():
    with patch.object(actions, "urlopen", side_effect=URLError("offline")):
        with pytest.raises(RuntimeError, match="Failed to download"):
            actions.get_gut_to_soil_demux()
