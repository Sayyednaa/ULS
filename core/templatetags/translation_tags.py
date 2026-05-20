
from django import template
from core.translations import TRANSLATIONS

register = template.Library()

@register.simple_tag(takes_context=True)
def atrans(context, text):
    """
    Arabic Translation tag. 
    Usage: {% atrans "Dashboard" %}
    Returns Arabic if context 'lang' is 'ar', else returns original text.
    """
    lang = context.get('lang', 'en')
    # If lang is not in context, try to get from request (if middleware is set)
    if not lang and 'request' in context:
        lang = getattr(context['request'], 'LANGUAGE_CODE', 'en')[:2]
    
    if lang == 'ar':
        return TRANSLATIONS.get(text, text)
    return text

@register.filter(name='t')
def translate_filter(text, lang='en'):
    """
    Filter version of translation.
    Usage: {{ "Dashboard"|t:lang }}
    """
    if lang == 'ar':
        return TRANSLATIONS.get(text, text)
    return text
