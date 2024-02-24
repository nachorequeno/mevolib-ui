from celery import shared_task
import nextflow
    
@shared_task()
def run_workflow(workflow_path, parameters):
    """Orders a Nextflow workflow to start, so that it can be executed asynchronously while the user keeps on
    doing other tasks."""
    
    nextflow.run(workflow_path, params = parameters)