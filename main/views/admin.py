from main.views import admin_required
from django.views.generic import simple

@admin_required
def admin_direct_to_template(request, template):
    return simple.direct_to_template(request, template=template)