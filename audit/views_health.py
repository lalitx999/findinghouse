from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.db import connection
from django.conf import settings
import time

class SystemHealthView(APIView):
    """
    System Health & Operational Status Check Endpoint for Finding House
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        health_status = {
            'status': 'healthy',
            'timestamp': time.time(),
            'services': {
                'database': 'unknown',
                'media_storage': 'unknown',
            }
        }

        # 1. Test Database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                health_status['services']['database'] = 'connected'
        except Exception as e:
            health_status['services']['database'] = f'error: {str(e)}'
            health_status['status'] = 'degraded'

        # 2. Test Media Storage access
        try:
            import os
            media_dir = settings.MEDIA_ROOT
            if os.path.exists(media_dir) or os.access(os.path.dirname(media_dir), os.W_OK):
                health_status['services']['media_storage'] = 'accessible'
            else:
                health_status['services']['media_storage'] = 'read_only'
        except Exception as e:
            health_status['services']['media_storage'] = f'error: {str(e)}'

        http_code = status.HTTP_200_OK if health_status['status'] == 'healthy' else status.HTTP_503_SERVICE_UNAVAILABLE
        return Response(health_status, status=http_code)
