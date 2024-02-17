"use strict"

// Before rendering the modal, all of the concrete modules params are hidden, as any option will be marked by default (it will be unclikec, just in case).
$("#full_wf_but").on('click', function(event){
   hideAndReset();
   hideErrors();
})

// ---- FETCH STAGE ----

$("#add_fetch").on('change', function(event){

    if(this.checked){   /* The user wants to make a fetch stage, so its parameters are shown. Also, the fetch label is
                           made bigger and changes to a blue colour, now the query or species params are shown, and the
                           user is forced to choose from one of them.*/
        $("#fetch_label").removeClass("text-secondary").addClass("fw-bold text-primary").css({"font-size": "1.35em"});
        $("#query_opt").prop("checked", false).prop("required",true);
        $(".query_species_params").hide();
        $("#fetch_params").show();

        hideSelectedInput();     /* If the fetch stage is selected, it does not make any sense to make the user to 
                                    introduce input files, as the workflow will start from fetch files, so the one
                                    that could have beem selected are hidden is cleared; alongside with its label.*/
                  
        $(".input_file").each(function(){   /* All the Cluster, Align and Inference file inputs are hidden alongside 
                                               their labels and file format, as there is no point on showing them if
                                               the Fetch stage will already provide the required files */
            $(this).hide();
        })           
        
        $(".input_file_label").each(function(){
            $(this).hide();
        })   

        $(".input_file_format").each(function(){
            $(this).hide();
        })  

        $(".input_file_format_label").each(function(){
            $(this).hide();
        })  
            
        
    }

    else{   /* The user does not want to make a fetch stage, so its parameters are hidden, the fetch label style gets
               back to its original one and radio buttons reset, just in case he clicks without meaning to. Also, 
               query or species fields are no more required, as they are going to be invisible, so it would not make 
               any sense.*/
        $("#fetch_label").removeClass("fw-bold text-primary").addClass("text-secondary").css({"font-size": "1.25em"})
        $(".query_species_params").hide();
        $("#fetch_params").hide();
        $("#query_opt").prop("checked", false);
        $("#species_opt").prop("checked", false);
        $("#fetch_output").hide();

        $(".fetch_required").each(function(){   /*Also, the required files now are not required, as the user has 
                                                  unselected the fetch stage, so they are not needed anymore.*/
            $(this).prop("required", false);
        })
        
        showSelectedInput();
    }


})

/* If the query option is clicked, then the species one and its params are hidden, and they stop being required 
   (as query one is required now).*/
$("#query_opt").on('click', function(event){
    $("#species_params").hide();
    $("#fetch_query").prop("required",true);
    $("#fetch_species").prop("required",false);
    $("#fetch_output").show();
    $("#fetch_output_name").prop("required",true);
    $("#query_params").show();
})


/* If the species option is clicked, then the query one and its params are hidden, and they stop being required 
   (as species one is required now). */
$("#species_opt").on('click', function(event){
    $("#query_params").hide();
    $("#fetch_query").prop("required",false);
    $("#fetch_species").prop("required",true);
    $("#fetch_output").show();
    $("#fetch_output_name").prop("required",true);
    $("#species_params").show();
})


// ---- CLUSTER STAGE ----

$("#add_cluster").on('change', function(event){

    showSelectedInput();

    if(this.checked){   /* The user wants to make a cluster stage, so its parameters are shown. Also, the cluster
                           label is made bigger and changes to a blue colour. */
        $("#cluster_label").removeClass("text-secondary").addClass("fw-bold text-primary").css({"font-size": "1.35em"});
        $(".cluster_required").each(function(){
            $(this).prop("required", true);
        })
        $("#cluster_params").show();
     
    }

    else{   /* The user does not want to make a cluster stage, so its parameters are hidden and the cluster label
               style gets back to its original one. */
        $("#cluster_label").removeClass("fw-bold text-primary").addClass("text-secondary").css({"font-size": "1.25em"})
        $(".cluster_required").each(function(){
            $(this).prop("required", false);
        })
        $("#cluster_params").hide();

    }
})


