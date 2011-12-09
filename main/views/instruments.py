from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required

from main.forms import InstrumentForm

@login_required
def add_instrument(request):
    if request.method == "POST":
        form = InstrumentForm(data = request.POST)
        if form.is_valid():
            instrument = form.save(commit=True)
            return HttpResponseRedirect(reverse('instrument_list'))
    else:
        form = InstrumentForm()
    return render_to_response('main/instruments/instrument_add.html', {'form':form}, context_instance=RequestContext(request))