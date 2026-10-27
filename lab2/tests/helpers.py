from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from main.models import Category, ServiceItem


def checkout_data(**changes):
    data = dict(full_name='Анна', phone='+375291234567', email='anna@example.com',
                fulfillment_method='pickup', address='', payment_method='cash',
                promo_code='', comment='', agree='on')
    return dict(data, **changes)


def registration_data(**changes):
    return dict(dict(username='anna', phone_number='+375(29)1234567',
                     birth_date='2000-01-01', password='Strong-password-123'), **changes)


class StoreCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name='Пицца')
        cls.pizza = ServiceItem.objects.create(title='Пицца', price=Decimal('18.50'),
                                              description='С сыром', category=cls.category)
        cls.water = ServiceItem.objects.create(title='Вода', price=Decimal('2.00'), description='Вода')
        cls.owner = User.objects.create_user('owner', password='secret')
        cls.other = User.objects.create_user('other', password='secret')
        cls.staff = User.objects.create_user('staff', password='secret', is_staff=True)
