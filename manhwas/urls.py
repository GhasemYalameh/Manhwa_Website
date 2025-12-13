from django.urls import path, include
from . import views
from rest_framework_nested import routers

router = routers.SimpleRouter()
router.register('manhwas', views.ManhwaViewSet, basename='manhwa')  # list & retrieve (manhwa-list, manhwa-detail)

manhwa_router = routers.NestedSimpleRouter(router, 'manhwas', lookup='manhwa')
manhwa_router.register('comments', views.CommentViewSet, basename='manhwa-comments')
manhwa_router.register('episodes', views.EpisodeViewSet, basename='manhwa-episodes')

router2 = routers.SimpleRouter()
router2.register('tickets', views.TicketViewSet, basename='ticket')

ticket_router = routers.NestedSimpleRouter(router2, 'tickets', lookup='ticket')
ticket_router.register('messages', views.TicketMessageViewSet, basename='ticket-messages')

urlpatterns = [
    path('', views.home_page, name='home'),
    path('healthy/', views.health_check, name='health-check'),
    path('detail/<int:pk>/', views.manhwa_detail, name='manhwa_detail'),
    path('detail/<int:manhwa_id>/show-replied-comment/<int:comment_id>/', views.show_replied_comment, name='manhwa_comment_replies'),

    # path('api/tickets/', views.TicketApiView.as_view(), name='tickets'),
    # path('api/tickets/<int:pk>/', views.TicketMessagesApiView.as_view(), name='ticket-messages'),

    path('api/', include(router.urls)),
    path('api/', include(manhwa_router.urls)),
    path('api/', include(router2.urls)),
    path('api/', include(ticket_router.urls)),
]
