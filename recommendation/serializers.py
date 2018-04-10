from rest_framework import serializers

from bangumi.models import Subject, UserInfo
from bangumi.serializers import BasicSubjectSerializer, UserInfoSerializer
from recommendation.models import Recommendation, RecommendationDetail, LikeLog
from recommendation.services import RecommendationService


class RecommendationDetailCreateSerializer(serializers.ModelSerializer):
    subject_1 = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), required=True)
    subject_2 = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), required=True)

    def validate(self, attrs):
        if attrs["subject_1"] == attrs["subject_2"]:
            raise serializers.ValidationError("Two subjects should be different.")
        return attrs

    class Meta:
        model = RecommendationDetail
        fields = ('comment', 'subject_1', 'subject_2')
        extra_kwargs = {'comment': {'required': True}}

    def create(self, validated_data):
        rmd = RecommendationService().get_or_create_recommendation(
            [validated_data["subject_1"], validated_data["subject_2"]],
            False
        )
        return RecommendationDetail.objects.create(recommendation=rmd,
                                                   comment=validated_data["comment"],
                                                   user=UserInfo.objects.get(user=self.context.get("request").user))


class RecommendationDetailSerializer(serializers.ModelSerializer):
    user = UserInfoSerializer(read_only=True)
    like_status = serializers.SerializerMethodField()

    def get_like_status(self, obj):
        if not obj:
            return 0
        try:
            user_info = UserInfo.objects.get(user=self.context.get("request").user)
            like_log = LikeLog.objects.get(user=user_info,
                                           recommendation_detail=obj)
            return like_log.score
        except(AttributeError, UserInfo.DoesNotExist, LikeLog.DoesNotExist):
            return 0

    class Meta:
        model = RecommendationDetail
        fields = ('id', 'recommendation', 'comment', 'like_count', 'update_time', 'user', 'like_status')
        read_only_fields = ('id', 'recommendation', 'like_count', 'update_time', 'user', 'like_status')


class RecommendationSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()
    subject_bigger = BasicSubjectSerializer()
    subject_smaller = BasicSubjectSerializer()

    class Meta:
        model = Recommendation
        fields = ('key', 'weight', 'count', 'similarity', 'subject_smaller', 'subject_bigger', 'comments')

    def get_comments(self, obj):
        assert isinstance(obj, Recommendation)
        return RecommendationDetailSerializer(obj.recommendationdetail_set.order_by("-like_count", "-update_time"),
                                              many=True,
                                              context=self.context).data
