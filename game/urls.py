from django.urls import path
from . import views

urlpatterns = [
    path('init/', views.init_board, name='init_board'),
    path('moves/', views.get_moves, name='get_moves'),
    path('move/', views.make_move, name='make_move'),
    path('games/<int:pk>/ai-move/', views.AIMoveAPIView.as_view(), name='ai-move')

]
