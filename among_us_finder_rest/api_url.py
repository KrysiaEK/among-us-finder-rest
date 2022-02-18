from rest_framework import routers

from among_us_finder_rest.apps.users.views import UserViewSet
from among_us_finder_rest.apps.rooms.views import RoomViewSet, MessageViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'message', MessageViewSet)

urlpatterns = router.urls
