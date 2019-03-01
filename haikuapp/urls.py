from django.contrib import admin
from django.urls import path
from django.views.static import serve
from haiku import settings
from haikuapp import views

urlpatterns = [
    path(r'', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path(r'activation/', views.activation, name='activation'),

    path(r'media/<str:path>', serve, {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    path(r'media/category/<str:path>', serve,
         {'document_root': settings.MEDIA_ROOT + '/category', 'show_indexes': True}),
    path(r'media/template/<str:path>', serve,
         {'document_root': settings.MEDIA_ROOT + '/template', 'show_indexes': True}),
    path(r'media/images/<str:path>', serve,
         {'document_root': settings.MEDIA_ROOT + '/images', 'show_indexes': True}),

    path(r'wizard/', views.wizard, name='wizard'),
    path(r'category/', views.category, name='category'),
    path(r'category/<int:category_id>/templates/', views.templates, name='templates'),
    path(r'create/<int:template_id>/', views.create_card, name='create_card'),
    path(r'cards/', views.cards, name='cards'),
    path(r'card/<int:card_id>', views.card, name='card'),
    path(r'card/<int:card_id>/delete/', views.card_delete, name='card_delete'),
]
