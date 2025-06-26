import datetime
from rest_framework import generics
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone

from ads.models import Ad
from ads.serializers import AdSerializer


class AdListAPIView(generics.ListAPIView):
    serializer_class = AdSerializer

    def get_queryset(self):
        today = timezone.now().date()
        now = timezone.now().time()
        current_day_of_week = datetime.datetime.now().strftime("%a").upper()

        queryset = Ad.objects.filter(
            is_active=True,
            campaign__is_active=True,
            campaign__start_date__lte=today,
            campaign__end_date__gte=today,
        )

        # Scheduling filters
        queryset = queryset.filter(
            Q(display_start_time__lte=now) | Q(display_start_time__isnull=True),
            Q(display_end_time__gte=now) | Q(display_end_time__isnull=True),
        )
        queryset = queryset.filter(
            Q(display_days_of_week__icontains=current_day_of_week)
            | Q(display_days_of_week__exact="")
        )

        # Targeting filters (from query parameters)
        user_age = self.request.query_params.get("age")
        user_gender = self.request.query_params.get("gender")
        user_location = self.request.query_params.get("location")
        page_keywords = self.request.query_params.getlist("keywords")
        ab_test_group = self.request.query_params.get("ab_test_group")

        if user_age:
            queryset = queryset.filter(
                Q(target_age_min__lte=user_age) | Q(target_age_min__isnull=True),
                Q(target_age_max__gte=user_age) | Q(target_age_max__isnull=True),
            )
        if user_gender:
            queryset = queryset.filter(
                Q(target_gender=user_gender) | Q(target_gender="A")
            )
        if user_location:
            queryset = queryset.filter(
                Q(target_location__icontains=user_location)
                | Q(target_location__exact="")
            )
        if page_keywords:
            queryset = queryset.filter(
                Q(target_keywords__name__in=page_keywords)
                | Q(target_keywords__isnull=True)
            ).distinct()
        if ab_test_group:
            queryset = queryset.filter(ab_test_group=ab_test_group)

        return queryset.order_by("?")  # Return a random ad from the filtered set

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        ad = queryset.first()  # Get only one ad

        if ad:
            # Increment impressions
            ad.total_impressions += 1
            ad.save()
            serializer = self.get_serializer(ad)
            return Response(serializer.data)
        fallback_ad = (
            Ad.objects.filter(
                is_active=True,
                campaign__is_active=True,
                campaign__start_date__lte=timezone.now().date(),
                campaign__end_date__gte=timezone.now().date(),
                target_age_min__isnull=True,
                target_age_max__isnull=True,
                target_gender="A",
                target_location__exact="",
                target_keywords__isnull=True,
                display_start_time__isnull=True,
                display_end_time__isnull=True,
                display_days_of_week__exact="",
                ab_test_group__exact="",
            )
            .order_by("?")
            .first()
        )

        if fallback_ad:
            fallback_ad.total_impressions += 1
            fallback_ad.save()
            serializer = self.get_serializer(fallback_ad)
            return Response(serializer.data)
        return Response({"detail": "No ad available"}, status=404)
