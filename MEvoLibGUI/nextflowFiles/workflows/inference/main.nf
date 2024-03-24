
process GET_INFERENCE {
    tag "$alignment"
    publishDir "${params.output_dir}/inferences/${params.output_name}", mode: 'copy', overwrite: true
    
    input:
        path alignment

    output:
        path '*_inference.newick'
       
    shell:
        '''
        get_inference -t !{params.tools.inference_tool} -i !{alignment} 
        '''
}


workflow {
 
    GET_INFERENCE(params.aln_files)
}
