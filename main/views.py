import random
import statistics
from django.shortcuts import render, redirect
from django.db.models import Avg
from django.utils import timezone  # Импортируем для работы с временем
from django.contrib.auth import login  # Импортируем для автоматической авторизации
from .models import ServiceItem, News, Dictionary, Contact, Vacancy, Review, PromoCode, CompanyInfo, Category
from .forms import ReviewForm, ExtendedRegistrationForm  # Подключаем новую форму регистрации

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


# --- ПОЛНОСТЬЮ ЗАПОЛНЕННАЯ АНАЛИТИКА НА РЕАЛЬНЫХ ТОВАРАХ ---
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

    # Получаем список твоих реальных товаров
    items_alphabetical = ServiceItem.objects.order_by('title')
    db_items = list(items_alphabetical)
    
    if db_items:
        random.seed(42)  # Фиксируем сид, чтобы данные не менялись при перезагрузке
        
        # 1. Симулируем 25 заказов на базе цен твоих пицц/услуг
        db_prices = [float(item.price) for item in db_items]
        simulated_orders = [random.choice(db_prices) for _ in range(22)]
        # Добавляем принудительно несколько одинаковых цен, чтобы мода гарантированно высчиталась
        simulated_orders.extend([db_prices[0], db_prices[0], db_prices[0]])
        
        # Расчет первой карточки (Экономические показатели)
        total_sales_sum = round(sum(simulated_orders), 2)
        sales_avg = round(statistics.mean(simulated_orders), 2)
        sales_median = round(statistics.median(simulated_orders), 2)
        sales_mode = round(statistics.mode(simulated_orders), 2)
        
        # 2. Симулируем возраст покупателей для второй карточки
        simulated_ages = [random.randint(19, 45) for _ in range(30)]
        age_avg = round(statistics.mean(simulated_ages), 1)
        age_median = int(statistics.median(simulated_ages))
        
        # 3. Ищем популярный тип товара (по твоим реальным категориям)
        categories_list = [item.category.title for item in db_items if item.category]
        if categories_list:
            popular_type = max(set(categories_list), key=categories_list.count)
            profitable_type = popular_type
        else:
            popular_type = "Пицца"
            profitable_type = "Пицца"
    else:
        # Защита на случай, если база пустая
        total_sales_sum = sales_avg = sales_median = sales_mode = 0
        age_avg = age_median = 0
        popular_type = "Нет товаров"
        profitable_type = "Нет товаров"

    context = {
        'total_services': total_services,
        'total_news': total_news,
        'total_reviews': total_reviews,
        'avg_rating': avg_rating,
        
        'items_alphabetical': items_alphabetical,  # Наполнит нижнюю таблицу
        
        # Для карточки экономических показателей:
        'total_sales_sum': total_sales_sum,
        'sales_avg': sales_avg,
        'sales_median': sales_median,
        'sales_mode': sales_mode,
        
        # Для карточки возраста клиентов:
        'age_avg': age_avg,
        'age_median': age_median,
        'popular_type': popular_type,
        'profitable_type': profitable_type,
    }
    return render(request, 'main/stats.html', context)


# Остальные страницы
def news_list(request): return render(request, 'main/news_list.html', {'news': News.objects.order_by('-created_at')})
def about(request): return render(request, 'main/about.html', {'company_info': CompanyInfo.objects.first()})
def contacts(request): return render(request, 'main/contacts.html', {'employees': Contact.objects.all()})
def promocodes(request): return render(request, 'main/promocodes.html', {'promocodes': PromoCode.objects.all()})
def vacancies(request): return render(request, 'main/vacancies.html', {'vacancies': Vacancy.objects.all()})
def dictionary(request): return render(request, 'main/dictionary.html', {'words': Dictionary.objects.order_by('word')})
def terms(request): return render(request, 'main/terms.html')
def privacy(request): return render(request, 'main/privacy.html')