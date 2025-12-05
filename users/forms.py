from allauth.account.forms import SignupForm
from django.contrib.auth.models import User

class CustomSignupForm(SignupForm):
    # extra profile fields from template
    def save(self, request):
        user = super().save(request)
        phone = request.POST.get("phone", "").strip()
        default_address = request.POST.get("default_address", "").strip()
        # profile is created by signal; update values
        prof = user.profile
        if phone:
            prof.phone = phone
        if default_address:
            prof.default_address = default_address
        prof.save()
        return user
