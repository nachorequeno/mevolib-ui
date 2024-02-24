from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from pathlib import Path
from celery.result import AsyncResult
import io, nextflow, random, zipfile
import random

from MEvoLibGUI.tasks import run_workflow
from MEvoLibGUI.settings import (
    NEXTFLOW_PIPELINE_ROOT as pr,
    NEXTFLOW_DATA_ROOT as dr,
    NEXTFLOW_UPLOADS_ROOT as ur,
    WORKFLOW_OUTPUT
)
from MEvoLibGUI.forms import AlignForm, ParamInferenceForm, AlignInfForm
from .formats import (
    ALIGN_TOOLS_LIST as align_tools,
    INFERENCE_TOOLS_LIST as inference_tools,
    INFERENCE_FORMAT_STR as inference_input_accepted,
    VALID_INPUT_FILES as accepted_mimetypes,
    VALID_CONVERSION_FILES as allowed_conversions
)

from .models import (
    InferenceDocument,
    ParamInferenceDocument,
    AlignInferenceDocument,
    FullWorkflowDocument,
)


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
            "accepted_mimetypes": accepted_mimetypes
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
            if request.FILES["unaligned_file"]: # If the form is valid and there is a file on it, it is saved and it's path got.
                
                file_name = request.FILES["unaligned_file"].name

                unaligned_file = AlignInferenceDocument(
                    docfile=request.FILES["unaligned_file"]
                )
                unaligned_file.save();

                unaln_file_path = (
                    Path(ur).joinpath("align_inference", file_name).absolute()
                )
                
                task_hash = str(random.getrandbits(32))     # A hash to provide a folder name concurrently to the task.
                
                params={"unaln_files": str(unaln_file_path), "output_name": task_hash}
                task = run_workflow.delay(str(workflow_path), params)   # After loading all the parameters, a celery task, which
                                                                        # will run the Nextflow workflow asynchronously, is called.

                return JsonResponse({"task_id": task.id, "task_hash": task_hash}, status=200)


def full_workflow(request):
    
    if request.method == "POST":    # User submits the full workflow's form.
        
        input_file = "" 
        stage = ""
        
        if request.FILES:   # If fetch stage has not been selected, one of the others will have an input file to develop the
                            # workflow from, so it must be saved and it's path added to the query.
            
            if request.FILES.get("cluster_input", False):   # If the submitted form has a cluster file input,it's input and 
                                                            # output mimetype must be checked before saving it or starting the workflow.
    
                file_name = request.FILES["cluster_input"].name                                             
                input_file_format = request.POST['cluster_input_format']
                output_file_format = "fasta"
                
                if request.POST["cluster_output_format"]:
                    output_file_format = request.POST["cluster_output_format"]

                if input_file_format != "fasta" and (input_file_format, output_file_format) not in allowed_conversions:
                    return JsonResponse(    # The reason behind this check is that MEvoLib can make conversions between certain file
                                            # types if the input file is not supported, so given that ".fasta" is the most common, if
                                            # it's input is not ".fasta" and it cannot be converted, the user must be prevented to
                                            # avoid launching a workflow that can lead to error.
                                            
                        {"cluster_file_err": f"The file conversion from '.{input_file_format}' to '.{output_file_format}' is not supported. Please, select another files and try again."},
                        status=400,
                    )

                else:
                    input_file = FullWorkflowDocument(docfile=request.FILES["cluster_input"])
                    input_file.save()
                    stage = "cluster"

            elif request.FILES.get("align_input", False):       # The same validation logic applies with alignment files...
                
                file_name = request.FILES["align_input"].name
                input_file_format = request.POST['align_input_format']
                output_file_format = "fasta"
                
                if request.POST["align_output_format"]:
                    output_file_format = request.POST["align_output_format"]

                if input_file_format != "fasta" and (input_file_format, output_file_format) not in allowed_conversions:
                    return JsonResponse(    
                        {"align_file_err": f"The file conversion from '.{input_file_format}' to '.{output_file_format}' is not supported. Please, select another files and try again."},
                        status=400,
                    )

                else:
                    input_file = FullWorkflowDocument(docfile=request.FILES["align_input"])
                    input_file.save()
                    stage = "align"

            elif request.FILES.get("inference_input", False):   # ... and with inference ones.
                
                file_name = request.FILES["inference_input"].name
                input_file_format = request.POST['inference_input_format']
                output_file_format = "newick"
                
                if request.POST["inference_output_format"]:
                    output_file_format = request.POST["inference_output_format"]

                if input_file_format != "fasta" and (input_file_format, output_file_format) not in allowed_conversions:
                    return JsonResponse(   
                        {"inference_file_err": f"The file conversion from '.{input_file_format}' to '.{output_file_format}' is not supported. Please, select another files and try again."},
                        status=400,
                    )

                else:
                    input_file = FullWorkflowDocument(
                        docfile=request.FILES["inference_input"]
                    )
                    input_file.save()
                    stage = "inference"

    query_file = ""

    if input_file:  # In case the form worn a valid file that is already saved, it's reference stage must ne checked to 
                    # add it to the query as a parameter; alongside it's input file format.
        file_path = Path(ur).joinpath("full_workflow", file_name).absolute()

        if stage == "cluster":
            query_file = f" -cif {request.POST['cluster_input_format']} -ci"
        elif stage == "align":
            query_file = f" -aif {request.POST['align_input_format']} -ai"
        elif stage == "inference":
            query_file = f" -iif {request.POST['inference_input_format']} -ii"

        query_file += f" {file_path}"

    full_query = buildFullQuery(request, query_file, stage)

    return JsonResponse({}, status=200) # If there are no errors, the client side receives a JSON (empty, because it does not need any
                                        # further information) and a status 200, that means the request was successful.

