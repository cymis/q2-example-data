"""QIIME 2 plugin registration for example-data."""

from q2_types.metadata import ImmutableMetadata
from q2_types.per_sample_sequences import PairedEndSequencesWithQuality
from q2_types.sample_data import SampleData
from q2_types.feature_data import FeatureData, Sequence, Taxonomy
from q2_types.feature_table import FeatureTable, Frequency
from qiime2.plugin import Plugin

from q2_example_data import __version__
from q2_example_data.actions import (
    get_gut_to_soil_demux,
    get_gut_to_soil_metadata,
    get_gut_to_soil_upstream_artifacts
)

_G2S_TUTORIAL_URL = "https://amplicon-docs.qiime2.org/en/stable/tutorials/gut-to-soil/"

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
        "metadata": "The sample metadata used in the gut-to-soil tutorial",
    },
    input_descriptions={},
    parameter_descriptions={},
    name="Get gut-to-soil sample metadata",
    description=f"Download the gut-to-soil tutorial sample metadata, verify the pinned content, and return it as an immutable metadata artifact. For usage examples, see {_G2S_TUTORIAL_URL}.",
)

plugin.methods.register_function(
    function=get_gut_to_soil_demux,
    inputs={},
    parameters={},
    outputs=[
        ("demux", SampleData[PairedEndSequencesWithQuality]),
    ],
    output_descriptions={
        "demux": "The demultiplexed paired-end sequences used in the gut-to-soil tutorial.",
    },
    input_descriptions={},
    parameter_descriptions={},
    name="Get gut-to-soil demultiplexed sequences",
    description=f"Download the gut-to-soil tutorial demultiplexed sequences, verify the pinned archive, and return the corresponding artifact. For usage examples, see {_G2S_TUTORIAL_URL}.",
)

plugin.methods.register_function(
    function=get_gut_to_soil_upstream_artifacts,
    inputs={},
    parameters={},
    outputs=[
        ("asv_table", FeatureTable[Frequency]),
        ("asv_sequences", FeatureData[Sequence]),
        ("asv_taxonomy", FeatureData[Taxonomy]),
    ],
    output_descriptions={
        "asv_table": "The ASV table generated in the gut-to-soil tutorial, as output from DADA2.",
        "asv_sequences": "The ASV sequences generated in the gut-to-soil tutorial, as output from DADA2.",
        "asv_taxonomy": "The ASV taxonomy generated in the gut-to-soil tutorial.",
    },
    input_descriptions={},
    parameter_descriptions={},
    name="Get gut-to-soil upstream artifacts.",
    description=f"Download the three primary outputs of the upstream analysis steps of the gut-to-soil tutorial and verify their checksums. For usage examples, see {_G2S_TUTORIAL_URL}.",
)
