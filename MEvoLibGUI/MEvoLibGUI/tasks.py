# See the NOTICE file distributed with this work for additional information
# regarding copyright ownership.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pathlib import Path

from celery import shared_task
import nextflow
    
from nextflowApp.formats import TASK_ERROR, WORKFLOW_ERROR    
    
@shared_task()
def run_workflow(workflow_path, parameters):
    """Orders a Nextflow workflow to start, so that it can be executed asynchronously while the user keeps on
    doing other tasks."""

    # Searches the output lines that indicate the errors within the log file.
    workflow_error = WORKFLOW_ERROR
    task_error = TASK_ERROR
    
    # Creates the report location.
    report_dir = Path(parameters["output_dir"]).joinpath("execution_report.html")
    
    # Runs the workflow given a set of parameters.
    execution = nextflow.run(workflow_path, params=parameters, report = report_dir)
    output_dir = Path(parameters["output_dir"])
    task_failed = False
    
    # If the output path is empty, it means no file has been generated, so an internal error
    # must have happened.
    if not Path.exists(output_dir.absolute()):
        task_failed = True
    
    # The output directory, among its children, is created, so that the report file and the log
    # can be allocated there (it is needed in case an error has happened and the log has to be
    # placed there).
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "nextflow.log"
    
    # The log file is written, using the patterns defined above.
    with log_path.open("w") as flog:
        flog.write(f"{execution.command}\n\n")
        for line in execution.log.splitlines():
            if workflow_error.search(line) or task_error.search(line):
                flog.write(f"{line}\n")
    
    # Celery's tasks only fails if the threw any exception, but nextflow.run command does not throw
    # any, so it has to be done manually to inform the user something went bad.            
    if task_failed:
        raise RuntimeError("An error has ocurred")