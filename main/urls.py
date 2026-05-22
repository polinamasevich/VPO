from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import ReviewForm

urlpatterns = [
    path('', views.index, name='index'),
    path('news/', views.news_list, name='news_list'),
    path('items/', views.item_list, name='item_list'),
    path('reviews/', views.reviews, name='reviews'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('promocodes/', views.promocodes, name='promocodes'),
    path('vacancies/', views.vacancies, name='vacancies'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    path('dictionary/', views.dictionary, name='dictionary'),
    
    # Пути для панели управления внизу страницы
    path('stats/', views.stats, name='stats'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'), # ВОТ ЭТО ИСПРАВИТ ОШИБКУ LOGOUT!
]