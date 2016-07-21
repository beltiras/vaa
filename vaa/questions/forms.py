# encoding=utf8

from django import forms
from django.conf import settings

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, HTML, Fieldset, Field
from crispy_forms.bootstrap import InlineRadios
from charsleft_widget.widgets import CharsLeftInput

from .models import Question, AnswerText


class UserForm(forms.Form):
    first_name = forms.CharField(
        label=u"Fornafn",
        max_length=40,
        widget=forms.TextInput(attrs={'size': '40'})
    )
    last_name = forms.CharField(
        label=u"Föðurnafn",
        max_length=40,
        widget=forms.TextInput(attrs={'size': '40'})
    )
    ssn = forms.CharField(
        label=u"Kennitala (dddddd-dddd)",
        max_length=11,
        widget=forms.TextInput(attrs={'size': '12'})
    )
    last_answer = forms.DateTimeField(label=u"Spurningum svarað", required=False)
    picture = forms.ImageField(label=u"Mynd (til kynningar)", required=False)
    blurb = forms.CharField(
        label=u"Kynningartexti frambjóðanda",
        max_length=2000,
        widget=forms.Textarea,
        required=False,

    )

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(UserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-userform'
        self.helper.form_method = 'post'
        self.helper.form_action = '/userupdate/'
        self.helper.layout = Layout(
            'first_name',
            'last_name',
            'ssn',
            'picture',
            'blurb',
            'last_answer',
            HTML('<div class="col-xs-12"><a class="btn btn-primary" href="/candanswer/">Svara spurningum</a></div>')
        )
        self.helper.add_input(Submit('submit', 'Vista'))


class AnswerForm(forms.Form):
    def __init__(self, *args, **kwargs):
        initial = kwargs.pop('initial', None)
        lang = kwargs.pop('language', "IS")
        election = kwargs.pop('election', 'reykjavik2016') # TODO: generalize the default
        answertexts = AnswerText.objects.filter(lang=lang).order_by('mod') 
        choices = [(str(at.mod), at.text) for at in answertexts]
        super(AnswerForm, self).__init__(*args, **kwargs)
        qs = [q.pk for q in Question.objects.filter(active=True, election__slug=election)]
        for question in Question.objects.filter(active=True):
           self.fields['q_%s' % question.pk] = forms.ChoiceField(
               label=question.questiontext_set.filter(lang=lang)[0].text,
               widget=forms.RadioSelect,
               choices=choices,
           )
           self.fields['t_%s' % question.pk] = forms.CharField(
               label=u"Nánari skýring á afstöðu",
               max_length=500,
               widget=CharsLeftInput(),
               required=False,
           )
           if initial:
               self.fields['t_%s' % question.pk].initial = initial.pop('t_%s' % question.pk)
               self.fields['q_%s' % question.pk].initial = initial.pop('q_%s' % question.pk)

        self.helper = FormHelper(self)
        self.helper.form_id = 'id-answerform'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = 'post'
        self.helper.form_action = '/candans/'
        layout = zip([Field("q_%s" % q) for q in qs], [Field("t_%s"%q) for q in qs])
        self.helper.layout = Layout(*layout)
        self.helper.add_input(Submit('submit', 'Vista'))

    def get_data(self):
        return self.cleaned_data.items()


class VoterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        lang = kwargs.pop('language', "IS")
        election = kwargs.pop('election', 'reykjavik2016')
        answertexts = AnswerText.objects.filter(lang=lang).order_by('mod') 
        choices = [(str(at.mod), at.text) for at in answertexts]
        super(VoterForm, self).__init__(*args, **kwargs)
        qs = [q.pk for q in Question.objects.filter(active=True)]
        for question in Question.objects.filter(active=True, election__slug=election):
           self.fields['q_%s' % question.pk] = forms.ChoiceField(
               label=question.questiontext_set.filter(lang=lang)[0].text,
               widget=forms.RadioSelect,
               choices=choices,
           )
           self.fields['i_%s' % question.pk] = forms.ChoiceField(
               label=u"Mikilvægi spurningar",
               widget=forms.RadioSelect,
               choices=[(1,1),(2,2),(3,3),(4,4),(5,5)],
               initial=3
           )
        self.helper = FormHelper(self)
        self.helper.form_id = 'id-answerform'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = 'post'
        self.helper.form_action = '/compare/'
        layout = zip([Field("q_%s" % q) for q in qs], [InlineRadios("i_%s"%q) for q in qs])
        self.helper.layout = Layout(*layout)
        self.helper.add_input(Submit('submit', u'Fá samanburð'))

    def get_data(self):
        return self.cleaned_data.items()
