# See the NOTICE file distributed with this work for additional information
# regarding copyright ownership.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from functools import reduce
import re

from Bio.Phylo._io import supported_formats
from Bio.SeqIO import _converter
from Bio.AlignIO import _FormatToWriter
from mevolib.align import _TOOL_TO_LIB as align_tools
from mevolib.cluster import _METHOD_TO_FUNC as cluster_tools
from mevolib.inference._FastTree import SPRT_INFILE_FORMATS as fasttree_formats
from mevolib.inference._RAxML import SPRT_INFILE_FORMATS as raxml_formats
from mevolib.inference import _PHYLO_TOOL_TO_LIB as inference_tools


# Allowed alignment output formats
ALIGN_OUTPUT = ["fasta"] + list(_FormatToWriter.keys())

# Alignment supported tools
ALIGN_TOOLS_LIST = list(align_tools.keys())

# Cluster supported tools
CLUSTER_TOOLS_LIST = list(cluster_tools.keys())

# Inference supported tools
INFERENCE_FORMAT_LIST = list(set(fasttree_formats).union(set(raxml_formats)))

INFERENCE_FORMAT_STR = str(reduce(lambda x, y: f"{x},{y}", map(lambda x: "." + x, INFERENCE_FORMAT_LIST)))

# Allowed inference output formats
INFERENCE_OUTPUT = list(supported_formats.keys())

# Inference supported tools
INFERENCE_TOOLS_LIST = list(inference_tools.keys())

TASK_ERROR = re.compile(r"^.+ terminated with an error .+$")

# Allowed inference input formats
VALID_INPUT_FILES = ["fasta"] + list(set(informat for informat, _ in _converter))

# Input format-output format valid tuples
VALID_CONVERSION_FILES = [(informat, outformat) for informat, outformat in _converter]

WORKFLOW_ERROR = re.compile(r"^.+ ERROR .+$")
