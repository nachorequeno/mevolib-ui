from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from pathlib import Path
import nextflow


from MEvoLibGUI.settings import (
    NEXTFLOW_PIPELINE_ROOT as pr,
    NEXTFLOW_DATA_ROOT as dr,
    NEXTFLOW_UPLOADS_ROOT as ur,
)
from MEvoLibGUI.forms import AlignForm, ParamInferenceForm, AlignInfForm
from .formats import (
    ALIGN_TOOLS_LIST as align_tools,
    INFERENCE_TOOLS_LIST as inference_tools,
    INFERENCE_FORMAT_STR as inference_input_accepted,
    VALID_INPUT_FILES as accepted_mimetypes,
)

from .models import (
    InferenceDocument,
    ParamInferenceDocument,
    AlignInferenceDocument,
    FullWorkflowDocument,
)

DEFAULT_INFERENCE_INPUT = ".fasta"


def home(request):
    al_form = AlignForm(request.POST)
    al_inf_form = AlignInfForm(request.POST)
    param_form = ParamInferenceForm(request.POST)

    return render(
        request,
        "nextflowApp/home.html",
        {
            "al_form": al_form,
            "param_form": param_form,
            "al_inf_form": al_inf_form,
            "align_tools": align_tools,
            "inference_tools": inference_tools,
            "inference_input_accepted": inference_input_accepted,
        },
    )


def simple_inference(request):
    if request.method == "POST":
        workflow_path = Path(pr).joinpath("inference", "main.nf")

        al_form = AlignForm(request.POST, request.FILES)

        if al_form.is_valid():
            if request.FILES["aligned_file"]:
                file_name = request.FILES["aligned_file"].name
                file_extension = file_name.split(".")[-1]

                aligned_file = InferenceDocument(docfile=request.FILES["aligned_file"])
                aligned_file.save()

                aln_file_path = Path(ur).joinpath("inference", file_name).absolute()

                execution = nextflow.run(
                    workflow_path, params={"aln_files": str(aln_file_path)}
                )

        processed_output = execution.stdout

    return HttpResponse(f"Execution's result: {processed_output}")


def parametrized_inference(request):
    #    {% render_field param_form.bootstraps class="text-warning" %}
    if request.method == "POST":
        workflow_path = Path(pr).joinpath("param_inference", "main.nf")

        al_form = AlignForm(request.POST, request.FILES)

        if al_form.is_valid():
            al_form.clean()
            if request.FILES["aligned_file"]:
                file_name = request.FILES["aligned_file"].name
                file_extension = file_name.split(".")[-1]

                aligned_file = ParamInferenceDocument(
                    docfile=request.FILES["aligned_file"]
                )

                aligned_file.save()

                aln_file_path = (
                    Path(ur).joinpath("param_inference", file_name).absolute()
                )

                tool = request.POST.get("tool")

                output_file_name = request.POST.get("output_file_name")
                output_file_name = output_file_name.replace(" ", "_")

                output_file_format = (
                    request.POST.get("output_file_format")
                    if request.POST.get("output_file_format")
                    else ""
                )

                bootstraps = (
                    request.POST.get("bootstraps")
                    if request.POST.get("bootstraps")
                    else ""
                )

                arguments = (
                    request.POST.get("arguments")
                    if request.POST.get("arguments")
                    else ""
                )

                total_query = get_inference_param_query(
                    aln_file_path,
                    tool,
                    output_file_name,
                    output_file_format,
                    bootstraps,
                    arguments,
                    file_extension,
                )

                execution = nextflow.run(
                    workflow_path,
                    params={
                        "total_query": total_query,
                        "output_name": output_file_name,
                    },
                )

        processed_output = execution.stdout

    return HttpResponse(f"Execution's result: {processed_output}")


def align_and_inference(request):
    if request.method == "POST":
        workflow_path = Path(pr).joinpath("align_inference", "main.nf")

        al_inf_form = AlignInfForm(request.POST, request.FILES)

        if al_inf_form.is_valid():
            if request.FILES["unaligned_file"]:
                
                file_name = request.FILES["unaligned_file"].name
                file_extension = file_name.split(".")[-1]

                unaligned_file = AlignInferenceDocument(
                    docfile=request.FILES["unaligned_file"]
                )
                unaligned_file.save();

                unaln_file_path = (
                    Path(ur).joinpath("align_inference", file_name).absolute()
                )

                execution = nextflow.run(
                    workflow_path, params={"unaln_files": str(unaln_file_path)}
                )

        processed_output = execution.stdout

    return HttpResponse(f"Execution's result: {processed_output}")


