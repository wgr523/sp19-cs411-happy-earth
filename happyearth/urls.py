from django.urls import path
from django.urls import path, include # new
from django.views.generic.base import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
        path('', views.user_home, name='homepage'),
        path('favorites/', views.user_favorites, name='user favorites'),
        path('favorites/<tag>/', views.user_favorites_tag, name='user favorites tag'),
        path('favorites/<tag>/remove/<rid>/', views.user_favorites_remove, name='user favorites remove'),
        path('restaurant/<rid>/', views.restaurant_id, name='restaurant'),
        path('restaurant/<rid>/comment/', views.restaurant_id_comment, name='restaurant comment'),
        path('restaurant/<rid>/edit/', views.restaurant_id_edit, name='restaurant comment edit'),
        path('restaurant/<rid>/edit/<cid>/', views.restaurant_id_edit_comment, name='restaurant edit comment'),
        path('restaurant/<rid>/edit/delete/<cid>/', views.restaurant_id_delete_comment, name='restaurant delete comment'),
        path('restaurant/<rid>/favorite/', views.restaurant_id_favorite, name='add restaurant to favorite'),
        path('search/', views.search_result, name='search result'),
        path('together/', views.user_together, name='eat together'),
        path('together/delete/', views.user_together_delete, name='eat together delete'),
        path('user/edit/', views.edit_user, name='edit user'),
        path('user/clear/', views.clear_user, name='clear user'),
        path('clear-recommend/', views.clear_recommend, name='clear recommend'),
        ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
