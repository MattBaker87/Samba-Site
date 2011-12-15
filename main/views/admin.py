from main.views import admin_required
from main.views.events import list_events
from django.views.generic import simple

@admin_required
def admin_direct_to_template(request, template):
    return simple.direct_to_template(request, template=template)

@admin_required
def admin_home(request):
    return list_events(request, queryset_filter=lambda x:x.future_events(),
                                    template_name='main/admin_home.html', paginate_by=5)