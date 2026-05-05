from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()


@register.filter
def kwd(value):
    """Format a decimal value as Gulfi Dinar with 3 decimal places.
    
    Usage: {{ invoice.cash|kwd }} → "1,234.500 KD"
    """
    try:
        d = Decimal(str(value))
        formatted = f"{d:,.3f}"
        return f"{formatted} KD"
    except (InvalidOperation, TypeError, ValueError):
        return "0.000 KD"


@register.filter
def format_hours(value):
    """Format decimal hours as Xh Ym.
    
    Usage: {{ total_hours|format_hours }} → "168h 30m"
    """
    try:
        total = float(value)
        hours = int(total)
        minutes = int((total - hours) * 60)
        return f"{hours}h {minutes}m"
    except (TypeError, ValueError):
        return "0h 0m"
@register.filter
def amount_in_words(value):
    """Very basic number to words converter for KD."""
    try:
        total = float(value)
        kd = int(total)
        fils = int(round((total - kd) * 1000))
        
        def n2w(n):
            units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
            tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
            if n < 20: return units[n]
            if n < 100: return tens[n // 10] + (("-" + units[n % 10]) if n % 10 != 0 else "")
            if n < 1000: return units[n // 100] + " Hundred" + ((" and " + n2w(n % 100)) if n % 100 != 0 else "")
            return str(n)

        words = []
        if kd > 0:
            words.append(n2w(kd))
            words.append("Gulfi Dinar")
        
        if fils > 0:
            if kd > 0: words.append("and")
            words.append(n2w(fils))
            words.append("Fils")
        
        if not words: return "Zero KD"
        return " ".join(words) + " Only"
    except (TypeError, ValueError):
        return ""
@register.filter
def subtract(value, arg):
    """Subtract arg from value."""
    try:
        return Decimal(str(value)) - Decimal(str(arg))
    except (InvalidOperation, TypeError, ValueError):
        return value
