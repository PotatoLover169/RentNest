from rest_framework import generics, permissions, status
from rest_framework.response import Response

from apps.notifications.models import Notification
from apps.notifications.services import NotificationService

from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    """
    List notifications belonging to the authenticated user.
    """

    serializer_class = NotificationSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user,
        )


class NotificationDetailView(generics.RetrieveAPIView):
    """
    Retrieve a notification belonging to the authenticated user.
    """

    serializer_class = NotificationSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user,
        )


class NotificationMarkReadView(generics.GenericAPIView):
    """
    Mark one of the authenticated user's notifications as read.
    """

    serializer_class = NotificationSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def post(self, request, *args, **kwargs):
        notification = generics.get_object_or_404(
            Notification,
            pk=kwargs["pk"],
            recipient=request.user,
        )

        notification = NotificationService.mark_as_read(
            notification_instance=notification,
        )

        return Response(
            NotificationSerializer(notification).data,
            status=status.HTTP_200_OK,
        )


class NotificationMarkUnreadView(generics.GenericAPIView):
    """
    Mark one of the authenticated user's notifications as unread.
    """

    serializer_class = NotificationSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def post(self, request, *args, **kwargs):
        notification = generics.get_object_or_404(
            Notification,
            pk=kwargs["pk"],
            recipient=request.user,
        )

        notification = NotificationService.mark_as_unread(
            notification_instance=notification,
        )

        return Response(
            NotificationSerializer(notification).data,
            status=status.HTTP_200_OK,
        )


class NotificationMarkAllReadView(generics.GenericAPIView):
    """
    Mark all unread notifications belonging to the authenticated
    user as read.
    """

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def post(self, request, *args, **kwargs):
        updated_count = NotificationService.mark_all_as_read(
            recipient=request.user,
        )

        return Response(
            {
                "message": "Notifications marked as read.",
                "updated_count": updated_count,
            },
            status=status.HTTP_200_OK,
        )


class NotificationDeleteView(generics.DestroyAPIView):
    """
    Delete one of the authenticated user's notifications.
    """

    serializer_class = NotificationSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user,
        )