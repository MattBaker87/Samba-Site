from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.template.context import RequestContext
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.generic import list_detail

from main.forms import UserSignupForm, ContactForm
from main.models import UserProfile
from django.contrib.auth.models import User


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

@login_required
def view_profile(request, slug=None):
    target_userprofile = get_object_or_404(UserProfile, slug=slug) if slug else request.user.get_profile()
    return render_to_response('main/accounts/profile.html', {'target_user': target_userprofile.user},
                                                                context_instance=RequestContext(request))

@login_required
def list_accounts(request, template_name, queryset_filter, paginate_by=None):
    user_list = queryset_filter(User.objects)
    return render_to_response(template_name, {'user_list': user_list}, context_instance=RequestContext(request))

@login_required
def profile_past_events(request, slug):
    target_userprofile = get_object_or_404(UserProfile, slug=slug)
    queryset = target_userprofile.get_past_events()
    return list_detail.object_list(request, queryset=queryset, template_object_name='event', extra_context={'target_user': target_userprofile.user},
                                    template_name='main/accounts/profile_past_events.html')