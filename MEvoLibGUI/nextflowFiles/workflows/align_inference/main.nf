include { GET_ALIGN } from '../../mevolib-workflow/modules/get_align.nf'
include { GET_INFERENCE } from '../../mevolib-workflow/modules/get_inference.nf'

workflow {
    GET_ALIGN(params.unaln_files)
    GET_INFERENCE (GET_ALIGN.out)
}