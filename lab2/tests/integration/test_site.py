from decimal import Decimal
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from main.models import Category, ServiceItem, PromoCode, Review, News, CompanyInfo, CompanyHistory, Contact, Dictionary, Vacancy, Partner
from lab2.tests.helpers import StoreCase, checkout_data, registration_data


class SiteIntegrationTests(StoreCase):
    def test_catalog_filters_category(self):
        # Arrange
        url = reverse('item_list')
        # Act
        response = self.client.get(url, {'category': self.category.pk})
        # Assert
        self.assertEqual(list(response.context['items']), [self.pizza])

    def test_catalog_sort_orders(self):
        for mode, expected in [('price_asc', [self.water, self.pizza]), ('price_desc', [self.pizza, self.water]), ('alpha', [self.water, self.pizza])]:
            with self.subTest(mode=mode):
                # Arrange / Act
                response = self.client.get(reverse('item_list'), {'sort': mode})
                # Assert
                self.assertEqual(list(response.context['items']), expected)

    def test_product_detail_and_missing_product(self):
        # Arrange / Act
        response = self.client.get(reverse('item_detail', args=[self.pizza.pk]))
        missing = self.client.get(reverse('item_detail', args=[99999]))
        # Assert
        self.assertContains(response, 'Пицца')
        self.assertEqual(missing.status_code, 404)

    def test_cart_total_from_database_and_sessions_are_isolated(self):
        # Arrange
        other_client = Client()
        self.client.post(reverse('add_to_cart', args=[self.pizza.pk]))
        # Act
        response = self.client.get(reverse('cart'))
        second = other_client.get(reverse('cart'))
        # Assert
        self.assertEqual(response.context['total'], Decimal('18.50'))
        self.assertEqual(response.context['cart_items'][0]['quantity'], 1)
        self.assertEqual(second.context['total'], 0)

    def test_get_cannot_add_to_cart(self):
        # Arrange / Act
        response = self.client.get(reverse('add_to_cart', args=[self.pizza.pk]))
        # Assert
        self.assertRedirects(response, reverse('item_detail', args=[self.pizza.pk]))
        self.assertFalse(self.client.session.get('cart'))

    def test_empty_checkout_redirect(self):
        # Arrange / Act
        response = self.client.get(reverse('checkout'))
        # Assert
        self.assertRedirects(response, reverse('cart'))

    def test_active_promo_calculates_discount_case_insensitively(self):
        # Arrange
        PromoCode.objects.create(code='PIZZA10', discount=10)
        self.client.post(reverse('add_to_cart', args=[self.pizza.pk]))
        # Act
        response = self.client.post(reverse('checkout'), checkout_data(promo_code=' pizza10 '))
        # Assert
        self.assertTemplateUsed(response, 'main/checkout_success.html')
        self.assertEqual(response.context['discount'], Decimal('1.85'))
        self.assertEqual(response.context['final_total'], Decimal('16.65'))
        self.assertEqual(self.client.session['cart'], {})

    def test_invalid_promos_preserve_cart(self):
        # Arrange
        PromoCode.objects.create(code='OLD', discount=50, is_active=False)
        self.client.post(reverse('add_to_cart', args=[self.pizza.pk]))
        for code in ['OLD', 'MISSING']:
            with self.subTest(code=code):
                # Act
                response = self.client.post(reverse('checkout'), checkout_data(promo_code=code))
                # Assert
                self.assertIn('promo_code', response.context['form'].errors)
                self.assertEqual(self.client.session['cart'], {str(self.pizza.pk): 1})

    def test_registration_persists_user_and_creates_session(self):
        # Arrange
        data = registration_data()
        # Act
        response = self.client.post(reverse('register'), data)
        # Assert
        self.assertRedirects(response, reverse('index'))
        user = User.objects.get(username='anna')
        self.assertTrue(user.check_password(data['password']))
        self.assertEqual(self.client.session['_auth_user_id'], str(user.pk))

    def test_registration_rejects_duplicate_username(self):
        # Arrange
        data = registration_data(username='owner')
        # Act
        response = self.client.post(reverse('register'), data)
        # Assert
        self.assertIn('username', response.context['form'].errors)
        self.assertEqual(User.objects.filter(username='owner').count(), 1)

    def test_login_success_failure_and_logout(self):
        # Arrange / Act
        failed = self.client.post(reverse('login'), {'username': 'owner', 'password': 'wrong'})
        # Assert
        self.assertTrue(failed.context['form'].errors)
        # Act
        success = self.client.post(reverse('login'), {'username': 'owner', 'password': 'secret'})
        # Assert
        self.assertRedirects(success, reverse('index'))
        self.assertRedirects(self.client.get(reverse('login')), reverse('index'))
        # Act
        self.client.post(reverse('logout'))
        # Assert
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_statistics_guest_and_regular_user_cannot_access(self):
        # Arrange / Act / Assert
        self.assertRedirects(self.client.get(reverse('stats')), reverse('index'))
        self.client.force_login(self.owner)
        self.assertRedirects(self.client.get(reverse('stats')), reverse('index'))

    def test_statistics_with_no_products(self):
        # Arrange: пустой каталог — отдельный допустимый случай.
        ServiceItem.objects.all().delete()
        self.client.force_login(self.staff)
        # Act
        response = self.client.get(reverse('stats'))
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_services'], 0)
        self.assertIsNone(response.context['chart_base64'])

    def test_statistics_for_products_without_categories(self):
        # Arrange: у товаров категория необязательна. Дефект с категорией проверяется отдельно.
        ServiceItem.objects.update(category=None)
        self.client.force_login(self.staff)
        # Act
        response = self.client.get(reverse('stats'))
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['chart_base64'].startswith('iVBOR'))

    def test_csrf_rejects_post_without_token(self):
        # Arrange
        client = Client(enforce_csrf_checks=True)
        # Act
        response = client.post(reverse('add_to_cart', args=[self.pizza.pk]))
        # Assert
        self.assertEqual(response.status_code, 403)
        self.assertFalse(client.session.get('cart'))

    def test_deleting_category_preserves_product(self):
        # Arrange / Act
        self.category.delete()
        self.pizza.refresh_from_db()
        # Assert
        self.assertIsNone(self.pizza.category_id)
        self.assertTrue(ServiceItem.objects.filter(pk=self.pizza.pk).exists())

    def test_model_labels(self):
        # Arrange
        samples = [(self.category, 'Пицца'), (self.pizza, 'Пицца'), (PromoCode(code='X'), 'X'),
                   (Partner(name='P'), 'P'), (News(title='N'), 'N'), (Dictionary(word='D'), 'D'),
                   (Contact(name='C'), 'C'), (Vacancy(title='V'), 'V'), (Review(user_name='R'), 'R'),
                   (CompanyInfo(name='I'), 'I'), (CompanyHistory(year=2020, title='Открытие'), '2020 — Открытие')]
        for obj, expected in samples:
            with self.subTest(model=type(obj).__name__):
                # Act / Assert
                self.assertEqual(str(obj), expected)

    def test_admin_creates_category(self):
        # Arrange: сотрудник с полными административными правами.
        self.staff.is_superuser = True
        self.staff.save(update_fields=['is_superuser'])
        self.client.force_login(self.staff)
        # Act
        response = self.client.post(reverse('admin:main_category_add'), {'name': 'Новая категория', '_save': 'Save'})
        # Assert
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Category.objects.filter(name='Новая категория').exists())


