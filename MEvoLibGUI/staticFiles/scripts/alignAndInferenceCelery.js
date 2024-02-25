"use strict"

$("#align_inf_form").on("submit", function(event){  // When the form is submitted, an AJAX call is made instead of a normal submission.
    event.preventDefault();

    var formData = new FormData($("#align_inf_form")[0]);   // Form data load
    if ($("#id_unaligned_file")[0].files.length === 1) {
        formData.append("unaligned_file", $("#id_unaligned_file")[0].files[0]);
    } 

    $.ajax({    // Ajax call to the server, to manage the response
        "url":"/align_and_inference/", type: "POST",
        processData: false,
        contentType:false,
        headers: {
            'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()
        },
        data: formData,
        dataType:"json",
        success: function(response){            // If all is fine, a modal indicating the correct submission will be shown.
            $("#align_inf_modal").modal("hide")
            $("#align_inference_successful_modal").modal("show")

            var task_id = response["task_id"], task_hash = response["task_hash"]

            checkTaskStatus(task_id, task_hash)  // Since the workflow execution is an asynchronous task, a function to
                                                 // check it's status from the server will be called.
        },
        error: function(jqhxr, status, errorThrown){  // If trhere is an error, the form modal will be closed and an alert will be shown.
            $("#align_inf_modal").modal("hide")
            alert("A server side error has ocurred: ", errorThrown)
        }       
    })
})

function checkTaskStatus(task_id, task_hash){

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
                download_task_zip(task_hash);
            }
            else if(task_status === "FAILURE"){          // If it fails, the user will be notified.
                $("#align_inference_successful_modal").modal("hide")
                alert("Somethong went bad with the task... Please, try again later.")
            }
            else{   // If it has not finished yet, it will be called again within a couple of seconds.
                setTimeout(function() {
                    checkTaskStatus(task_id, task_hash);
                }, 2000); // Check again after 2 seconds
            }

        },
        error: function(jqhxr, status, error){      // If an error occurs, the user will be notified.
            $("#align_inference_successful_modal").modal("hide")
            alert("A server side error has ocurred: ", error)
        }
    })
}

function download_task_zip(task_hash){  // An AJAX call makes the server to send the client a ZIP with its files.

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

            $("#align_inference_successful_modal").modal("hide")
            $("#align_inference_finished_modal").modal("show")

            // A zip link is generated and clicked in the background, so that user does not need to click on it.
            var link = document.createElement('a');
            link.href = window.URL.createObjectURL(response)
            link.download = 'processOutput.zip';    // Naming is still under development, this is only a prototype.
            document.body.appendChild(link);
            link.click();
        },
        error: function(jqhxr, status, errorThrown){    // Again, any error will be communicated to the user.
            $("#align_inference_successful_modal").modal("hide")
            alert("A server side error has ocurred: ", errorThrown)
        }
    })
}