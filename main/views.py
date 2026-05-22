from django.shortcuts import render, redirect
from django.db.models import Avg
from .models import ServiceItem, News, Dictionary, Contact, Vacancy, Review, PromoCode, CompanyInfo, Category
from .forms import ReviewForm

def index(request):
    # Получаем самую свежую новость для главной страницы
    last_news = News.objects.order_by('-created_at').first()
    return render(request, 'main/index.html', {'last_news': last_news})

def item_list(request):
    category_id = request.GET.get('category')
    sort_by = request.GET.get('sort')
    categories = Category.objects.all()
    
    items = ServiceItem.objects.all()
    
    # Фильтрация по категории
    if category_id:
        items = items.filter(category_id=category_id)
        
    # Сортировка каталога товаров/услуг
    if sort_by == 'price_asc':
        items = items.order_by('price')
    elif sort_by == 'price_desc':
        items = items.order_by('-price')
    elif sort_by == 'alpha':
        items = items.order_by('title')
        
    return render(request, 'main/item_list.html', {
        'items': items, 
        'categories': categories,
        'active_category': int(category_id) if category_id else None,
        'active_sort': sort_by
    })

def reviews(request):
    # Логика отправки отзыва через форму
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

def news_list(request):
    # Выводим все новости, новые будут сверху (благодаря -created_at)
    return render(request, 'main/news_list.html', {'news': News.objects.order_by('-created_at')})

def about(request):
    return render(request, 'main/about.html', {'company_info': CompanyInfo.objects.first()})

def contacts(request):
    return render(request, 'main/contacts.html', {'employees': Contact.objects.all()})

def promocodes(request):
    return render(request, 'main/promocodes.html', {'promocodes': PromoCode.objects.all()})

def vacancies(request):
    return render(request, 'main/vacancies.html', {'vacancies': Vacancy.objects.all()})

def dictionary(request):
    return render(request, 'main/dictionary.html', {'words': Dictionary.objects.order_by('word')})

def terms(request):
    return render(request, 'main/terms.html')

def privacy(request):
    return render(request, 'main/privacy.html')

def stats(request):
    # Считаем количество записей в каждой таблице для аналитики
    total_services = ServiceItem.objects.count()
    total_news = News.objects.count()
    total_reviews = Review.objects.count()
    
    # Считаем средний рейтинг среди всех отзывов
    avg_rating = Review.objects.aggregate(Avg('rating'))['rating__avg']
    if avg_rating:
        avg_rating = round(avg_rating, 1)  # Округляем до одного знака, например 4.5
    else:
        avg_rating = "Нет оценок"

    context = {
        'total_services': total_services,
        'total_news': total_news,
        'total_reviews': total_reviews,
        'avg_rating': avg_rating,
    }
    return render(request, 'main/stats.html', context)