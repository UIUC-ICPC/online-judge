"""
Changes the following behavior
1. Disables removing connected accounts
2. Enforces same-email restriction on connected accounts
"""

from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def validate_disconnect(self, account, accounts):
        raise ValidationError("Connected accounts cannot be removed")

    def pre_social_login(self, request, sociallogin):
        super().pre_social_login(request, sociallogin)

        if (
            sociallogin.state.get("process") != "connect"
            or not request.user.is_authenticated
        ):
            return

        expected = request.user.email.casefold()
        matches = expected and any(
            email.verified and email.email.casefold() == expected
            for email in sociallogin.email_addresses
        )

        if not matches:
            # FIXME: these messages aren't actually displayed
            messages.error(
                request,
                "Connect a Google account with the same email address as your account.",
            )
            raise ImmediateHttpResponse(redirect("socialaccount_connections"))
