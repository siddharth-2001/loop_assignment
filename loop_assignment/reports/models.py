from django.db import models

# Create your models here.


class Report(models.Model):

    report_id = models.CharField(max_length=300, primary_key=True)
    status = models.CharField(max_length=120)

    def __str__(self):
        return f'{self.report_id}'