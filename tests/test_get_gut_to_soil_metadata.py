"""Tests for the Gut-to-Soil metadata source action."""

from hashlib import sha256
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.error import URLError

import pytest
from qiime2 import Metadata

from q2_example_data import actions


def _metadata_payload() -> bytes:
    return (Path(__file__).parent / "data" / "sample-metadata.tsv").read_bytes()


def _mock_response(payload: bytes) -> MagicMock:
    response = MagicMock()
    response.__enter__.return_value = response
    response.read.return_value = payload
    return response


def test_get_gut_to_soil_metadata_returns_metadata():
    payload = _metadata_payload()
    expected_sha256 = sha256(payload).hexdigest()
    response = _mock_response(payload)

    with (
        patch.object(actions, "urlopen", return_value=response) as mocked_urlopen,
        patch.object(actions, "GUT_TO_SOIL_METADATA_SHA256", expected_sha256),
    ):
        metadata = actions.get_gut_to_soil_metadata()

    assert isinstance(metadata, Metadata)
    assert set(metadata.ids) == {"gut-sample", "soil-sample"}
    assert metadata.get_column("sample-type").to_series().to_dict() == {
        "gut-sample": "gut",
        "soil-sample": "soil",
    }

    request = mocked_urlopen.call_args.args[0]
    assert request.full_url == actions.GUT_TO_SOIL_METADATA_URL
    assert request.get_header("User-agent") == actions._USER_AGENT
    assert mocked_urlopen.call_args.kwargs == {
        "timeout": actions._DOWNLOAD_TIMEOUT_SECONDS
    }
    response.read.assert_called_once_with(actions._MAX_METADATA_DOWNLOAD_BYTES + 1)


def test_registered_method_returns_immutable_metadata_artifact():
    from q2_example_data.plugin_setup import plugin

    payload = _metadata_payload()
    expected_sha256 = sha256(payload).hexdigest()

    with (
        patch.object(actions, "urlopen", return_value=_mock_response(payload)),
        patch.object(actions, "GUT_TO_SOIL_METADATA_SHA256", expected_sha256),
    ):
        results = plugin.methods["get_gut_to_soil_metadata"]()

    assert str(results.metadata.type) == "ImmutableMetadata"
    assert set(results.metadata.view(Metadata).ids) == {
        "gut-sample",
        "soil-sample",
    }


def test_get_gut_to_soil_metadata_rejects_changed_content():
    payload = _metadata_payload()

    with (
        patch.object(actions, "urlopen", return_value=_mock_response(payload)),
        pytest.raises(RuntimeError, match="checksum did not match"),
    ):
        actions.get_gut_to_soil_metadata()


def test_get_gut_to_soil_metadata_reports_network_failure():
    with patch.object(
        actions,
        "urlopen",
        side_effect=URLError("offline"),
    ), pytest.raises(RuntimeError, match="Failed to download"):
        actions.get_gut_to_soil_metadata()
