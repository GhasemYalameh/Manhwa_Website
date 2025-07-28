from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('detail/<int:pk>/', views.manhwa_detail, name='manhwa_detail'),
    path('detail/<int:pk>/set-view/', views.set_user_view_for_manhwa, name='set_user_view_for_manhwa'),
    path('detail/<int:pk>/show-replied-comment/', views.show_replied_comment, name='manhwa_comment_replies'),
    path('manhwa/<int:pk>/add-comment/', views.add_comment_manhwa, name='add_comment_manhwa'),
    path('comment-reaction/<int:pk>/', views.change_or_create_reaction, name='set_reaction'),


    path('api/manhwa-list/', views.api_manhwa_list, name='api_manhwa_list'),
    path('api/manhwa-detail/<int:pk>/', views.api_manhwa_detail, name='api_manhwa_detail'),
    path('api/comment-create/', views.api_create_comment_manhwa, name='api_create_comment_manhwa'),

]
