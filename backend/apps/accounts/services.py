from django.db import transaction

from .models import User


class AccountService:

    # ============================================================
    # REGISTER USER
    # ============================================================

    @staticmethod
    @transaction.atomic
    def register_user(
        *,
        email,
        password,
        first_name="",
        last_name="",
    ):
        """
        Register a new user.

        Public registration is intended for TENANT accounts.
        Administrative and property manager accounts are created
        through protected administrative workflows.
        """

        email = email.strip().lower()
        first_name = first_name.strip()
        last_name = last_name.strip()

        return User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )