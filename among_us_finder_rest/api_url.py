from rest_framework import routers

from among_us_finder_rest.apps.users.views import UserViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = router.urls

