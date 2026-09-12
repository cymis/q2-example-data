"""Smoke tests for the empty plugin framework."""


def test_plugin_registration():
    from q2_example_data.plugin_setup import plugin

    assert plugin.name == "example-data"
    assert plugin.package == "q2_example_data"
    assert "get_gut_to_soil_metadata" in plugin.methods
    assert "get_gut_to_soil_demux" in plugin.methods
