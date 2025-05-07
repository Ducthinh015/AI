from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Tất cả API của game sẽ nằm dưới /api/game/
    path('api/game/', include('game.urls')),
]
