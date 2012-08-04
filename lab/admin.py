from lab.models import computerlab
from django.contrib import admin
from django.contrib.auth.models import User

class computerlabAdmin(admin.ModelAdmin):
	fields = ['labname', 'labdescription', 'coursename', 'coursecode', 'coursesemester', 'courseinstructor', 'amazonami', 'date_created']

admin.site.register(computerlab, computerlabAdmin)

