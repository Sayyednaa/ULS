"""Driver Portal Views — Personal dashboard + document status, view own profile."""
from django.shortcuts import render
from core.mixins import DriverRequiredMixin
from core.models import Driver, Notification, Task
from django.views import View


class DriverDashboardView(DriverRequiredMixin, View):
    def get(self, request):
        driver = None
        docs = []
        try:
            driver = request.user.driver_profile
            docs = driver.get_expiring_documents()
        except Driver.DoesNotExist:
            pass

        tasks = Task.objects.filter(user=request.user)
        recent_notifs = Notification.objects.filter(user=request.user, is_read=False)[:5]

        return render(request, 'driver_portal/dashboard.html', {
            'driver': driver,
            'documents': docs,
            'tasks': tasks,
            'recent_notifs': recent_notifs,
        })


class DriverMyProfileView(DriverRequiredMixin, View):
    def get(self, request):
        driver = None
        docs = []
        try:
            driver = request.user.driver_profile
            docs = driver.get_expiring_documents()
        except Driver.DoesNotExist:
            pass

        return render(request, 'driver_portal/my_profile.html', {
            'driver': driver,
            'documents': docs,
        })
