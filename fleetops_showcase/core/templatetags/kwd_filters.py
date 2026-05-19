from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()


from core.middleware import get_current_request

@register.filter
def kwd(value):
    """Format a decimal value as currency with 3 decimal places.
    
    Usage: {{ invoice.cash|kwd }} → "1,234.500 KWD"
    """
def _get_currency():
    req = get_current_request()
    currency = 'KWD'
    try:
        settings_obj = __import__('core').models.SystemSettings.objects.first()
        if settings_obj and settings_obj.currency:
            currency = settings_obj.currency
    except Exception:
        pass
        
    if req and hasattr(req, 'user') and req.user.is_authenticated:
        if hasattr(req.user, 'company') and req.user.company and getattr(req.user.company, 'currency', None):
            currency = req.user.company.currency
            
    return currency

@register.filter
def kwd(value):
    """Format a decimal value as currency with 3 decimal places.
    
    Usage: {{ invoice.cash|kwd }} → "1,234.500 KWD"
    """
    currency = _get_currency()
    try:
        d = Decimal(str(value))
        formatted = f"{d:,.3f}"
        return f"{formatted} {currency}"
    except (InvalidOperation, TypeError, ValueError):
        return f"0.000 {currency}"


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
    """Very basic number to words converter for currency."""
    currency = _get_currency()
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
            words.append(currency)
        
        if fils > 0:
            if kd > 0: words.append("and")
            words.append(n2w(fils))
            words.append("Cents/Fils")
        
        if not words: return f"Zero {currency}"
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
