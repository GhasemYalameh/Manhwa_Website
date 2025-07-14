from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('detail/<int:pk>/', views.manhwa_detail, name='manhwa_detail'),
    path('manhwa/<int:pk>/add-comment/', views.add_comment_manhwa, name='add_comment_manhwa'),
    path('comment-reaction/<int:pk>/', views.change_or_create_reaction, name='set_reaction'),
]
