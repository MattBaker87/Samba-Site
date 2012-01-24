from django import template
from main.models import Instrument

register = template.Library()

def do_get_instruments(parser, token):
    """
        {% get_instruments as <var_value> [mia [<user>] | not_signed_in [<user>]] %}
    """
    parts = token.split_contents()
    if not (len(parts) == 3 and parts[1] == 'as') and not ((len(parts) == 4 or len(parts) == 5) \
                                and parts[1] == 'as' and parts[3] in ('mia', 'not_signed_in', 'just_played')):
        raise template.TemplateSyntaxError("'get_instruments' tag must be of the form: \
                                {% get_instruments as <var_value> [mia [<user>] | not_signed_in [<user>]] %}")
    cat = parts[3] if len(parts) >= 4 else None
    user = parts[4] if len(parts) == 5 else None
    return GetInstrumentsNode(parts[2], cat, user)

class GetInstrumentsNode(template.Node):
    def __init__(self, var_name, cat, user):
        self.var_name = var_name
        self.user = template.Variable(user) if user else None
        self.cat = cat

    def render(self, context):
        try:
            user = self.user.resolve(context) if self.user else None
        except template.VariableDoesNotExist:
            return u""
        if self.cat == 'mia':
            instruments = sorted(Instrument.live.mia(user), key=lambda x: x.get_next_needed_date())
        elif self.cat == 'not_signed_in':
            instruments = sorted(Instrument.live.not_signed_in(user), key=lambda x: x.get_next_needed_date())
        elif self.cat == 'just_played':
            instruments = sorted(Instrument.live.just_played(user), key=lambda x: x.get_next_needed_date())
        else:
            instruments = Instrument.live.all()
        context[self.var_name] = instruments
        return u""

register.tag('get_instruments', do_get_instruments)