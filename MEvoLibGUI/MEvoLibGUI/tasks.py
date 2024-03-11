from celery import shared_task
from pathlib import Path
import nextflow, os, re

from MEvoLibGUI.settings import (
    WORKFLOW_OUTPUT as wf_output,
)
    
@shared_task()
def run_workflow(workflow_path, parameters):
    """Orders a Nextflow workflow to start, so that it can be executed asynchronously while the user keeps on
    doing other tasks."""

    workflow_error = re.compile(r"^.+ ERROR .+$")
    task_error = re.compile(r"^.+ terminated with an error .+$")
    
    report_dir = Path(parameters["output_dir"]).joinpath("execution_report.html")
    
    execution = nextflow.run(workflow_path, params=parameters, report = report_dir)
    output_dir = Path(parameters["output_dir"])
    
    if not Path.exists(output_dir.absolute()):
        output_dir.mkdir(parents=True, exist_ok=True)
        log_path = output_dir / "nextflow.log"
        
        with log_path.open("w") as flog:
            flog.write(f"{execution.command}\n\n")
            for line in execution.log.splitlines():
                if workflow_error.search(line) or task_error.search(line):
                    flog.write(f"{line}\n")

        raise RuntimeError("An error has ocurred")
        
    

    
  