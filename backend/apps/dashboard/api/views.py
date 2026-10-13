from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.api.serializers import NotificationSerializer
from apps.notifications.models import Notification
from apps.dashboard.services import get_dashboard_summary


class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        recent_notifications = Notification.objects.filter(
            recipient=user
        ).order_by("-created_at", "-id")[:5]

        return Response(
            {
                "role": user.role,
                "summary": get_dashboard_summary(user),
                "recent_notifications": NotificationSerializer(
                    recent_notifications,
                    many=True,
                    context={"request": request},
                ).data,
            }
        )
