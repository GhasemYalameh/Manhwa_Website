from django.urls import path, include
from . import views
from rest_framework_nested import routers

router = routers.SimpleRouter()
router.register('manhwas', views.ManhwaViewSet, basename='manhwa')  # list & retrieve (manhwa-list, manhwa-detail)

manhwa_router = routers.NestedSimpleRouter(router, 'manhwas', lookup='manhwa')
manhwa_router.register('comments', views.CommentViewSet, basename='manhwa-comments')
manhwa_router.register('episodes', views.EpisodeViewSet, basename='manhwa-episodes')

urlpatterns = [
    path('', views.home_page, name='home'),
    path('detail/<int:pk>/', views.manhwa_detail, name='manhwa_detail'),
    path('detail/<int:manhwa_id>/show-replied-comment/<int:comment_id>/', views.show_replied_comment, name='manhwa_comment_replies'),

    path('api/comment-reaction/', views.api_reaction_handler, name='api_toggle_reaction_comment'),
    path('api/tickets/', views.TicketApiView.as_view(), name='tickets'),

    path('api/', include(router.urls + manhwa_router.urls)),
]
