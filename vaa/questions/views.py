import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import render


from .forms import UserForm, AnswerForm, VoterForm
from .models import AnswerSheet, Candidate
from vaa.utils import render_with, max_d

@render_with("home.html")
def home(request):
    return {}

@render_with("userpage.html")
def userpage(request):
    candidate = request.user.candidate_set.all()[0]
    last_answers = candidate.answersheet_set.first()
    form_context =  {
                'first_name':request.user.first_name,
                'last_name':request.user.last_name,
                'ssn':candidate.ssn,
                'picture':candidate.picture,
                'blurb':candidate.blurb,
                }
    if last_answers:
        form_context['last_answer'] = last_answers.timestamp
    return { 'userpageform': UserForm(form_context)}

def userupdate(request):
    userform = UserForm(request.POST)
    candidate = request.user.candidate_set.all()[0]
    if userform.is_valid():
        data = userform.cleaned_data
        request.user.first_name = data['first_name']
        request.user.last_name = data['last_name']
        candidate.ssn = data['ssn']
        candidate.picture = data['picture']
        candidate.blurb = data['blurb']
        request.user.save()
        candidate.save()
    return HttpResponseRedirect("/userpage/")


@render_with("candanswers.html")
def candanswer(request):
    last_answers = request.user.candidate_set.first().last_answers
    if last_answers:
        form = AnswerForm(initial=dict(last_answers))
    else:
        form = AnswerForm()
    return {
        'answerform':form
        }

def candreply(request):
    form = AnswerForm(request.POST)
    if form.is_valid() == False:
        return render(request, "candanswers.html", {'answerform':form})
    data = form.get_data()
    AnswerSheet(
        timestamp=datetime.datetime.utcnow(),
        candidate=request.user.candidate_set.all()[0],
        answers=[[k,v] for k,v in data]
    ).save()
    return HttpResponseRedirect("/userpage/")


@render_with("voter_form.html")
def voterform(request):
    form = VoterForm()
    return {'voterform':form}



@render_with("comparison.html")
def compare(request):
    form = VoterForm(request.POST)
    if form.is_valid() == False:
        return render(request, "voter_form.html", {'voterform':form})
    voterdata = form.get_data()
    max_distance = max_d(voterdata)
    context = {'data': sorted(
        [(cand, 1.0 - (float(cand.compare(voterdata))/float(max_distance))) for cand in Candidate.objects.all() if cand.last_answers],
        key=lambda i:i[1], reverse=True)}
    return context
