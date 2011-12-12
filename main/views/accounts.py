from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.template.context import RequestContext
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from main.forms import UserSignupForm, ContactForm

def signup(request):
    if request.user.is_authenticated():
        return HttpResponse("You're already logged in") #TODO Fail more cleanly if authenticated user tries to sign up

    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            user = authenticate(username=user.username, password=form.cleaned_data['password1'])
            login(request, user)
            return HttpResponseRedirect(reverse('home'))
    else:
        form = UserSignupForm()

    return render_to_response('main/accounts/signup.html', {'form': form}, context_instance=RequestContext(request))


@login_required
def edit_profile(request):
    user = request.user
    form = ContactForm(data = request.POST or None, instance = user)
    if form.is_valid():
        form.save(commit=True)
        return HttpResponseRedirect(reverse('profile'))

    return render_to_response('main/accounts/edit_contact.html', {'form':form}, context_instance=RequestContext(request))