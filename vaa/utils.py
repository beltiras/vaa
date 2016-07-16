from random import choice

from django.shortcuts import render


def trunc(text, size):
    return text[:size] + (" ..." if len(text) > size else "")


def max_d(dataset):
    return sum([[4,3,2,3,4,1][q-1]*i for q, i in zipvalues(dataset)])


def zipvalues(dataset, d=False):
    dataset = dict(dataset)
    if not d:
        return [(int(dataset['q_'+str(i)]), int(dataset['i_'+str(i)])) for i in xrange(1,len(dataset)/2+1)]    
    else:
        return dict([('q_%s' % i, (int(dataset['q_'+str(i)]), int(dataset['i_'+str(i)]))) for i in xrange(1,len(dataset)/2+1)])

class render_with:
    def __init__(self, template):
        self.template = template

    def __call__(self, f):
        def wrapped(*args, **kwargs):
            return render(args[0], self.template, f(*args, **kwargs))
        return wrapped

def randstring(length, charset="abcdefghijklmnopqrstuvxyzABCDEFGHIJKLMNOPQRSTUVXYZ01234567890.!"):
    return "".join([choice(charset) for x in xrange(length)])
