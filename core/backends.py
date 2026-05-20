from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        
        try:
            # Check by email or username, case-insensitive
            user = UserModel.objects.get(username__iexact=username)
        except UserModel.DoesNotExist:
            try:
                user = UserModel.objects.get(email__iexact=username)
            except UserModel.DoesNotExist:
                return None
        except UserModel.MultipleObjectsReturned:
            user = UserModel.objects.filter(email__iexact=username).order_by('id').first()

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