// ---- ALIGN STAGE ----

$("#add_align").on('change', function(event){

    showSelectedInput();

    if(this.checked){   /* The user wants to make an align stage, so its parameters are shown. Also, the align label
                           is made bigger and changes to a blue colour. */
        $("#align_label").removeClass("text-secondary").addClass("fw-bold text-primary").css({"font-size": "1.35em"});
        $(".align_required").each(function(){
            $(this).prop("required", true);
        })
        $("#align_params").show();

        
        if(!$("#align_input").hasClass("selected_input")){
            $("#align_input").hide();    
            $("label[for='"+$("#align_input").attr("id")+"']").hide(); 

            $("label[for='"+$("#align_input").attr("id")+"_format']").hide(); 
            $("select[id='"+$("#align_input").attr("id")+"_format']").hide(); 
        }

    }

    else{   /* The user does not want to make an align stage, so its parameters are hidden and the align label style
               gets back to its original one. */
        $("#align_label").removeClass("fw-bold text-primary").addClass("text-secondary").css({"font-size": "1.25em"})
        $(".align_required").each(function(){
            $(this).prop("required", false);
        })
        $("#align_params").hide();
        
    }
})


// ---- INFERENCE STAGE ----

$("#add_inference").on('change', function(event){

    showSelectedInput();

    if(this.checked){   /* The user wants to make an inference stage, so its parameters are shown. Also, the cluster 
                           label is made bigger and changes to a blue colour. */
        $("#inference_label").removeClass("text-secondary").addClass("fw-bold text-primary").css({"font-size": "1.35em"});
        $(".inference_required").each(function(){
            $(this).prop("required", true);
        })
        $("#inference_params").show();


        if(!$("#inference_input").hasClass("selected_input")){
            $("#inference_input").hide();    
            $("label[for='"+$("#inference_input").attr("id")+"']").hide(); 
            $("label[for='"+$("#inference_input").attr("id")+"_format']").hide(); 
            $("select[id='"+$("#inference_input").attr("id")+"_format']").hide(); 
        }
    }

    else{   /* The user does not want to make an inference stage, so its parameters are hidden and the inference label 
               style gets back to its original one. */
        $("#inference_label").removeClass("fw-bold text-primary").addClass("text-secondary").css({"font-size": "1.25em"})
        $(".inference_required").each(function(){
            $(this).prop("required", false);
        })
        $("#inference_params").hide();
        
    }
})

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
                $("#full_wf_successful_modal").modal("show")
            },
            error: function(response){  /* If there is a server error, it's matching message is shown alongside the form (or an alert
                                            is shown, in case there is an unknown server internal error.)*/
                if(response.responseJSON){
                     if(response.responseJSON.align_file_err){
                    $("#align_file_err").text(response.responseJSON.align_file_err).show();
                    } 
                    else if(response.responseJSON.cluster_file_err) $("#cluster_file_err").text(response.responseJSON.cluster_file_err).show();
                    else if(response.responseJSON.inference_file_err) $("#inference_file_err").text(response.responseJSON.inference_file_err).show();
                }
                else{
                    alert("An internal server error has occured.")
                }
               
            }
        })
    }
})

function hideAndReset(){    /* All labels styles get back to normal ones and the whole form is reset. This function is triggered
                               everytime the user opens the modal, in order to ensure it does not have any trash. */
    $(".form_label").each(function(){
        $(this).removeClass("fw-bold text-primary").addClass("text-secondary").css({"font-size": "1.25em"});
    })
    $(".workflow_params").hide();

    $("#full_wf_form").trigger("reset");

    resetRequirements();    // Deletes "required" attribute for some inputs.
}

function hideSelectedInput(){   /* If any stage (that is not fetch) had been selected, it is hidden, reset, made not required
                                   and loses it's "selected_input" class. */
    $(".selected_input").each(function(){                   
        $(this).removeClass("selected_input").prop("required",false).val("").hide();    
        $("label[for='"+this.id+"']").hide(); 
        $("label[for='"+this.id+"_format']").hide(); 
        $("select[id='"+this.id+"_format']").hide(); 
    })
}

