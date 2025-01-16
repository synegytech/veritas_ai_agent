from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ModelInputViewSet, ModelOutputViewSet

router = DefaultRouter()
router.register(r"inputs", ModelInputViewSet)
router.register(r"outputs", ModelOutputViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
