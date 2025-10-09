from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.utils import timezone
from monitor.models import Chick, TemperatureReading, FeverAlert
from .serializers import TempSerializer
from drf_spectacular.utils import extend_schema

@extend_schema(
    request=TempSerializer,
)
@api_view(['GET', 'POST'])
def monitor(request):
    if request.method == 'GET':
        return Response({"message": "example of get requests"}, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = TempSerializer(data=request.data)
        if serializer.is_valid():
            temp = serializer.validated_data['temp']
            tag_id = f"U{timezone.now().strftime('%Y%m%d%H%M%S%f')}"
            chick = Chick.objects.create(
                name=f"Unknown Chick {timezone.now().strftime('%H%M%S')}",
                tag_id=tag_id
            )

            TemperatureReading.objects.create(
                chick=chick,
                temperature=temp
            )
            FeverAlert.objects.create(
                chick=chick,
                temperature=temp,
                recorded_at=timezone.now(),
            )
            
            return Response({"message": temp}, status=status.HTTP_201_CREATED)