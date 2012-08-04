from django.db import models
import datetime
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class computerlab(models.Model):
	labname = models.CharField(max_length=100)
	labdescription = models.CharField(max_length=100)
	coursename = models.CharField(max_length=100)
	coursecode = models.CharField(max_length=100)
	coursesemester = models.CharField(max_length=100)
	courseinstructor = models.CharField(max_length=100)
	amazonami = models.CharField(max_length=100)
	date_created = models.DateTimeField('date published')
	
	def __unicode__(self):
		return self.labname