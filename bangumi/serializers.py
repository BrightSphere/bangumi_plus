from itertools import chain

from django.db.models import Q
from rest_framework import serializers

from bangumi.models import Subject, UserInfo
from recommendation.models import Recommendation

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ('uid', 'username', 'nickname', 'avatar')

class BasicSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ('id', 'type', 'cover',
                  'rank', 'rating')


class BasicRecommendationSerializer(serializers.ModelSerializer):
    subject = serializers.SerializerMethodField()

    class Meta:
        model = Recommendation
        fields = ('key', 'weight', 'count', 'similarity', 'auto', 'subject')

    def get_subject(self, obj):
        base_subject = self.context.get("base_subject")
        if base_subject == obj.subject_smaller:
            serializer = BasicSubjectSerializer(obj.subject_bigger)
        else:
            serializer = BasicSubjectSerializer(obj.subject_smaller)
        return serializer.data


class SubjectSerializer(serializers.ModelSerializer):
    recommendations = serializers.SerializerMethodField()

    def get_recommendations(self, obj):
        assert isinstance(obj, Subject)
        rmds = Recommendation.objects.filter(Q(subject_bigger=obj) | Q(subject_smaller=obj))
        human_rmds = rmds.filter(auto=False).order_by("-weight")
        auto_rmds = rmds.filter(auto=True).order_by("-similarity")
        num_of_auto = 10 - len(human_rmds)
        r_rmds = list(chain(human_rmds, auto_rmds[:num_of_auto if num_of_auto > 0 else 0]))
        serializer = BasicRecommendationSerializer(r_rmds, many=True, context={"base_subject": obj})
        return serializer.data

    class Meta:
        model = Subject
        fields = ('id', 'type', 'cover',
                  'rank', 'rating', 'update_time', 'recommendations')


