from django.contrib import admin

from . import models
# Register your models here.

admin.site.register(models.Test)
admin.site.register(models.ExtendedUser)
admin.site.register(models.Question)
admin.site.register(models.PassedTest)
admin.site.register(models.Answer)
admin.site.register(models.PassedQuestion)

