import datetime

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.serializers.json import json
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import cache_page

from .forms import UserForm, AnswerForm, VoterForm
from .models import AnswerSheet, Candidate, Question, AnswerText

from vaa.staticpages.models import Page
from vaa.utils import render_with, max_d


@cache_page(60*5)
@render_with("home.html")
def home(request):
    return {
        'page':Page.objects.filter(page_url="frontpage")
    }


@render_with("userpage.html")
def userpage(request):
    candidate = request.user.candidate_set.all()[0]
    last_answers = candidate.answersheet_set.order_by('-timestamp')
    form_context =  {
                'first_name':request.user.first_name,
                'last_name':request.user.last_name,
                'ssn':candidate.ssn,
                'picture':candidate.picture,
                'blurb':candidate.blurb,
                }
    if last_answers:
        form_context['last_answer'] = last_answers[0].timestamp
    context = { 
        'userpageform': UserForm(initial=form_context),
        'candidate': candidate,
        'receipt': request.GET.get('receipt', False),
        'blurb':candidate.blurb
    }
    if candidate.picture.name:
        context.update({'picture': candidate.picture.file.name.split("/")[-1]})
    return context

@login_required
def userupdate(request):
    userform = UserForm(request.POST, request.FILES)
    candidate = request.user.candidate_set.all()[0]
    if userform.is_valid():
        data = userform.cleaned_data
        request.user.first_name = data['first_name']
        request.user.last_name = data['last_name']
        candidate.ssn = data['ssn']
        if 'picture' in request.FILES:
            with open(settings.MEDIA_UPLOADS + "cand_pics" + data['picture'].name, "wb+") as cand_pic:
                for chunk in request.FILES['picture']:
                    cand_pic.write(chunk)
        if 'picture' in data:
            candidate.picture = data['picture']
        candidate.blurb = data['blurb']
        request.user.save()
        candidate.save()
    return HttpResponseRedirect("/userpage/")


@login_required
@render_with("candanswers.html")
def candanswer(request, election):
    last_answers = getattr(request.user.candidate_set.filter(election__slug=election).first(), "last_answers", None)
    if last_answers:
        form = AnswerForm(initial=dict(last_answers), election=election)
    else:
        form = AnswerForm(election=election)
    return {
        'answerform':form,
        'election':election,
        }


@login_required
def candreply(request, election):
    form = AnswerForm(request.POST, election=election)
    if form.is_valid() == False:
        return render(request, "candanswers.html", {'answerform':form, 'election':election})
    data = form.get_data()
    AnswerSheet(
        timestamp=datetime.datetime.utcnow(),
        candidate=request.user.candidate_set.filter(election__slug=election).first(),
        answers=[[k,v] for k,v in data]
    ).save()
    return HttpResponseRedirect("/userpage/?receipt=1")


@user_passes_test(lambda u: u.is_superuser)
@render_with("voter_form.html")
def voterform(request, election, hashcode=None):
    form = VoterForm(election=election)
    return {'voterform':form, 'election':election}


@user_passes_test(lambda u: u.is_superuser)
@render_with("comparison.html")
def compare(request, election):
    form = VoterForm(request.POST)
    valid_form = form.is_valid()
    voterdata = form.get_data()
    q_pk = [q.pk for q in Question.objects.filter(active=True, election__slug=election)]
    max_distance = float(max_d(voterdata, q_pk))
    context = {'data': sorted(
        [(
            (cand, (
                1.0 - (float(cand.compare(voterdata))/max_distance)
            )*100.0
            )) for cand in Candidate.objects.filter(
                election__slug=election
            ) if cand.last_answers],
        key=lambda i:i[1], reverse=True),
               'election':election}
    request.session['candlist'] = [(d[0].pk, d[1]) for d in context['data']]
    request.session['voterdata'] = voterdata # ditto, but maybe that is a bad plan
    return context

@render_with("comparison.html")
def compare_load(request, election, hashcode):
    pass


remap = 'id_q_%s_%s'
def oldanswers(request, election):
    last_answers = dict(getattr(request.user.candidate_set.filter(election__slug=election).first(), "last_answers", None))
    for key in last_answers:
        if "q_" in key:
            number = key[2:]
            last_answers[key] = remap % (number, int(last_answers[key])-1)
    if last_answers:
        return HttpResponse(json.dumps(last_answers.items()), content_type="application/json")
    return HttpResponse("[]", content_type="application/json")


@render_with("candidate_page.html")
def candidate_page(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    questions = Question.objects.filter(active=True, election=candidate.election).order_by('pk')
    answertexts = [a.text for a in AnswerText.objects.order_by('mod')]
    if not candidate.last_answers:
        return HttpResponse("No answers")
    if 'voterdata' in request.session:
        print request.session['voterdata']
        vd = dict(request.session['voterdata'])
        la = dict(candidate.last_answers)
        context = {
            'answers':True, 
            'questions':[
                (
                    q,
                    la.get("t_%s"%q.pk, ""),
                    answertexts[int(vd.get("q_%s"%q.pk))-1],
                    answertexts[int(la.get("q_%s"%q.pk))-1]
                ) for q in questions
            ],
            'cand':candidate}
    else:
        la = dict(candidate.last_answers)
        context = {
            'answers':True, 
            'questions':[
                (
                    q,la.get("t_%s"%q.pk, ""),
                    "",
                    answertexts[int(la.get("q_%s"%q.pk))-1]
                ) for q in questions
            ],
            'cand':candidate}

    return context

