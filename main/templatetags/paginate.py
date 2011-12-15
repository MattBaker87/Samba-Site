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
    def display_pages(self, page, last_page):
        DISPLAY_LENGTH = 10
        if last_page <= DISPLAY_LENGTH:
            return range(1, last_page + 1)
            
        if page <= math.ceil(float(DISPLAY_LENGTH)/2):
            display_p = list(range(1, DISPLAY_LENGTH - 1))
            display_p.extend(['...', last_page])
            return display_p
        
        if page >= last_page - math.ceil(float(DISPLAY_LENGTH)/2):
            display_p = [1, '...']
            display_p.extend(range(last_page - DISPLAY_LENGTH + 3, last_page + 1))
            return display_p
        
        display_p = [1, '...']
        display_p.extend(range(page - int(math.ceil(float(DISPLAY_LENGTH)/2)) + 3, page + int(DISPLAY_LENGTH/2) -1))
        display_p.extend(['...', last_page])
        return display_p

    def render(self, context):
        t = template.loader.get_template('main/utils/paginate.html')
        if context['pages'] > 1:
            return t.render(template.Context({
                                            'has_previous': context['has_previous'],
                                            'previous': context['previous'],
                                            'has_next': context['has_next'],
                                            'next': context['next'],
                                            'page': context['page'],
                                            'page_range': self.display_pages(context['page'], context['pages']),
                                            }))
        else:
            return ''

register.tag('pagination', do_display_pagination)