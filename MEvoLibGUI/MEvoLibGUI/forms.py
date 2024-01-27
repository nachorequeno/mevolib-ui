from django import forms
from .settings import NEXTFLOW_UPLOADS_ROOT as ur

from nextflowApp.formats import INFERENCE_FORMAT_STR

INPUT_CLASSES = "col-md-6 col-sm-9 col-12 mx-md-2 my-md-1 mt-3 form-control-md"


class AlignForm(forms.Form):
    aligned_file = forms.FileField(
        required=False,
        widget=forms.FileInput(
            attrs={"required": "True", "accept": INFERENCE_FORMAT_STR}
        ),
    )


class AlignInfForm(forms.Form):
    unaligned_file = forms.FileField(
        required=False,
        widget=forms.FileInput(
            attrs={"required": "True", "accept": INFERENCE_FORMAT_STR}
        ),
    )


class ParamInferenceForm(forms.Form):
    aligned_file = forms.FileField(
        required=False,
        widget=forms.FileInput(
            attrs={"required": "True", "accept": INFERENCE_FORMAT_STR}
        ),
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
