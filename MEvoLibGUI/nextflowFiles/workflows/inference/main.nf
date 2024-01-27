
process GET_INFERENCE {
    tag "$alignment"
    publishDir "./output/inference/${params.output_name}", mode: 'copy', overwrite: false
    
    input:
        path alignment

    output:
        path '*_inference.newick'
       
    shell:
        '''
        get_inference -t !{params.tools.inference_tool} -i !{alignment} -o !{params.output_name}
        '''
}


workflow {
 
    GET_INFERENCE(params.aln_files)
}
