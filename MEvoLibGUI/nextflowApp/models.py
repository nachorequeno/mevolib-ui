from django.db import models
from django.core.validators import FileExtensionValidator
from pathlib import Path

from MEvoLibGUI.settings import NEXTFLOW_UPLOADS_ROOT as ur


# Create your models here.
class InferenceDocument(models.Model):
    save_path = Path(ur).joinpath("inference")
    docfile = models.FileField(upload_to=save_path)


class ParamInferenceDocument(models.Model):
    save_path = Path(ur).joinpath("param_inference")
    docfile = models.FileField(upload_to=save_path)


class AlignInferenceDocument(models.Model):
    save_path = Path(ur).joinpath("align_inference")
    docfile = models.FileField(upload_to=save_path)
    

class FullWorkflowDocument(models.Model):   # Model to store a full workflow file.
    save_path = Path(ur).joinpath("full_workflow")
    docfile = models.FileField(upload_to=save_path)    

