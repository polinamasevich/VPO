from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Category, ServiceItem, PromoCode


class StorefrontTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name='Пицца')
        self.item = ServiceItem.objects.create(title='Маргарита', price=Decimal('18.50'), description='Классическая пицца', category=category)

    def test_item_can_be_added_and_updated_in_cart(self):
        self.client.post(reverse('add_to_cart', args=[self.item.id]))
        response = self.client.get(reverse('cart'))
        self.assertContains(response, 'Маргарита')
        self.client.post(reverse('update_cart', args=[self.item.id]), {'action': 'increase'})
        self.assertEqual(self.client.session['cart'][str(self.item.id)], 2)

    def test_detail_and_news_routes_are_available(self):
        self.assertEqual(self.client.get(reverse('item_detail', args=[self.item.id])).status_code, 200)
        self.assertEqual(self.client.get(reverse('news_list')).status_code, 200)

    def test_login_page_is_available(self):
        self.assertEqual(self.client.get(reverse('login')).status_code, 200)

    def test_review_uses_authenticated_username(self):
        User.objects.create_user(username='guest', password='safe-password-123')
        self.client.login(username='guest', password='safe-password-123')
        response = self.client.post(reverse('reviews'), {'rating': 5, 'text': 'Очень вкусная пицца!'}, follow=True)
        self.assertContains(response, 'guest')

    def test_checkout_applies_active_promo_code(self):
        PromoCode.objects.create(code='PIZZA10', discount=10, description='Тестовая скидка')
        self.client.post(reverse('add_to_cart', args=[self.item.id]))
        response = self.client.post(reverse('checkout'), {
            'full_name': 'Гость', 'phone': '+375291234567', 'fulfillment_method': 'pickup',
            'address': '', 'payment_method': 'card', 'promo_code': 'PIZZA10', 'comment': '',
        })
        self.assertContains(response, 'PIZZA10')
        self.assertContains(response, '16,65')
