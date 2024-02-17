
process GET_ALIGN {
    tag "$alignment"
    publishDir "./output/inference/${params.output_name}", mode: 'copy', overwrite: false
    
    input:
        path unaligned_files

    output:
        path '*_align.fasta'
       
    shell:
        '''
        get_align -t !{params.tools.align_tool} -i !{unaligned_files} -o !{params.output_name}
        '''
}


workflow {
 
    GET_ALIGN(params.unaln_files)
}