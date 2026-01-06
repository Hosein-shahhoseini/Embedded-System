from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from .models import ExpoPushToken, Pill, History
from .serializers import ExpoTokenSerializer, IntakeRequestSerializer, PillSerializer, HistorySerializer
from django.shortcuts import get_object_or_404

class PillHistoryAPI(APIView):
    @extend_schema(responses={200: HistorySerializer(many=True)}, summary="دریافت تاریخچه مصرف")
    def get(self, request):
        history = History.objects.all().order_by('-timestamp')[:50] 
        serializer = HistorySerializer(history, many=True)
        return Response(serializer.data)
    @extend_schema(
        responses={204: {"message": "history cleared"}},
        summary="حذف کامل تاریخچه مصرف داروها"
    )
    def delete(self, request):
        History.objects.all().delete()
        
        return Response({
            "status": "success",
            "message": "تمامی سوابق مصرف با موفقیت حذف شدند."
        }, status=status.HTTP_204_NO_CONTENT)
    
class MedicineDashboardAPI(APIView):
    @extend_schema(responses={200: PillSerializer(many=True)}, summary="دریافت وضعیت محفظه‌ها")
    def get(self, request):
        pills = Pill.objects.all().order_by('container_id')
        return Response(PillSerializer(pills, many=True).data)
    @extend_schema(request=PillSerializer)
    def post(self, request):
        serializer = PillSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            c_id = data['container_id']

            if c_id not in [0, 1]:
                return Response({"error": "فقط محفظه 0 و 1 موجود است."}, status=400)

            existing = Pill.objects.filter(container_id=c_id).first()
            if existing and existing.count > 0 and existing.name != data['name']:
                return Response({"error": f"محفظه {c_id} پر است. ابتدا آن را خالی کنید."}, status=400)

            pill, _ = Pill.objects.update_or_create(
                container_id=c_id,
                defaults={
                    'name': data['name'],
                    'count': data['count'],
                    'interval_value': data['interval_value'],
                    'interval_unit': data['interval_unit'],
                }
            )
            return Response(PillSerializer(pill).data, status=201)
        return Response(serializer.errors, status=400)
    
    @extend_schema(request=PillSerializer, summary="ویرایش اطلاعات داروی موجود")
    def put(self, request):
        """بروزرسانی نام، تعداد یا زمان‌بندی یک محفظه خاص"""
        c_id = request.data.get('id')
        if c_id is None:
            return Response({"error": "ارسال فیلد id الزامی است."}, status=400)

        pill = get_object_or_404(Pill, container_id=c_id)
        
        serializer = PillSerializer(pill, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": f"اطلاعات محفظه {c_id} با موفقیت بروزرسانی شد.",
                "updated_data": serializer.data
            }, status=200)
        
        return Response(serializer.errors, status=400)

class ContainerStatusAPI(APIView):
    def get(self, request):
        data = []
        for i in [0, 1]:
            p = Pill.objects.filter(container_id=i).first()
            data.append({
                "container": i,
                "pill_name": p.name if p else None,
                "count": p.count if p else 0,
                "status": "Empty" if not p or p.count == 0 else "Full"
            })
        return Response(data)

class MockIntakeAPI(APIView):
    @extend_schema(
        request=IntakeRequestSerializer,
        responses={200: HistorySerializer},
        summary="تست مصرف دارو"
    )
    def post(self, request):
        serializer = IntakeRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
            
        c_id = serializer.validated_data['id']
        pill = get_object_or_404(Pill, container_id=c_id)
        
        if pill.count > 0:
            pill.count -= 1
            pill.save()
            
            history_entry = History.objects.create(
                pill=pill, 
                pill_name=pill.name,
                count_after_intake=pill.count
            )
            return Response(HistorySerializer(history_entry).data, status=200)
        
        return Response({"error": "Inventory is zero!"}, status=400)
    
class RegisterTokenAPI(APIView):
    
    @extend_schema(
        request=ExpoTokenSerializer,
        responses={200: {"message": "success"}},
        summary="به‌روزرسانی و جایگزینی توکن (تنها یک توکن در دیتابیس می‌ماند)"
    )
    def put(self, request):
        serializer = ExpoTokenSerializer(data=request.data)
        if serializer.is_valid():
            token_value = serializer.validated_data['token']
            
            ExpoPushToken.objects.all().delete()
            
            obj = ExpoPushToken.objects.create(token=token_value)
            
            return Response({
                "status": "success",
                "message": "توکن قبلی حذف و توکن جدید جایگزین شد",
                "token": token_value
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={204: {"message": "all tokens deleted"}},
        summary="حذف کامل تمام توکن‌های موجود"
    )
    def delete(self, request):
        ExpoPushToken.objects.all().delete()
        return Response({
            "status": "success",
            "message": "تمام توکن‌ها با موفقیت پاک شدند"
        }, status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        responses={200: ExpoTokenSerializer(many=True)},
        summary="مشاهده لیست توکن‌ها"
    )
    def get(self, request):
        tokens = ExpoPushToken.objects.all()
        serializer = ExpoTokenSerializer(tokens, many=True)
        return Response(serializer.data)

    @extend_schema(exclude=True) 
    def post(self, request):
        return self.put(request)
    