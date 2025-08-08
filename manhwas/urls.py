from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('detail/<int:pk>/', views.manhwa_detail, name='manhwa_detail'),
    path('detail/<int:pk>/show-replied-comment/', views.show_replied_comment, name='manhwa_comment_replies'),


    path('api/manhwa-list/', views.api_manhwa_list, name='api_manhwa_list'),
    path('api/manhwa-detail/<int:pk>/', views.api_manhwa_detail, name='api_manhwa_detail'),
    path('api/comment-create/', views.api_create_manhwa_comment, name='api_create_manhwa_comment'),
    path('api/manhwa/<int:manhwa_id>/comment/<int:comment_id>', views.api_get_comment_replies, name='api_get_comment_replies'),
    path('api/manhwa-comments/<int:pk>/', views.api_get_manhwa_comments, name='api_get_manhwa_comments'),
    path('api/comment-reaction/', views.api_reaction_handler, name='api_toggle_reaction_comment'),
    path('api/set-view/', views.api_set_user_view_for_manhwa, name='api_set_view_manhwa'),

    path('new/manhwa/<int:manhwa_id>/comments/', views.get_new_comments, name='new_comments'),
    path('new/comment-chiled/<int:pk>', views.api_new_comment_childes, name='new_comment_childes'),
]
