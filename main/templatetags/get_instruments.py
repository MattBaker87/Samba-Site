from django import template
from main.models import Instrument

register = template.Library()

def do_get_instruments(parser, token):
    """
        {% get_instruments as <var_value> [mia [<user>]]%}
    """
    parts = token.split_contents()
    if not (len(parts) == 3 and parts[1] == 'as') and not ((len(parts) == 4 or len(parts) == 5) and parts[1] == 'as' and parts[3] == 'mia'):
        raise template.TemplateSyntaxError("'get_instruments' tag must be of the form:  {% get_instruments as <var_value> %}")
    mia = len(parts) >= 4
    user = parts[4] if len(parts) == 5 else None
    return GetInstrumentsNode(parts[2], mia, user)

class GetInstrumentsNode(template.Node):

    def __init__(self, var_name, mia, user):
        self.var_name = var_name
        self.user = template.Variable(user) if user else None
        self.mia = mia

    def render(self, context):
        try:
            user = self.user.resolve(context) if self.user else None
        except template.VariableDoesNotExist:
            return u""
        instruments = Instrument.objects.all()
        if self.mia and self.user:
            instruments = instruments.filter(id__in=[i.id for i in instruments if i.bookings.not_signed_in().filter(user=user).exists()])
        elif self.mia:
            instruments = instruments.filter(id__in=[i.id for i in instruments if i.bookings.not_signed_in().exists()])
        context[self.var_name] = instruments
        return u""

register.tag('get_instruments', do_get_instruments)