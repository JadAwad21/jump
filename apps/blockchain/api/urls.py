from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'blockchain'

router = DefaultRouter()
router.register('investigations', views.InvestigationViewSet, basename='investigation')
router.register('acquisition-events', views.AcquisitionEventViewSet, basename='acquisition-event')
router.register('evidence', views.EvidenceViewSet, basename='evidence')
router.register('tags', views.TagViewSet, basename='tag')
router.register('guid-resolver', views.GUIDResolverViewSet, basename='guid-resolver')

urlpatterns = [
    path('', include(router.urls)),
]

from .user_info import user_with_roles
urlpatterns.append(path('user-info/', user_with_roles, name='user-info'))
