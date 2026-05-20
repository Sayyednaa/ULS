from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def if_role(context, *roles):
    """Check if the current user has one of the specified roles.
    
    Usage:
        {% load role_tags %}
        {% if_role 'admin' 'manager' as is_staff %}
        {% if is_staff %} ... {% endif %}
    """
    request = context.get('request')
    if request and hasattr(request, 'user') and hasattr(request.user, 'role'):
        return request.user.role in roles
    return False
