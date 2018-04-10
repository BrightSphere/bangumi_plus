from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, BasePermission, SAFE_METHODS
from rest_framework.response import Response

from bangumi.models import UserInfo
from recommendation.models import Recommendation, RecommendationDetail, LikeLog
from recommendation.serializers import RecommendationSerializer, RecommendationDetailSerializer, \
    RecommendationDetailCreateSerializer


class RecommendationViewSet(viewsets.GenericViewSet,
                            mixins.RetrieveModelMixin):
    queryset = Recommendation.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = RecommendationSerializer


class IsOwnerOrReadOnly(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.user.user == request.user


class RecommendationDetailViewSet(viewsets.GenericViewSet,
                                  mixins.RetrieveModelMixin,
                                  mixins.UpdateModelMixin,
                                  mixins.CreateModelMixin):
    queryset = RecommendationDetail.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = RecommendationDetailSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return RecommendationDetailCreateSerializer
        return self.serializer_class

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer = self.serializer_class(serializer.instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def _like(self, obj, request, type=LikeLog.LIKE):
        try:
            user_info = UserInfo.objects.get(user=request.user)
            like_log, created = LikeLog.objects.get_or_create(user=user_info,
                                                              recommendation_detail=obj,
                                                              defaults={
                                                                  "score": type
                                                              })

            if like_log.score == type and not created:
                like_log.delete()
                return Response({"like_status": 0})
            else:
                like_log.score = type
                like_log.save()

            return Response({"like_status": like_log.score})

        except UserInfo.DoesNotExist:
            return Response({"detail": "User have no bangumi user info."},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def like(self, request, pk):
        obj = self.get_object()
        return self._like(obj, request, type=LikeLog.LIKE)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def dislike(self, request, pk):
        obj = self.get_object()
        return self._like(obj, request, type=LikeLog.DISLIKE)


