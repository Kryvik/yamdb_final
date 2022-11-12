from rest_framework import mixins, viewsets


class AuthViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    pass


class GetPostDelViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                        mixins.DestroyModelMixin, viewsets.GenericViewSet):
    pass
