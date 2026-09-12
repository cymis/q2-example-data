"""QIIME 2 plugin registration for example-data."""

from qiime2.plugin import Plugin
from q2_types.metadata import ImmutableMetadata
from q2_types.per_sample_sequences import PairedEndSequencesWithQuality
from q2_types.sample_data import SampleData

from q2_example_data import __version__
from q2_example_data.actions import (
    get_gut_to_soil_demux,
    get_gut_to_soil_metadata,
)

plugin = Plugin(
    name="example-data",
    version=__version__,
    website="https://github.com/cymis/q2-example-data",
    package="q2_example_data",
    description="Curated example datasets for learning Adagio with QIIME 2.",
    short_description="Curated example datasets for learning Adagio with QIIME 2.",
)

plugin.methods.register_function(
    function=get_gut_to_soil_metadata,
    inputs={},
    parameters={},
    outputs=[
        ("metadata", ImmutableMetadata),
    ],
    output_descriptions={
        "metadata": "Sample metadata for the Gut-to-Soil tutorial dataset.",
    },
    input_descriptions={},
    parameter_descriptions={},
    name="Get Gut-to-Soil sample metadata",
    description="Download the Gut-to-Soil tutorial sample metadata, verify the pinned content, and return it as an immutable metadata artifact.",
)

plugin.methods.register_function(
    function=get_gut_to_soil_demux,
    inputs={},
    parameters={},
    outputs=[
        ("demux", SampleData[PairedEndSequencesWithQuality]),
    ],
    output_descriptions={
        "demux": "Demultiplexed paired-end sequences for the Gut-to-Soil tutorial dataset.",
    },
    input_descriptions={},
    parameter_descriptions={},
    name="Get Gut-to-Soil demultiplexed sequences",
    description="Download the Gut-to-Soil tutorial demultiplexed sequences, verify the pinned QIIME 2 archive, and return paired-end sequences with quality scores.",
)
