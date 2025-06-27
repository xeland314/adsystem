from rest_framework import serializers
from ads.models import Ad, Campaign, Keyword, Carousel


class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ['name']


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = ['name', 'start_date', 'end_date', 'budget', 'target_audience', 'is_active']


class AdSerializer(serializers.ModelSerializer):
    campaign = CampaignSerializer(read_only=True)
    target_keywords = KeywordSerializer(many=True, read_only=True)

    class Meta:
        model = Ad
        fields = [
            'id',
            'name',
            'image',
            'target_url',
            'is_active',
            'total_clicks',
            'total_impressions',
            'campaign',
            'target_age_min',
            'target_age_max',
            'target_gender',
            'target_location',
            'target_keywords',
            'display_start_time',
            'display_end_time',
            'display_days_of_week',
            'ab_test_group',
        ]


class CarouselSerializer(serializers.ModelSerializer):
    ads = AdSerializer(many=True, read_only=True)

    class Meta:
        model = Carousel
        fields = [
            'id',
            'name',
            'ads',
            'is_active',
            'campaign',
        ]
