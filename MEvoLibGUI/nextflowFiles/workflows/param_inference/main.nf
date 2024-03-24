
process GET_INFERENCE {
    tag "$alignment"
    publishDir "./output/param_inference/${params.output_name}", mode: 'copy', overwrite: false
    
    input:
        val command

    output:
        path '*_inference.newick'
       
    shell:
        '''
        !{command}
        '''
}


workflow {
 
    GET_INFERENCE(params.total_query)
}
