from rest_framework import serializers

class TempSerializer(serializers.Serializer):
    temp = serializers.FloatField()