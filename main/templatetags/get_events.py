from django import template
from main.models import Event

from datetime import datetime

register = template.Library()

def do_get_future_events(parser, token):
    """
        {% get_future_events as <var_value> %}
    """
    parts = token.split_contents()
    if len(parts) != 3 or parts[1] != 'as':
        raise template.TemplateSyntaxError("'get_future_events' tag must be of the form:  {% get_future_events as <var_value> %}")
    return GetFutureEventsNode(parts[2])

class GetFutureEventsNode(template.Node):

    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        events = Event.objects.filter(start__gte=datetime.now()).order_by('start')
        context[self.var_name] = events
        return u""

register.tag('get_future_events', do_get_future_events)