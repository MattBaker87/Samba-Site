"""
This is the paginator that supports pages generated with class-based generic views. Intention is to migrate
all views to use this
"""

from django import template
import math

register = template.Library()

def do_display_pagination(parser, token):
    """
        {% display_pagination %}
    """
    parts = token.split_contents()
    if len(parts) != 1:
        raise template.TemplateSyntaxError("'display_pagination' tag takes no arguments")
    return DisplayPaginationNode()

class DisplayPaginationNode(template.Node):
    def display_pages(self, page_obj, paginator):
        DISPLAY_LENGTH = 10
        if paginator.num_pages <= DISPLAY_LENGTH:
            return range(1, paginator.num_pages + 1)
            
        if page_obj.number <= math.ceil(float(DISPLAY_LENGTH)/2):
            display_p = list(range(1, DISPLAY_LENGTH - 1))
            display_p.extend(['...', paginator.num_pages])
            return display_p
        
        if page_obj.number >= paginator.num_pages - math.ceil(float(DISPLAY_LENGTH)/2):
            display_p = [1, '...']
            display_p.extend(range(paginator.num_pages - DISPLAY_LENGTH + 3, paginator.num_pages + 1))
            return display_p
        
        display_p = [1, '...']
        display_p.extend(range(page_obj.number - int(math.ceil(float(DISPLAY_LENGTH)/2)) + 3,
                                                                                page_obj.number + int(DISPLAY_LENGTH/2) -1))
        display_p.extend(['...', paginator.num_pages])
        return display_p

    def render(self, context):
        t = template.loader.get_template('main/utils/paginate.html')
        if context['is_paginated']:
            return t.render(template.Context({
                                            'page_obj': context['page_obj'],
                                            'page_range': self.display_pages(context['page_obj'], context['paginator']),
                                            }))
        else:
            return ''

register.tag('display_pagination', do_display_pagination)