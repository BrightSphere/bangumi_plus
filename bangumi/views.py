from django.http import Http404
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from bangumi.models import Subject
from bangumi.serializers import SubjectSerializer
from bangumi.services import BangumiService, UserService, RemoteRecommendationService


class TokenViewSet(viewsets.ViewSet):

    def list(self, request):
        code = request.query_params.get("code", None)
        if code is None:
            return Response({"detail": "parameter 'code' not found."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = UserService().get_or_create_user_by_code(code)
            token = UserService().get_or_create_token(user)
            return Response({"token": token.key})
        except RuntimeError as e:
            return Response({"detail": "{}".format(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def reset(self, request):
        token = UserService().reset_token(request.user)
        return Response({"token": token.key})


class SubjectViewSet(viewsets.GenericViewSet,
                     mixins.RetrieveModelMixin):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}

        try:
            obj = get_object_or_404(queryset, **filter_kwargs)
        except Http404 as e:
            pk = filter_kwargs.get("pk", None)
            if pk is None:
                raise e
            obj, dummy = BangumiService().update_or_create_subject(pk)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def refresh(self, request, pk):
        obj = self.get_object()
        BangumiService().update_or_create_subject(obj.id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def refresh_recommendations(self, request, pk):
        obj = self.get_object()
        RemoteRecommendationService().save_recommendations_by_subject(obj)
        return Response(status=status.HTTP_204_NO_CONTENT)
