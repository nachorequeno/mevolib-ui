from django.db import models
from pathlib import Path

from MEvoLibGUI.settings import NEXTFLOW_UPLOADS_ROOT as ur


# Create your models here.

class FullWorkflowDocument(models.Model):   # Model to store a full workflow file.
    save_path = Path(ur).joinpath("full_workflow")
    docfile = models.FileField(upload_to=save_path)    

