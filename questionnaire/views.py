from django.shortcuts import render
from django.views import View

from . import models
# Create your views here.


class TestListView(View):
    def get(self, request):
        tests = models.Test.objects.all()
        return render(request, "tests/list.html", context={"tests": tests})