function resetRequirements(){   /* All the "required" attributes inputs are made non-required, as it is called when the form has
                                   just being opened, and the user has not selected anything. */

    $(".fetch_required").each(function(){
        $(this).prop("required", false);
    })

    $(".cluster_required").each(function(){
        $(this).prop("required", false);
    })

    $(".align_required").each(function(){
        $(this).prop("required", false);
    })

    $(".inference_required").each(function(){
        $(this).prop("required", false);
    })
}


function showSelectedInput(){   /* If any stage (that is not fetch) had been selected, the one chosen before is cleared and a new
                                   one is selected, as order marks the priority. */
    var selected

    hideSelectedInput();    // The previously selectd input file is hidden, cleared and made not required.

    if(!$("#add_fetch").prop("checked")){   /* If the user has not selected the fetch stage, there will be an input file selected
                                               from the selected stages from which those stages will execute. */ 
        if($("#add_cluster").prop("checked")){
        selected=$("#cluster_input")
        }
        else if($("#add_align").prop("checked")){
            selected=$("#align_input")
        }
        else if($("#add_inference").prop("checked")){
            selected=$("#inference_input")
        }
        
                        // If there is a selected file, it is made visible (alongside with its label and file format) and required.
        if(selected){
            $(selected).addClass("selected_input").prop("required",true).show();  
            $("label[for='"+$(selected).attr("id")+"']").show(); 
            $("label[for='"+$(selected).attr("id")+"_format']").show(); 
            $("select[id='"+$(selected).attr("id")+"_format']").show(); 
        }
    }
}

function hideErrors(){      // Both, server and client side errors, are hidden.
    $(".client_side_err").each(function(){
        $(this).hide();
    })
    $(".server_side_err").each(function(){
        $(this).hide();
    })
}

function validateSelectFields(){    /* Client side validation to ensure the user chooses an alignment/
                                       inference tool. */


                                       
    if($("#add_cluster").prop("checked")){

        if($("#cluster_input").hasClass("selected_input") && $("#cluster_input_format").val()===""){

            $("#cluster_input_format_err").text("Please, select a valid input file format.").show();
            return false;
        }
    }

    if($("#add_align").prop("checked")){

        if($("#align_input").hasClass("selected_input") && $("#align_input_format").val()===""){

            $("#align_input_format_err").text("Please, select a valid input file format.").show();
            return false;
        }

        else if($("#align_tool").val()===""){

            $("#align_tool_err").text("Please, select a valid alignment tool.").show();
            return false;
        }
    }

    if($("#add_inference").prop("checked")){

        if($("#inference_input").hasClass("selected_input") && $("#inference_input_format").val()===""){

            $("#inference_input_format_err").text("Please, select a valid input file format.").show();
            return false;
        }

        else if($("#inference_tool").val()===""){
            $("#inference_tool_err").text("Please, select a valid inference tool.").show();
            return false;
        }
    }

    return true;
}

function validateOutputNames(){     /* Client side validation to ensure the user does not introduce invalid
                                       (empty/full empty spaces) file outputs. */

    if($("#add_cluster").prop("checked")){

        if($("#cluster_output").val().trim()===""){
            $("#cluster_output_err").text("Please, write a non-empty output name.").show();
            return false;
        }
    }

    if($("#add_align").prop("checked")){

        if($("#align_output").val().trim()===""){
            $("#align_output_err").text("Please, write a non-empty output name.").show();
            return false;
        }
    }

    if($("#add_inference").prop("checked")){

        if($("#inference_output").val().trim()===""){
            $("#inference_output_err").text("Please, write a non-empty output name.").show();
            return false;
        }
    }

    return true;
}

function validate(){    // Form validation.
    hideErrors();
    return validateSelectFields() && validateOutputNames();
}
