from django.contrib import admin

from . import models
# Register your models here.


# Обещаю не далать так в проде =)

for obj_str in dir(models):
    if obj_str.islower() or obj_str.startswith("__"):
        continue
    admin.site.register(getattr(models, obj_str))
