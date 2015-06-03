from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.views import generic
import os

# Create your views here.
class MainIndexView(generic.View):

  def get(self, request):
    # a = NLPModel.NLPModel()
    # r = a.useModel("testString a husband RA Rheumatoid Arthritis")
    # return render_to_response('patient/dashboard.html', context_instance = RequestContext(request))
    return render(request,'main/index.html', 
      {"get": True} 
      )

def exportResumeFile(request):
  # Create the HttpResponse object with the appropriate CSV header.

  path_to_file = os.path.realpath("/Users/ahau/alanhausite/main/static/alan_hau_resume.pdf")
  # path_to_file = os.path.realpath("/home/ubuntu/alanhausite/main/static/alan_hau_resume.pdf")
  f = open(path_to_file, 'r')
  

  # response = HttpResponse(f, content_type='application/vnd.ms-excel')
  # response['Content-Disposition'] = 'attachment; filename="HOOS_Steps.xlsx"'

  response = HttpResponse(f, content_type='application/pdf')
  response['Content-Disposition'] = 'attachment; filename="alan_hau_resume.pdf"'

  f.close()

  return response