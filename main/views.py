import random
import statistics
import io
import base64
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Avg
from django.utils import timezone  # Импортируем для работы с временем
from django.contrib.auth import login  # Импортируем для автоматической авторизации
from .models import ServiceItem, News, Dictionary, Contact, Vacancy, Review, PromoCode, CompanyInfo, Category
from .forms import ReviewForm, ExtendedRegistrationForm  # Подключаем новую форму регистрации

# Настройка Matplotlib для работы на сервере в фоновом режиме (без графического интерфейса)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def index(request):
    last_news = News.objects.order_by('-created_at').first()
    now_local = timezone.localtime(timezone.now())
    
    context = {
        'last_news': last_news,
        'server_time': now_local.strftime('%d/%m/%Y %H:%M:%S'),
        'utc_time': timezone.now().strftime('%d/%m/%Y %H:%M:%S'),
    }
    return render(request, 'main/index.html', context)


def register(request):
    if request.method == 'POST':
        form = ExtendedRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Сохраняем пользователя в базу (пароль захешируется)
            login(request, user)  # Сразу авторизуем его в системе
            return redirect('index')  # Перенаправляем на главную страницу
    else:
        form = ExtendedRegistrationForm()
    
    return render(request, 'main/register.html', {'form': form})


def item_list(request):
    category_id = request.GET.get('category')
    sort_by = request.GET.get('sort')
    categories = Category.objects.all()
    
    items = ServiceItem.objects.all()
    
    if category_id:
        items = items.filter(category_id=category_id)
        
    if sort_by == 'price_asc':
        items = items.order_by('price')
    elif sort_by == 'price_desc':
        items = items.order_by('-price')
    elif sort_by == 'alpha' or not sort_by:
        items = items.order_by('title')
        
    return render(request, 'main/item_list.html', {
        'items': items, 
        'categories': categories,
        'active_category': int(category_id) if category_id else None,
        'active_sort': sort_by
    })


# --- РАБОТА С ОТЗЫВАМИ (ПРОСМОТР И ДОБАВЛЕНИЕ) ---
def reviews(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid(): 
            form.save()
            return redirect('reviews')
    else: 
        form = ReviewForm()
        
    return render(request, 'main/reviews.html', {
        'reviews': Review.objects.order_by('-date_created'), 
        'form': form
    })


# --- РЕДАКТИРОВАНИЕ ОТЗЫВА С ФРОНТА ---
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    # Проверка прав: редактирует админ или автор (если у модели есть связь с user)
    if not request.user.is_staff and getattr(review, 'user', None) != request.user:
        return redirect('reviews')

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('reviews')
    else:
        form = ReviewForm(instance=review)
        
    return render(request, 'main/edit_review.html', {
        'form': form,
        'review': review
    })


# --- УДАЛЕНИЕ ОТЗЫВА С ФРОНТА ---
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    # Проверка прав на удаление
    if request.user.is_staff or getattr(review, 'user', None) == request.user:
        review.delete()
        
    return redirect('reviews')


# --- АНАЛИТИКА НА РЕАЛЬНЫХ ТОВАРАХ + СЕРВЕРНЫЙ ГРАФИК MATPLOTLIB ---
def stats(request):
    # Ограничение доступа: только для админов
    if not request.user.is_staff:
        return redirect('index')

    # Сбор базовых данных
    total_services = ServiceItem.objects.count()
    total_news = News.objects.count()
    total_reviews = Review.objects.count()
    
    avg_rating = Review.objects.aggregate(Avg('rating'))['rating__avg']
    avg_rating = round(avg_rating, 1) if avg_rating else 0

    # Получаем список реальных товаров
    items_alphabetical = ServiceItem.objects.order_by('title')
    db_items = list(items_alphabetical)
    
    chart_base64 = None  # Сюда запишем готовую картинку графика

    if db_items:
        random.seed(42)  # Фиксируем сид для воспроизводимости симуляции
        
        # 1. Симулируем 25 заказов на базе цен товаров
        db_prices = [float(item.price) for item in db_items]
        simulated_orders = [random.choice(db_prices) for _ in range(22)]
        simulated_orders.extend([db_prices[0], db_prices[0], db_prices[0]])
        
        # Расчет экономических показателей
        total_sales_sum = round(sum(simulated_orders), 2)
        sales_avg = round(statistics.mean(simulated_orders), 2)
        sales_median = round(statistics.median(simulated_orders), 2)
        sales_mode = round(statistics.mode(simulated_orders), 2)
        
        # 2. Симулируем возраст покупателей (генерируется случайно, от базы отзывов не зависит)
        simulated_ages = [random.randint(19, 45) for _ in range(30)]
        age_avg = round(statistics.mean(simulated_ages), 1)
        age_median = int(statistics.median(simulated_ages))
        
        # 3. Популярный тип товара по категориям
        categories_list = [item.category.title for item in db_items if item.category]
        if categories_list:
            popular_type = max(set(categories_list), key=categories_list.count)
            profitable_type = popular_type
        else:
            popular_type = "Пицца"
            profitable_type = "Пицца"

        # --- ОТРИСОВКА ГРАФИКА ЧЕРЕЗ MATPLOTLIB ---
        plt.figure(figsize=(10, 5))
        titles = [item.title for item in db_items]
        prices = [float(item.price) for item in db_items]
        
        plt.bar(titles, prices, color='#1890ff', edgecolor='#0050b3', alpha=0.8)
        plt.title('Столбчатая диаграмма цен ассортимента', fontsize=14, fontweight='bold', pad=15)
        plt.ylabel('Цена (BYN)', fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        plt.xticks(rotation=30, ha='right', fontsize=10)
        plt.tight_layout()

        # Сохранение графика в виртуальный буфер памяти без сохранения на диск
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        chart_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        plt.close()  # Очищаем память после генерации рисунка

    else:
        total_sales_sum = sales_avg = sales_median = sales_mode = 0
        age_avg = age_median = 0
        popular_type = "Нет товаров"
        profitable_type = "Нет товаров"

    context = {
        'total_services': total_services,
        'total_news': total_news,
        'total_reviews': total_reviews,
        'avg_rating': avg_rating,
        'items_alphabetical': items_alphabetical,
        'total_sales_sum': total_sales_sum,
        'sales_avg': sales_avg,
        'sales_median': sales_median,
        'sales_mode': sales_mode,
        'age_avg': age_avg,
        'age_median': age_median,
        'popular_type': popular_type,
        'profitable_type': profitable_type,
        'chart_base64': chart_base64,  # Передаем картинку в шаблон
    }
    return render(request, 'main/stats.html', context)


# Остальные вспомогательные страницы сайта
def news_list(request): return render(request, 'main/news_list.html', {'news': News.objects.order_by('-created_at')})
def about(request): return render(request, 'main/about.html', {'company_info': CompanyInfo.objects.first()})
def contacts(request): return render(request, 'main/contacts.html', {'employees': Contact.objects.all()})
def promocodes(request): return render(request, 'main/promocodes.html', {'promocodes': PromoCode.objects.all()})
def vacancies(request): return render(request, 'main/vacancies.html', {'vacancies': Vacancy.objects.all()})
def dictionary(request): return render(request, 'main/dictionary.html', {'words': Dictionary.objects.order_by('word')})
def terms(request): return render(request, 'main/terms.html')
def privacy(request): return render(request, 'main/privacy.html')