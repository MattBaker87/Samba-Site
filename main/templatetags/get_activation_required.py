from django import template
from registration.models import RegistrationProfile

from datetime import datetime

register = template.Library()

def do_get_activation_required(parser, token):
    """
        {% get_activation_required as <var_value> %}
    """
    parts = token.split_contents()
    if len(parts) != 3 or parts[1] != 'as':
        raise template.TemplateSyntaxError("'get_activation_required' tag must be of the form:  {% get_activation_required as <var_value> %}")
    return GetActivationRequiredNode(parts[2])

class GetActivationRequiredNode(template.Node):
    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        users = RegistrationProfile.objects.filter(id__in=[x.id for x in \
                                        RegistrationProfile.objects.all() if not x.activation_key_expired()]).order_by('user')
        context[self.var_name] = users
        return u""

register.tag('get_activation_required', do_get_activation_required)