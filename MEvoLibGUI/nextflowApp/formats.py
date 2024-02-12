from functools import reduce

from Bio.SeqIO import _converter

from MEvoLib.mevolib.align import _TOOL_TO_LIB as align_tools
from MEvoLib.mevolib.inference._FastTree import SPRT_INFILE_FORMATS as fasttree_formats
from MEvoLib.mevolib.inference._RAxML import SPRT_INFILE_FORMATS as raxml_formats
from MEvoLib.mevolib.inference import _PHYLO_TOOL_TO_LIB as inference_tools

ALIGN_TOOLS_LIST = list(align_tools.keys())     # Alignent supported tools.

INFERENCE_FORMAT_LIST = list(set(fasttree_formats).union(set(raxml_formats)))   # Inference supported tools.

INFERENCE_FORMAT_STR = str(
    reduce(lambda x, y: f"{x},{y}", map(lambda x: "." + x, INFERENCE_FORMAT_LIST))
)


INFERENCE_TOOLS_LIST = list(inference_tools.keys())
"""
VALID_INPUT_FILES = [   # AlignIO and SeqIO valid file formats. Bio.SeqIO._FormatToIterator Keys // ("<format>", "fasta") in Bio.SeqIO._converter
    "clustal",
    "emboss",
    "fasta",
    "fasta-m10",
    "ig",
    "msf",
    "nexus",
    "phylip",
    "phylip-sequential",
    "phylip-relaxed",
    "stockholm",
    "mauve",
]
"""

VALID_INPUT_FILES = ['fasta'] + list(set(informat for informat, _ in _converter))

VALID_CONVERSION_FILES = list((informat,outformat) for informat,outformat in _converter)
