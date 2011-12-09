from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('home'))
    else:
        return HttpResponseRedirect(reverse('login'))
