from django.urls import path, include
from . import views
from rest_framework_nested import routers

router = routers.SimpleRouter()
router.register('manhwas', views.ManhwaViewSet, basename='manhwa')  # list & retrieve (manhwa-list, manhwa-detail)

manhwa_router = routers.NestedSimpleRouter(router, 'manhwas', lookup='manhwa')
manhwa_router.register('comments', views.CommentViewSet, basename='manhwa-comments')


urlpatterns = [
    path('', views.home_page, name='home'),
    path('detail/<int:pk>/', views.manhwa_detail, name='manhwa_detail'),
    path('detail/<int:pk>/show-replied-comment/', views.show_replied_comment, name='manhwa_comment_replies'),

    path('api/comment-reaction/', views.api_reaction_handler, name='api_toggle_reaction_comment'),
    path('api/set-view/', views.api_set_user_view_for_manhwa, name='api_set_view_manhwa'),

    path('api/', include(router.urls + manhwa_router.urls)),
]
