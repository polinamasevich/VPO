"""Проверки ожидаемого контракта. expectedFailure фиксирует открытый дефект.
После исправления unexpected success потребует убрать метку.
"""
from unittest import expectedFailure
from django.test import Client
from django.urls import reverse
from main.models import Review
from lab2.tests.helpers import StoreCase


class KnownDefectTests(StoreCase):
    @expectedFailure
    def test_D01_anonymous_review_post_must_not_return_500(self):
        # Arrange
        client = Client(raise_request_exception=False)
        # Act
        response = client.post(reverse('reviews'), {'rating': 5, 'text': 'Хорошая пицца'})
        # Assert: требуется контролируемый отказ.
        self.assertIn(response.status_code, [302, 401, 403])
        self.assertFalse(Review.objects.exists())

    @expectedFailure
    def test_D02_stats_with_category_must_render(self):
        # Arrange
        client = Client(raise_request_exception=False)
        client.force_login(self.staff)
        # Act
        response = client.get(reverse('stats'))
        # Assert
        self.assertEqual(response.status_code, 200)

    @expectedFailure
    def test_D03_invalid_category_must_not_return_500(self):
        # Arrange
        client = Client(raise_request_exception=False)
        # Act
        response = client.get(reverse('item_list'), {'category': 'abc'})
        # Assert: игнорирование фильтра или контролируемая ошибка.
        self.assertIn(response.status_code, [200, 400, 404])

    @expectedFailure
    def test_D04_get_must_not_delete_review(self):
        # Arrange
        review = Review.objects.create(user=self.owner, user_name='owner', rating=5, text='Хорошая пицца')
        self.client.force_login(self.owner)
        # Act
        self.client.get(reverse('delete_review', args=[review.pk]))
        # Assert
        self.assertTrue(Review.objects.filter(pk=review.pk).exists())
