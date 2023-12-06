from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from pprint import pprint

# REFERENCE: https://stackoverflow.com/questions/40684838/django-django-allauth-save-extra-data-from-social-login-in-signal
# REFERENCE: https://stackoverflow.com/questions/28897220/django-allauth-social-account-connect-to-existing-account-on-login
# REFERENCE: https://django-allauth.readthedocs.io/en/latest/socialaccount/signals.html

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        socialuser = sociallogin.user
        # existing social account
        if socialuser.id:
            return
        try:
            # connect new social account w existing local account
            user = User.objects.get(email=socialuser.email)
            sociallogin.connect(request, user)
            socialuser_data = SocialAccount.objects.get(user=user).extra_data
            pprint(socialuser_data)
            user.first_name = socialuser_data['given_name']
            user.last_name = socialuser_data['family_name']
            user.save()
        except User.DoesNotExist:
            # create new social and local account
            pass
