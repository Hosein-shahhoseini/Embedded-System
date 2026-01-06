from rest_framework import serializers
from .models import Pill, History
import jdatetime
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field

class IntervalSerializer(serializers.Serializer):
    value = serializers.IntegerField(default=8)
    unit = serializers.CharField(default="hour")

class PillSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='container_id')
    interval = IntervalSerializer(source='*')

    class Meta:
        model = Pill
        fields = ['id', 'name', 'count', 'interval', 'is_active']

    def to_internal_value(self, data):
        interval_data = data.get('interval', {})
        return {
            "container_id": data.get('id'),
            "name": data.get('name'),
            "count": data.get('count'),
            "interval_value": interval_data.get('value'),
            "interval_unit": interval_data.get('unit'),
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['interval'] = {
            "value": instance.interval_value,
            "unit": instance.interval_unit
        }
        return representation
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.count = validated_data.get('count', instance.count)
        instance.interval_value = validated_data.get('interval_value', instance.interval_value)
        
        instance.interval_unit = validated_data.get('interval_unit', instance.interval_unit)
        
        instance.save()
        return instance
    
class IntakeRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="آیدی محفظه (0 یا 1)")

class HistorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='pill_name') 
    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    count = serializers.IntegerField(source='count_after_intake')

    class Meta:
        model = History
        fields = ['name', 'date', 'time', 'count']
    

    def get_date(self, obj):
        jd = jdatetime.datetime.fromgregorian(datetime=obj.timestamp)
        return jd.strftime("%Y/%m/%d")

    def get_time(self, obj):
        local_time = timezone.localtime(obj.timestamp)
        return local_time.strftime("%H:%M")

class ExpoTokenSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, help_text="Expo Push Token را اینجا وارد کنید")
    created_at = serializers.DateTimeField(read_only=True)