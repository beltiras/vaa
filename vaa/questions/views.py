import datetime

from hashlib import sha1

from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import cache_page


from .forms import UserForm, AnswerForm, VoterForm
from .models import AnswerSheet, Candidate, Question, PermanentResult, QuestionSheet
from vaa.utils import render_with, max_d


@cache_page(60*5)
@render_with("home.html")
def home(request):
    return {}


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
    return { 'userpageform': UserForm(form_context)}


@login_required
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
    return HttpResponseRedirect("/userpage/")


@user_passes_test(lambda u: u.is_superuser)
@render_with("voter_form.html")
def voterform(request, election):
    form = VoterForm(election=election)
    return { 'voterform':form, 'election':election }


@user_passes_test(lambda u: u.is_superuser)
@render_with("comparison.html")
def compare(request, election):
    form = VoterForm(request.POST)
    valid_form = form.is_valid()
    voterdata = form.get_data()
    voter_hash = sha1(str(voterdata)).hexdigest
    voter_data_obj = QuestionSheet.objects.filter(lookup=voter_hash)
    if not voter_data_obj:
        voter_data_obj = QuestionSheet(questions=voterdata, lookup=voter_hash)
        voter_data_obj.save()
    else:
        voter_data_obj = voter_data_obj[0]
    max_distance = max_d(voterdata)
    context = {'data': sorted(
        [(
            cand, 1.0 - (
                float(cand.compare(voterdata))/float(max_distance)
            )) for cand in Candidate.objects.filter(
                election__slug=election
            ) if cand.last_answers],
        key=lambda i:i[1], reverse=True),
               'election':election}
    perm_result = [(rank, cand.pk, percent) for rank, (cand, percent) in zip(xrange(1, len(context['data']) + 1), context['data'])]
    pr_hash = sha1(str(perm_result)).hexdigest
    pr_obj = PermanentResult.objects.filter(lookup=pr_hash)
    if not pr_obj:
        pr_obj = PermanentResult(ranks=perm_result, lookup=pr_hash)
        pr_obj.save()
    else:
        pr_obj = pr_obj[0]
    request.session['candlist'] = pr_hash
    request.session['voterdata'] = voter_hash
    return context


@user_passes_test(lambda u: u.is_superuser)
@render_with("voter_form.html")
def load_answers(request, election, lookup):
    qs_obj = get_object_or_404(QuestionSheet, lookup=lookup)
    form = VoterForm(election=election, initial=qs_obj.questions)
    return { 'voterform':form, 'election':election }


@user_passes_test(lambda u: u.is_superuser)
@render_with("comparison_page.html")
def comparison_page(request, election, lookup):
    pr_obj = get_object_or_404(PermanentResult, lookup=lookup)
    return { 'data': pr_obj.ranks }

    
"""
@render_with("candidate_page.html")
def candidate_page(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    questions = Question.objects.filter(active=True).order_by('pk')
    if candidate.last_answers:
        la = dict(candidate.last_answers)
        context = {'answers':True, 'questions':[(q,la.get("t_%s"%q.pk, ""), la.get("q_%s"%q.pk,6)) for q in questions], 'cand':candidate}
        if 'voterdata' in request.session:
            pass
        return context
    else:
        return {'answers':False, 'cand':candidate }

"""
