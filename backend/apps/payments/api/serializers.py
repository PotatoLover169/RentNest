from rest_framework import serializers

from apps.payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for rental payments.

    Tenant and tenancy ownership are controlled by the API/service
    layer and are not trusted from arbitrary client input.
    """

    tenancy = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    tenant = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        model = Payment

        fields = [
            "id",
            "tenancy",
            "tenant",
            "amount",
            "payment_method",
            "status",
            "payment_date",
            "reference_number",
            "notes",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "tenancy",
            "tenant",
            "status",
            "created_at",
            "updated_at",
        ]

    def validate_amount(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Payment amount cannot be negative."
            )

        return value

    def validate_payment_date(self, value):
        return value

    def validate(self, attrs):
        payment_method = attrs.get(
            "payment_method",
            getattr(self.instance, "payment_method", None),
        )

        reference_number = attrs.get(
            "reference_number",
            getattr(self.instance, "reference_number", ""),
        )

        # Electronic payments should have a reference number.
        if payment_method in {
            "BANK_TRANSFER",
            "GCASH",
            "MAYA",
            "CARD",
        } and not reference_number:
            raise serializers.ValidationError(
                {
                    "reference_number": (
                        "A reference number is required "
                        "for this payment method."
                    )
                }
            )

        return attrs