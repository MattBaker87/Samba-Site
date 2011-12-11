from django.forms.widgets import SplitDateTimeWidget, DateInput, TimeInput

class MySplitDateTimeWidget(SplitDateTimeWidget):
    def __init__(self, date_placeholder=None, time_placeholder=None, *args, **kwargs):
        super(MySplitDateTimeWidget, self).__init__(*args, **kwargs)
        if date_placeholder:
            self.widgets[0].attrs.update({'placeholder':date_placeholder})
        if time_placeholder:
            self.widgets[1].attrs.update({'placeholder':time_placeholder})
