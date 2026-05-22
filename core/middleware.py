import threading
from django.shortcuts import redirect

_thread_locals = threading.local()

def get_current_request():
    return getattr(_thread_locals, 'request', None)

class CurrentRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        try:
            response = self.get_response(request)
        finally:
            _thread_locals.request = None
        return response


class CompanyStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated:
            if getattr(user, 'company', None):
                company = user.company
                path = request.path
                
                allowed_prefixes = [
                    '/logout/',
                    '/company-status/',
                    '/i18n/',
                    '/static/',
                    '/media/',
                ]
                
                is_allowed = any(path.startswith(prefix) for prefix in allowed_prefixes)
                
                if not is_allowed:
                    import datetime
                    today = datetime.date.today()
                    is_expired = False
                    if company.status == 'accepted' and company.access_expiry_date:
                        if company.access_expiry_date < today:
                            is_expired = True
                    
                    if company.status != 'accepted' or company.is_paused or is_expired:
                        return redirect('company_verification_status')
                        
        return self.get_response(request)

