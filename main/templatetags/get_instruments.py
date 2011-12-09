from django import template
from main.models import Instrument

register = template.Library()

def do_get_instruments(parser, token):
    """
        {% get_instruments as <var_value> %}
    """
    parts = token.split_contents()
    if len(parts) != 3 or parts[1] != 'as':
        raise template.TemplateSyntaxError("'get_instruments' tag must be of the form:  {% get_instruments as <var_value> %}")
    return GetInstrumentsNode(parts[2])

class GetInstrumentsNode(template.Node):

    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        instruments = Instrument.objects.all().order_by('name')
        context[self.var_name] = instruments
        return u""

register.tag('get_instruments', do_get_instruments)