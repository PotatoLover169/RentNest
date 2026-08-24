from django.contrib.auth import get_user_model
from django.db import transaction


User = get_user_model()


class AccountService:
    """
    Business logic for RentNest user accounts.

    API views should not directly handle account creation
    or other account-related business operations.
    """

    @staticmethod
    @transaction.atomic
    def register_user(
        *,
        email,
        password,
        first_name,
        last_name,
    ):
        """
        Register a new RentNest user.

        Public registration always creates a TENANT account.
        Administrative roles must never be assigned through
        the public registration endpoint.
        """

        email = email.strip().lower()

        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
        )

        return user