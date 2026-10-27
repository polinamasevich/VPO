from django.contrib import admin 
from .models import Category, ServiceItem, News, Dictionary, Contact, Vacancy, Review, PromoCode, CompanyInfo, Partner, CompanyHistory
 
# 1. Настройка для PromoCode 
@admin.register(PromoCode) 
class PromoCodeAdmin(admin.ModelAdmin): 
    list_display = ('code', 'discount', 'description') 
    list_editable = ('discount', 'description') 
 
# 2. Настройка для Dictionary (твой Словарь/Условия) 
@admin.register(Dictionary) 
class DictionaryAdmin(admin.ModelAdmin): 
    list_display = ('word', 'definition') 
    search_fields = ('word',) # Добавим поиск по терминам для удобства 
 
# 3. Регистрация остальных моделей 
admin.site.register(Category) 
admin.site.register(ServiceItem) 
admin.site.register(News) 
admin.site.register(Contact) 
admin.site.register(Vacancy) 
admin.site.register(Review) 
admin.site.register(CompanyInfo) 
admin.site.register(Partner)
admin.site.register(CompanyHistory)