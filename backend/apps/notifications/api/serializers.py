from rest_framework import serializers

from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for safely exposing notification data.
    """

    class Meta:
        model = Notification

        fields = [
            "id",
            "notification_type",
            "title",
            "message",
            "is_read",
            "read_at",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "notification_type",
            "title",
            "message",
            "is_read",
            "read_at",
            "created_at",
        ]