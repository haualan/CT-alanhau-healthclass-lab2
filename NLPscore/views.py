from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views import generic
from django.utils import timezone
from vanilla import CreateView, ListView
import NLPModel

# Create your views here.


class docScoreView(generic.View):

  def get(self, request):
    # a = NLPModel.NLPModel()
    # r = a.useModel("testString a husband RA Rheumatoid Arthritis")
    # return render_to_response('patient/dashboard.html', context_instance = RequestContext(request))
    return render(request,'NLPscore/docScore.html', 
      {"get": True} 
      )

  def post(self, request):
    textEntry = request.POST['textEntry']

    a = NLPModel.NLPModel()
    r = a.useModel(textEntry)
    comments = [
    "Your score is below 25, Your writing is truly unhelpful at all or off-topic, please rewrite your content and try again.",
    "Your score is below 50, patients would generally find your text uninteresting or not helpful, look at the tips above and study the examples and edit your content. Don't give up!",
    "Your score is above 50, patients would generally find your text interesting and helpful. Incorporate more attributes from our tips section to see if you can score even higher.",
    "Your score is above 75, you have done a great job to make your writing interesting for your patients. Well done!"

    ]

    score = (((r + 10) / 20 ) * 100)

    if score < 25:
      if score < 0:
        score = 0
      comment = comments[0]
    elif score >= 25 and score < 50:
      comment = comments[1]
    elif score >= 50 and score < 75:
      comment = comments[2]
    elif score >= 75:
      if score > 100:
        score = 100
      comment = comments[3]



    return render(request,'NLPscore/docScore.html', 
      {
        "relativeScore": "{:.0f}".format(score),
        "textEntry": textEntry,
        "comment": comment
      }  
      )