def check_task_status(request):             # This function provides the client a way to know the status of their task, if requested any.
    task_id = request.GET.get("task_id")
    
    if task_id:
        # Check the status of the Celery task
        task = AsyncResult(task_id)
        return JsonResponse({'task_status': task.status}, status=200)
    else:
        return JsonResponse({'error': 'Task ID not provided'}, status=400)

def download_task_zip(request):    

    folder_path = Path(WORKFLOW_OUTPUT).joinpath(request.GET.get("task_hash")).absolute()

    zip_buffer = io.BytesIO() # Fisrt, a zip buffer is created to allocate the following zip contents.

    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file: # Next, a ZipFile object is created, to store that
                                                                             # information in memory

        for entry in folder_path.rglob("*"):   # It iterates through all the files/subdirectories within the specified folder and
                                               # adds them to the zip file.
            zip_file.write(entry, entry.relative_to(folder_path))


    zip_buffer.seek(0)      # The position of the buffer's file pointer is resetted to point to the start.

    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip', status=200) # The zip response is prepared and
                                                                                               # given to the user. 
    response['Content-Disposition'] = 'attachment; filename="folder_download.zip"'

    return response

def buildFullQuery(request, query_file, stage):    # Function to construct the whole workflow query based on the data 
                                            # submitted in the form.
    total_query = {}
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

        total_query["fetch_query"] = fetch_query

    if "add_cluster" in req and req["add_cluster"] == "on":  # Cluster stage selected
        cluster_query = ""

        cluster_query += f"-co {req['cluster_output']}"    # However, the output file name is needed (as
                                                            # in every single selected module).

        if req["cluster_output_format"]:
            cluster_query += f" -cof {req['cluster_output_format']}"
            
        if stage == "cluster":
            cluster_query += query_file
            
        total_query["cluster_query"] = cluster_query

    if "add_align" in req and req["add_align"] == "on":  
                                                     # Align stage selected
                                                     # In this stage, both, the alignment tool and the
                                                     # output file name are required.
                                                     
        align_query = f"-ao {req['align_output']} -at {req['align_tool']}"
        
        if req["align_output_format"]:
            align_query += f" -aof {req['align_output_format']}"

        if stage == "align":
            align_query += query_file
            
        total_query["align_query"] = align_query    

    if "add_inference" in req and req["add_inference"] == "on":  # Inference stage selected
        inference_query = ""

                                            # The inference module may have plenty of non-required arguments,
                                            # such as the output file format or the arguments.
        if req["inference_output_format"]:
            inference_query += f"-iof {req['inference_output_format']} "

        if req["inference_arguments"]:
            inference_query += f"-ia {req['inference_arguments']} "
        
        # However, the inference tool, the output file name and the bootstraps must be specified.
        inference_query += f"-it {req['inference_tool']} -io {req['inference_output']} -ib {req['inference_bootstraps']}"

        if stage == "inference":
            inference_query += query_file
            
        total_query["inference_query"] = inference_query     

    return total_query
