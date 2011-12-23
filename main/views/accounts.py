from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.utils.functional import lazy
from datetime import datetime, timedelta

from django.views.generic import ListView, UpdateView, DetailView, TemplateView
from main.views import ActiveViewMixin, AdminViewMixin

from main.forms import ContactForm, MyPasswordChangeForm

from main.models import UserProfile
from django.contrib.auth.models import User

import registration

reverse_lazy = lazy(reverse, str)


class EditProfile(UpdateView, ActiveViewMixin):
    form_class = ContactForm
    template_name = 'main/accounts/edit_contact.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super(EditProfile, self).get_context_data(**kwargs)
        context['target_user'] = self.request.user
        return context


class ViewProfile(DetailView, ActiveViewMixin):
    template_name = 'main/accounts/profile.html'
    context_object_name = 'target_user'
    
    def get_object(self):
        return get_object_or_404(UserProfile, slug=self.kwargs['slug']).user if 'slug' in self.kwargs else self.request.user
    
    def get_context_data(self, **kwargs):
        context = super(ViewProfile, self).get_context_data(**kwargs)
        context['password_changed'] = bool('password_changed' in self.kwargs)
        return context


class ListAccounts(ListView, ActiveViewMixin):
    template_name = 'main/accounts/accounts_list.html'
    def get_queryset(self):
        return User.objects.filter(last_login__gte=datetime.now()-timedelta(365), is_active=True).order_by('userprofile__name')


class ProfilePastEvents(ListView, ActiveViewMixin):
    template_name = 'main/accounts/profile_past_events.html'
    def get_queryset(self):
        self.userprofile = get_object_or_404(UserProfile, slug=self.kwargs['slug'])
        return self.userprofile.get_past_events()
    
    def get_context_data(self, **kwargs):
        context = super(ProfilePastEvents, self).get_context_data(**kwargs)
        context['target_user'] = self.userprofile.user
        return context


class ChangePassword(UpdateView, ActiveViewMixin):
    form_class = MyPasswordChangeForm
    template_name = 'main/accounts/change_password.html'
    success_url = reverse_lazy('password_changed')

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super(ChangePassword, self).get_context_data(**kwargs)
        context['target_user'] = self.request.user
        return context
    
    def get_form_kwargs(self):
        kwargs = super(ChangePassword, self).get_form_kwargs()
        kwargs.pop('instance')
        kwargs['user'] = self.object
        return kwargs


class ModerateNewUser(TemplateView, AdminViewMixin):
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse_lazy('admin_users'))
    
    def post(self, request, *args, **kwargs):
        if self.request.POST.has_key('approve'):
            return registration.views.activate(request, **self.kwargs)
        if self.request.POST.has_key('deny'):
            registration.models.RegistrationProfile.objects.get(activation_key=kwargs['activation_key']).user.delete()
            return HttpResponseRedirect(reverse('admin_users_denied'))

