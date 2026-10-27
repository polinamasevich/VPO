from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.user_login, name='login'),
    path('news/', views.news_list, name='news_list'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),
    path('items/', views.item_list, name='item_list'),
    path('items/<int:item_id>/', views.item_detail, name='item_detail'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    
    # Пути для работы с отзывами (Просмотр, Редактирование, Удаление)
    path('reviews/', views.reviews, name='reviews'),
    path('reviews/edit/<int:review_id>/', views.edit_review, name='edit_review'),
    path('reviews/delete/<int:review_id>/', views.delete_review, name='delete_review'),
    
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('promocodes/', views.promocodes, name='promocodes'),
    path('vacancies/', views.vacancies, name='vacancies'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    path('dictionary/', views.dictionary, name='dictionary'),
    
    # --- СТРОКА ДЛЯ РЕГИСТРАЦИИ (18+) ---
    path('register/', views.register, name='register'),
    
    # Пути для панели управления и выхода из системы
    path('stats/', views.stats, name='stats'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'), 
]
