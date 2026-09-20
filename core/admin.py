from django.contrib import admin
from .models import *
admin.site.register([Institution,Reference,ReferenceNode,Guide,Visit,VisitNode,Assignment])
