from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.template.context import RequestContext
from django.contrib.auth import authenticate, login
from main.views import admin_required, active_required
from datetime import datetime, timedelta

from django.views.generic import ListView
from main.views import ActiveViewMixin

from main.forms import ContactForm, MyPasswordChangeForm
from main.models import UserProfile
from django.contrib.auth.models import User

import registration


@active_required
def edit_profile(request):
    user = request.user
    form = ContactForm(data = request.POST or None, instance = user)
    if form.is_valid():
        form.save(commit=True)
        return HttpResponseRedirect(reverse('profile'))
    return render_to_response('main/accounts/edit_contact.html', {'form': form, 'target_user': user},
                                                                context_instance=RequestContext(request))

@active_required
def view_profile(request, slug=None, password_changed=False):
    target_userprofile = get_object_or_404(UserProfile, slug=slug) if slug else request.user.get_profile()
    return render_to_response('main/accounts/profile.html', {'target_user': target_userprofile.user,
                                                                'password_changed': password_changed},
                                                                context_instance=RequestContext(request))


class ListAccounts(ListView, ActiveViewMixin):
    def get_queryset(self):
        return User.objects.filter(last_login__gte=datetime.now()-timedelta(365), is_active=True).order_by('userprofile__name')
    
    template_name = 'main/accounts/accounts_list.html'


class ProfilePastEvents(ListView, ActiveViewMixin):
    def get_queryset(self):
        self.userprofile = get_object_or_404(UserProfile, slug=self.kwargs['slug'])
        return self.userprofile.get_past_events()
    
    def get_context_data(self, **kwargs):
        context = super(ProfilePastEvents, self).get_context_data(**kwargs)
        context['target_user'] = self.userprofile.user
        return context
    
    template_name = 'main/accounts/profile_past_events.html'


@active_required
def change_password(request):
    user = request.user
    form = MyPasswordChangeForm(data = request.POST or None, user=user)
    if form.is_valid():
        form.save(commit=True)
        return redirect(reverse('password_changed'))
    return render_to_response('main/accounts/change_password.html', {'form': form, 'target_user': user},
                                                                    context_instance=RequestContext(request))

@admin_required
def moderate_new_users(request, **kwargs):
    if request.method == "POST":
        if request.POST.has_key('approve'):
            return registration.views.activate(request, **kwargs)
        if request.POST.has_key('deny'):
            registration.models.RegistrationProfile.objects.get(activation_key=kwargs['activation_key']).user.delete()
    return HttpResponseRedirect(reverse('admin_home'))
