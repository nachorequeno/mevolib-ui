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

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from pathlib import Path
from celery.result import AsyncResult
import io, random, zipfile
import random

from MEvoLibGUI.tasks import run_workflow
from MEvoLibGUI.settings import (
    FULL_WORKFLOW_ROUTE as full_wf_route,
    NEXTFLOW_UPLOADS_ROOT as ur,
    WORKFLOW_OUTPUT as wf_output,
)

from .formats import (
    ALIGN_OUTPUT as align_output_mimetypes,
    ALIGN_TOOLS_LIST as align_tools,
    CLUSTER_TOOLS_LIST as cluster_tools,
    INFERENCE_TOOLS_LIST as inference_tools,
    INFERENCE_FORMAT_STR as inference_input_accepted,
    INFERENCE_OUTPUT as inference_output_mimetypes,
    VALID_INPUT_FILES as accepted_mimetypes,
    VALID_CONVERSION_FILES as allowed_conversions,
)

from .models import FullWorkflowDocument


def home(request):

    return render(
        request,
        "nextflowApp/home.html",
        {
            "accepted_align_output_mimetypes": align_output_mimetypes,
            "accepted_inference_output_mimetypes": inference_output_mimetypes,
            "accepted_input_mimetypes": accepted_mimetypes,
            "align_tools": align_tools,
            "cluster_tools": cluster_tools,
            "inference_input_accepted": inference_input_accepted,
            "inference_tools": inference_tools,
        },
    )


def full_workflow(request):

    if request.method == "POST":  # User submits the full workflow's form.

        input_file = ""
        stage = ""

        if (
            request.FILES
        ):  # If fetch stage has not been selected, one of the others will have an input file to develop the
            # workflow from, so it must be saved and it's path added to the query.

            if request.FILES.get(
                "cluster_input", False
            ):  # If the submitted form has a cluster file input,it's input and
                # output mimetype must be checked before saving it or starting the workflow.

                file_name = request.FILES["cluster_input"].name
                input_file_format = request.POST["cluster_input_format"]

                input_file = FullWorkflowDocument(docfile=request.FILES["cluster_input"])
                input_file.save()
                stage = "cluster"

            elif request.FILES.get(
                "align_input", False
            ):  # The same validation logic applies with alignment files...

                file_name = request.FILES["align_input"].name
                input_file_format = request.POST["align_input_format"]

                if input_file_format != "fasta" and (input_file_format, "fasta") not in allowed_conversions:
                    return JsonResponse(
                        {
                            "align_file_err": f"The file conversion from '.{input_file_format}' to '.fasta' is not supported. Please, select another format and try again."
                        },
                        status=400,
                    )

                else:
                    input_file = FullWorkflowDocument(docfile=request.FILES["align_input"])
                    input_file.save()
                    stage = "align"

            elif request.FILES.get("inference_input", False):  # ... and with inference ones.

                file_name = request.FILES["inference_input"].name
                input_file_format = request.POST["inference_input_format"]

                if input_file_format != "fasta" and (input_file_format, "fasta") not in allowed_conversions:
                    return JsonResponse(
                        {
                            "inference_file_err": f"The file conversion from '.{input_file_format}' to '.fasta' is not supported. Please, select another format and try again."
                        },
                        status=400,
                    )

                else:
                    input_file = FullWorkflowDocument(docfile=request.FILES["inference_input"])
                    input_file.save()
                    stage = "inference"

    params = {}

    task_hash = str(random.getrandbits(32))  # A hash to provide a folder name concurrently to the task.
    output_name = ""

    if (
        input_file
    ):  # In case the form worn a valid file that is already saved, it's reference stage must ne checked to
        # add it to the query as a parameter; alongside it's input file format.
        file_path = Path(ur).joinpath("full_workflow", file_name).absolute()
        params["input_file"] = str(file_path)

        if stage == "cluster":
            params["input_format"] = request.POST["cluster_input_format"]
            output_name = request.POST["cluster_output"]

        elif stage == "align":
            params["input_format"] = request.POST["align_input_format"]
            output_name = request.POST["align_output"]

        elif stage == "inference":
            params["input_format"] = request.POST["inference_input_format"]
            output_name = request.POST["inference_output"]

    else:
        output_name = request.POST["fetch_output_name"]

    params["output_dir"] = str(Path(wf_output).joinpath(task_hash))

    getQueryParams(request, params)

    workflow_path = str(Path(full_wf_route))

    task = run_workflow.delay(
        str(workflow_path), params
    )  # After loading all the parameters, a celery task, which
    # will run the Nextflow workflow asynchronously, is called.
    return JsonResponse(
        {"task_id": task.id, "task_hash": task_hash, "zip_name": output_name}, status=200
    )  # If there are no errors, the client side receives a JSON fill with
    # the task information and a status 200, that means the request was
    # successful.