def full_workflow(request):
    
    if request.method == "POST":    # User submits the full workflow's form.
        
        input_file = "" 
        stage = ""
        
        if request.FILES:   # If fetch stage has not been selected, one of the others will have an input file to develop the
                            # workflow from, so it must be saved and it's path added to the query.
            
            if request.FILES.get("cluster_input", False):   # If the submitted form has a cluster file input,it's mimetype must be checked before
                                                            # saving it or starting the workflow.
                
                file_name = request.FILES["cluster_input"].name
                file_extension = file_name.split(".")[-1]

                if file_extension not in accepted_mimetypes:
                    return JsonResponse(    # If the mimetype is not supported, the client is notified with a message and the response emits
                                            # a status 400, that means an error has occured during the user's request.
                        {"cluster_file_err": f"The extension '.{file_extension}' cannot be used to perform a clustering stage on the workflow."},
                        status=400,
                    )

                else:
                    input_file = FullWorkflowDocument(docfile=request.FILES["cluster_input"])
                    input_file.save()
                    stage = "cluster"

            elif request.FILES.get("align_input", False):       # The same validation logic applies with alignment files...
                file_name = request.FILES["align_input"].name
                file_extension = file_name.split(".")[-1]

                if file_extension not in accepted_mimetypes:
                    return JsonResponse(
                        {
                            "align_file_err": f"The extension '.{file_extension}' cannot be used to perform an alignment stage on the workflow."
                        },
                        status=400,
                    )

                else:
                    input_file = FullWorkflowDocument(
                        docfile=request.FILES["align_input"]
                    )
                    input_file.save()
                    stage = "align"

            elif request.FILES.get("inference_input", False):   # ... and with inference ones.
                file_name = request.FILES["inference_input"].name
                file_extension = file_name.split(".")[-1]

                if file_extension not in accepted_mimetypes:
                    return JsonResponse(
                        {
                            "inference_file_err": f"The extension '.{file_extension}' cannot be used to perform am inference stage on the workflow."
                        },
                        status=400,
                    )

                else:
                    input_file = FullWorkflowDocument(
                        docfile=request.FILES["inference_input"]
                    )
                    input_file.save()
                    stage = "inference"

    query_file = ""

    if input_file:  # In case thw form worn a valid file that is already saved, it's reference stage must ne checked to 
                    # add it to the query as a parameter.
        file_path = Path(ur).joinpath("full_workflow", file_name).absolute()

        if stage == "cluster":
            query_file = "-ci"
        elif stage == "align":
            query_file = "-ai"
        elif stage == "inference":
            query_file = "-ii"

        query_file += f" {file_path}"

    buildFullQuery(request, query_file)

    return JsonResponse({}, status=200) # If there are no errors, the client side receives a JSON (empty, because it does not need any
                                        # further information) and a status 200, that means the request was successful.


def buildFullQuery(request, query_file):    # Function to construct the whole workflow query based on the data 
                                            # submitted in the form.
    total_query = ""
    req = request.POST

    if "add_fetch" in req and req["add_fetch"] == "on":  # Fetch stage selected.
        fetch_query = "-q "     # Whatever the user has selected, the first parameter is the query (-q).

        if req["fetch_query"]:  # The full query is already given.
            fetch_query += req["fetch_query"]

        else:   # The query must be built.
            fetch_query += f"{req['fetch_species']}[Organism]"  # In case query is not provided, 
                                                                # the species must be given.

            if req["fetch_seq_type"]:   # Apart from that, the sequence type and the reference sequence
                                        # may be present or not in the form, as they are optional values.
                fetch_query += f" AND {req['fetch_seq_type']}[PROP]"

            if req["fetch_ref_seq"]:
                fetch_query += f" AND {req['fetch_ref_seq']}[filter]"

        fetch_query += f" -fo {req['fetch_output_name']}"   # Also, the output file name has to be present.

        total_query += fetch_query

    if "add_cluster" in req and req["add_cluster"] == "on":  # Cluster stage selected
        cluster_query = ""

        if req["cluster_input_format"]: # In this case, the input file format is optional.
            cluster_query += f" -cif {req['cluster_input_format']}"

        cluster_query += f" -co {req['cluster_output']}"    # However, the output file name is needed (as
                                                            # in every single selected module).

        total_query += cluster_query

    if "add_align" in req and req["add_align"] == "on":  # Align stage selected
        align_query = ""

        align_query += f" -at {req['align_tool']}"   # In this stage, both, the alignment tool and the
                                                     # output file name are required.

        align_query += f" -ao {req['align_output']}"

        total_query += align_query

    if "add_inference" in req and req["add_inference"] == "on":  # Inference stage selected
        inference_query = ""

        if req["inference_input_format"]:   # The inference module may have plenty of non-required arguments,
                                            # such as the input/output file format or the arguments.
            inference_query += f" -iif {req['inference_input_format']}"

        if req["inference_output_format"]:
            inference_query += f" -iof {req['inference_output_format']}"

        if req["inference_arguments"]:
            inference_query += f" -ia {req['inference_arguments']}"
            
        # However, the inference tool, the output file name and the bootstraps must be specified.
        inference_query += f" -it {req['inference_tool']} -io {req['inference_output']} -ib {req['inference_bootstraps']} "

        total_query += inference_query

    total_query += query_file

    return total_query
