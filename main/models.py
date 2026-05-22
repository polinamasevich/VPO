from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from datetime import date

phone_regex = RegexValidator(regex=r'^\+?375\d{9}$', message="Номер в формате: '+375XXXXXXXXX'")

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    
    def __str__(self): return self.name
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

class PromoCode(models.Model):
    code = models.CharField(max_length=50, verbose_name="Промокод")
    discount = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], verbose_name="Скидка %")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    
    def __str__(self): return self.code
    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"

class ServiceItem(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    description = models.TextField(verbose_name="Описание")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Категория")
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True, verbose_name="Изображение")
    
    def __str__(self): return self.title
    class Meta:
        verbose_name = "Товар/Услуга"
        verbose_name_plural = "Товары/Услуги"

class News(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст новости")
    image = models.ImageField(upload_to='news_images/', blank=True, null=True, verbose_name="Изображение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self): return self.title
    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ['-created_at'] # Сортировка: новые сверху

class Dictionary(models.Model):
    word = models.CharField(max_length=200, verbose_name="Термин")
    definition = models.TextField(verbose_name="Определение")
    date_added = models.DateTimeField(default=timezone.now, verbose_name="Дата добавления")
    
    def __str__(self): return self.word
    class Meta:
        verbose_name = "Условие"
        verbose_name_plural = "Условия сотрудничества"

class Contact(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    position = models.CharField(max_length=100, verbose_name="Должность")
    phone = models.CharField(validators=[phone_regex], max_length=20, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    image = models.ImageField(upload_to='contact_images/', blank=True, null=True, verbose_name="Фото сотрудника")
    
    def __str__(self): return self.name
    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Контакты"

class Vacancy(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    salary = models.CharField(max_length=100, verbose_name="Зарплата")
    
    def __str__(self): return self.title
    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"

class Review(models.Model):
    user_name = models.CharField(max_length=100, verbose_name="Имя клиента")
    birth_date = models.DateField(verbose_name="Дата рождения", default=date(2000, 1, 1))
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Рейтинг (1-5)")
    text = models.TextField(verbose_name="Отзыв")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")
    
    def __str__(self): return self.user_name
    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

class CompanyInfo(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название компании")
    description = models.TextField(verbose_name="Описание")
    image = models.ImageField(upload_to='company_images/', blank=True, null=True, verbose_name="Логотип/Фото")
    
    def __str__(self): return self.name
    class Meta:
        verbose_name = "Информация о компании"
        verbose_name_plural = "Информация о компании"