def check_task_status(
    request,
):  # This function provides the client a way to know the status of their task, if requested any.
    task_id = request.GET.get("task_id")

    if task_id:
        # Check the status of the Celery task
        task = AsyncResult(task_id)
        return JsonResponse({"task_status": task.status}, status=200)
    else:
        return JsonResponse({"error": "Task ID not provided"}, status=400)


def download_task_zip(request):

    folder_path = Path(wf_output).joinpath(request.GET.get("task_hash")).absolute()

    zip_buffer = io.BytesIO()  # Fisrt, a zip buffer is created to allocate the following zip contents.

    with zipfile.ZipFile(
        zip_buffer, "w", zipfile.ZIP_DEFLATED
    ) as zip_file:  # Next, a ZipFile object is created, to store that
        # information in memory

        for entry in folder_path.rglob(
            "*"
        ):  # It iterates through all the files/subdirectories within the specified folder and
            # adds them to the zip file.
            zip_file.write(entry, entry.relative_to(folder_path))

    zip_buffer.seek(0)  # The position of the buffer's file pointer is resetted to point to the start.

    response = HttpResponse(
        zip_buffer.getvalue(), content_type="application/zip", status=200
    )  # The zip response is prepared and
    # given to the user.
    response["Content-Disposition"] = 'attachment; filename="folder_download.zip"'

    return response


def getQueryParams(request, params):  # Function to construct the whole workflow query based on the data
    # submitted in the form.

    req = request.POST

    if "add_fetch" in req and req["add_fetch"] == "on":  # Fetch stage selected.

        params["max_seqs"] = "3000"
        
        if req["fetch_query"]:  # The full query is already given.
            params["query"] = req["fetch_query"]

        else:  # The query must be built.
            params["species"] = req["fetch_species"]  # In case query is not provided,
            # the species must be given.

            if req["fetch_seq_type"]:  # Apart from that, the sequence type and the reference sequence
                # may be present or not in the form, as they are optional values.
                params["seq_type"] = req["fetch_seq_type"]

            if "ref_seq" in req and req["ref_seq"]:
                params["refseq"] = "True"

    if "add_cluster" in req and req["add_cluster"] == "on":  # Cluster stage selected.

        params["cluster_tool"] = req["cluster_tool"]  # the clustering tool.

    if "add_align" in req and req["add_align"] == "on":
        # Align stage selected.
        # In this stage, both, the alignment tool and the
        # output file name are required.
        params["align_tool"] = req["align_tool"]

        if req["align_output_format"]:
            params["align_out_format"] = req["align_output_format"]

        if req["align_arguments"]:
            params["align_args"] = req["align_arguments"]

    if "add_inference" in req and req["add_inference"] == "on":  # Inference stage selected

        # The inference module may have plenty of non-required arguments,
        # such as the output file format or the arguments.
        if req["inference_output_format"]:
            params["inference_out_format"] = req["inference_output_format"]

        if req["inference_arguments"]:
            params["inference_args"] = req["inference_arguments"]

        # However, the inference tool, the output file name and the bootstraps must be specified.

        params["inference_tool"] = req["inference_tool"]

        params["inference_bootstraps"] = req["inference_bootstraps"]