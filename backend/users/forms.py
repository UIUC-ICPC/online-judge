"""
Prevents user from changing the email connected to their account
after authenticating via OAuth
"""

from allauth.socialaccount.forms import SignupForm


class SocialSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        email = self.initial.get("email")
        if email:
            self.fields["email"].disabled = True
