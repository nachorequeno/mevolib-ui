include { GET_ALIGN } from '../../workflows/align/main.nf'
include { GET_INFERENCE } from '../../workflows/inference/main.nf'

workflow {
    GET_ALIGN(params.unaln_files)
    GET_INFERENCE (GET_ALIGN.out)
}