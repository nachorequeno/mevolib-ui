
process GET_ALIGN {
    tag "$alignment"
    publishDir "${params.output_dir}/alignments/${params.output_name}", mode: 'copy', overwrite: true
    
    input:
        path unaligned_files

    output:
        path '*_align.fasta'
       
    shell:
        '''
        get_align -t !{params.tools.align_tool} -i !{unaligned_files}
        '''
}


workflow {
 
    GET_ALIGN(params.unaln_files)
}