class PagesIntegrationTests(TestCase):
    def test_information_pages_display_database_content(self):
        # Arrange
        company = CompanyInfo.objects.create(name='Тестовая компания', description='Описание')
        CompanyHistory.objects.create(year=2020, title='История', description='Начало')
        Contact.objects.create(name='Сотрудник', position='Менеджер', phone='+375291234567', email='a@example.com')
        Vacancy.objects.create(title='Тестовая вакансия', description='Описание', salary='1000')
        Dictionary.objects.create(word='Тестовый термин', definition='Определение')
        PromoCode.objects.create(code='TESTCODE', discount=10)
        Partner.objects.create(name='Тестовый партнёр', website='https://partner.example/')
        news = News.objects.create(title='Тестовая новость', text='Текст', short_text='Кратко')
        for route, text in [('index', news.title), ('about', company.name), ('contacts', 'Сотрудник'),
                            ('vacancies', 'Тестовая вакансия'), ('dictionary', 'Тестовый термин'),
                            ('promocodes', 'TESTCODE'), ('news_list', news.title)]:
            with self.subTest(route=route):
                # Act
                response = self.client.get(reverse(route))
                # Assert
                self.assertContains(response, text)
        self.assertContains(self.client.get(reverse('news_detail', args=[news.pk])), news.title)

    def test_static_and_auth_pages_render(self):
        for route in ['terms', 'privacy', 'register', 'login', 'reviews']:
            with self.subTest(route=route):
                # Arrange / Act
                response = self.client.get(reverse(route))
                # Assert
                self.assertEqual(response.status_code, 200)

    def test_news_limit_and_order(self):
        # Arrange
        News.objects.all().delete()
        for i in range(9):
            News.objects.create(title=str(i), text='Текст', short_text='Кратко')
        # Act
        response = self.client.get(reverse('news_list'))
        # Assert
        self.assertEqual([n.title for n in response.context['news']], ['8', '7', '6', '5', '4', '3', '2'])
        self.assertEqual(self.client.get(reverse('news_detail', args=[99999])).status_code, 404)
