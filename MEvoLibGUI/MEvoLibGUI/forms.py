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

from django import forms
from nextflowApp.formats import INFERENCE_FORMAT_STR

from .settings import NEXTFLOW_UPLOADS_ROOT as ur


INPUT_CLASSES = "col-md-6 col-sm-9 col-12 mx-md-2 my-md-1 mt-3 form-control-md"


class AlignForm(forms.Form):
    aligned_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={"required": "True", "accept": INFERENCE_FORMAT_STR}),
    )


class AlignInfForm(forms.Form):
    unaligned_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={"required": "True", "accept": INFERENCE_FORMAT_STR}),
    )


class ParamInferenceForm(forms.Form):
    aligned_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={"required": "True", "accept": INFERENCE_FORMAT_STR}),
    )

    tool = forms.ChoiceField(
        initial={"tool": "FastTree"},
        widget=forms.RadioSelect(attrs={"required": "True"}),
        choices=[("fasttree", "FastTree"), ("raxml", "RAxML")],
        required=False,
    )  # Req

    output_file_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"required": "True", "class": INPUT_CLASSES}),
    )  # Req

    output_file_format = forms.CharField(
        initial="",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": INPUT_CLASSES,
                "placeholder": "By default, 'Newick' will be used",
            }
        ),
    )

    bootstraps = forms.IntegerField(
        initial={"bootstraps": 0},
        min_value=0,
        max_value=10,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": INPUT_CLASSES,
            }
        ),
    )

    arguments = forms.CharField(
        initial="ajjaja",
        max_length=150,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": INPUT_CLASSES,
                "placeholder": "By default, 'default' will be used.",
            }
        ),
    )
