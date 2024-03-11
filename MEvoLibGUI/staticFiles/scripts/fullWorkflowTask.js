"use strict"

$("#full_wf_form").on("submit", function(event){ 

    event.preventDefault(); /* If the user submits the form, the first thing to do is to prevent the server call, as the
                               submission would be much clearer (specially, in error case) if it was made via an AJAX call,
                               and page's reload would not be neccessary; saving up resources.  */
   
    var formData = new FormData($("#full_wf_form")[0]); /* First, the data the server will received is initialized to all
                                                        the non-file parameters of the form. */

                                                    /* Next, if Fetch has not been selected and any of the other stages have
                                                       been selected, the matching input files are added to the dataset.  */
    if ($("#cluster_input")[0].files.length === 1) {
        formData.append("cluster_input", $("#cluster_input")[0].files[0]);
    } else if ($("#align_input")[0].files.length === 1) {
        formData.append("align_input", $("#align_input")[0].files[0]);
    } else if ($("#inference_input")[0].files.length === 1) {
        formData.append("inference_input", $("#inference_input")[0].files[0]);
    }

    if(validate()){     /* If the submission is valid, the AJAX call is made to asynchronously make server side's data
                           validation, by sending the previously compound data and evaluating the response given. */
        $.ajax({
            url: "/full_workflow/",
            type: "POST",
            processData: false,
            contentType:false,
            headers: {
                'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()   // Needed CSRF token, to avoid session hijack attacks.
            },
            data: formData,
            dataType:"json",
            success: function(response){    // If all goes fine, the form workflow is hidden and a message informing the user is shown.
                $("#full_wf_modal").modal("hide")
                $("#full_workflow_successful_modal").modal("show")

                var task_id = response["task_id"], task_hash = response["task_hash"], zip_name = response["zip_name"]

                checkTaskStatus(task_id, task_hash, zip_name)  // Since the workflow execution is an asynchronous task, a function to
                                                                // check it's status from the server will be called.
            },
            error: function(response){  /* If there is a server error, it's matching message is shown alongside the form (or an alert
                                            is shown, in case there is an unknown server internal error.)*/

                response = JSON.parse(response.responseText)         

                if(response["align_file_err"]) $("#align_file_err").text(response["align_file_err"]).show();
                else if(response["inference_file_err"]) $("#inference_file_err").text(response["inference_file_err"]).show();
                else{
                    $("#full_wf_modal").modal("hide")
                    alert("An internal server error has occured.")
                } 
                
            }
        })
    }
})

function checkTaskStatus(task_id, task_hash, zip_name){

    $.ajax({
        url: "/check_task_status/",
        type: "GET",
        headers: {
            'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()
        },
        data: {"task_id":task_id},
        dataType:"json",
        success: function(response){    // Every 2 seconds, an AJAX call is made to check if the task has finished.

            var task_status = response["task_status"]

            if(task_status === "SUCCESS"){  // If it finishes successfully, another function to get the generated files will be called.
                $("#full_workflow_successful_modal").modal("hide")
                $("#full_workflow_finished_modal").modal("show")
                download_task_zip(task_hash, zip_name);
            }
            else if(task_status === "FAILURE"){          // If it fails, the user will be notified.
                $("#full_workflow_successful_modal").modal("hide")
                $("#full_workflow_failed_modal").modal("show")
            }
            else if(task_status === "PENDING"){   // If it has not finished yet, it will be called again within a couple of seconds.
                setTimeout(function() {
                    checkTaskStatus(task_id, task_hash, zip_name);
                }, 2000); // Check again after 2 seconds
            }
            else{
                $("#full_workflow_successful_modal").modal("hide")
                alert("A server side error has ocurred. Try again later.")
            }

        },
        error: function(jqhxr, status, error){      // If an error occurs, the user will be notified.
            $("#full_workflow_successful_modal").modal("hide")
            alert("A server side error has ocurred: ", error)
        }
    })
}

function download_task_zip(task_hash, zip_name){  // An AJAX call makes the server to send the client a ZIP with its files.

    $.ajax({
        url: "/download_task_zip/",
        type: "GET",
        data: {"task_hash":task_hash},
        contentType: false,
        xhrFields:{
            responseType: 'blob'
        },
        headers: {
            'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()
        },
       
        success: function(response){    // If all goes fine, the user will get a message to tell them the zip has been downloaded.

            // A zip link is generated and clicked in the background, so that user does not need to click on it.
            var link = document.createElement('a'); // Link (a href...) element dynamically generated and added to the DOM.
            link.href = window.URL.createObjectURL(response)
            link.download = zip_name;    // Zip, named after the original output the client selected.
            document.body.appendChild(link);
            link.click();
        },
        error: function(jqhxr, status, errorThrown){    // Again, any error will be communicated to the user.
            $("#full_workflow_successful_modal").modal("hide")
            alert("A server side error has ocurred: ", errorThrown)
        }
    })
}