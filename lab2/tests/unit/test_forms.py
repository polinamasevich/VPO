from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch
from django.test import SimpleTestCase
from django.core.exceptions import ValidationError
from main.forms import CheckoutForm, ReviewForm, ExtendedRegistrationForm
from main.context_processors import cart_total
from main.models import phone_regex
from lab2.tests.helpers import checkout_data, registration_data


class FormsUnitTests(SimpleTestCase):
    def test_checkout_delivery_and_pickup(self):
        # Arrange: разные условия получения одного заказа.
        for method, address, valid in [('pickup', '', True), ('delivery', '', False), ('delivery', 'Минск', True)]:
            with self.subTest(method=method, address=address):
                form = CheckoutForm(checkout_data(fulfillment_method=method, address=address))
                # Act
                result = form.is_valid()
                # Assert
                self.assertEqual(result, valid)
                if not valid:
                    self.assertIn('address', form.errors)

    def test_checkout_invalid_fields(self):
        for field, value in [('agree', ''), ('email', 'wrong'), ('phone', ''),
                             ('full_name', ''), ('full_name', 'a' * 101),
                             ('payment_method', 'crypto'), ('fulfillment_method', 'unknown')]:
            with self.subTest(field=field):
                # Arrange
                form = CheckoutForm(checkout_data(**{field: value}))
                # Act
                valid = form.is_valid()
                # Assert
                self.assertFalse(valid)
                self.assertIn(field, form.errors)

    def test_review_text_boundary(self):
        for text, valid in [('', False), ('1234', False), ('12345', True), ('123456', True)]:
            with self.subTest(text=text):
                # Arrange
                form = ReviewForm({'rating': 5, 'text': text})
                # Act
                result = form.is_valid()
                # Assert
                self.assertEqual(result, valid)

    def test_review_rating_boundaries(self):
        for rating, valid in [(0, False), (1, True), (5, True), (6, False), ('abc', False)]:
            with self.subTest(rating=rating):
                # Arrange
                form = ReviewForm({'rating': rating, 'text': 'Вкусная пицца'})
                # Act
                result = form.is_valid()
                # Assert
                self.assertEqual(result, valid)

    @patch('main.forms.User.validate_unique')
    def test_registration_age_boundary_with_mocked_clock(self, unique):
        # Arrange: фиксированная дата и подмена проверки уникальности (нет БД).
        for birthday, valid in [('2008-10-27', True), ('2008-10-28', False), ('2030-01-01', False)]:
            with self.subTest(birthday=birthday), patch('main.forms.date') as clock:
                clock.today.return_value = date(2026, 10, 27)
                form = ExtendedRegistrationForm(registration_data(birth_date=birthday))
                # Act
                result = form.is_valid()
                # Assert
                self.assertEqual(result, valid)
                if not valid:
                    self.assertIn('birth_date', form.errors)
        self.assertTrue(unique.called)

    @patch('main.forms.User.validate_unique')
    def test_registration_phone_format(self, unique):
        for phone, valid in [('+375(29)1234567', True), ('+375291234567', False), ('', False)]:
            with self.subTest(phone=phone):
                # Arrange
                form = ExtendedRegistrationForm(registration_data(phone_number=phone))
                # Act
                result = form.is_valid()
                # Assert
                self.assertEqual(result, valid)

    @patch('main.forms.User.validate_unique')
    def test_password_hash_and_commit_behavior_with_mocked_repository(self, unique):
        for commit in [False, True]:
            with self.subTest(commit=commit), patch('main.forms.User.save') as save:
                # Arrange
                form = ExtendedRegistrationForm(registration_data())
                self.assertTrue(form.is_valid())
                # Act
                user = form.save(commit=commit)
                # Assert
                self.assertNotEqual(user.password, 'Strong-password-123')
                self.assertTrue(user.check_password('Strong-password-123'))
                self.assertEqual(save.call_count, int(commit))

    def test_phone_validator_raises_on_invalid_input(self):
        # Arrange
        invalid = '12345'
        # Act / Assert: ожидаем исключение валидатора.
        with self.assertRaises(ValidationError):
            phone_regex(invalid)

    @patch('main.context_processors.ServiceItem.objects.filter')
    def test_cart_total_filters_corrupted_session_with_mocked_database(self, products):
        # Arrange
        products.return_value = [SimpleNamespace(id=1, price=Decimal('18.50'))]
        request = SimpleNamespace(session={'cart': {'1': 2, 'bad': 4, '3': -1, '4': None}})
        # Act
        result = cart_total(request)
        # Assert
        self.assertEqual(result, {'cart_total': Decimal('37.00')})
        products.assert_called_once_with(id__in={1: 2})

    @patch('main.context_processors.ServiceItem.objects.filter', return_value=[])
    def test_cart_total_handles_non_dictionary_session(self, products):
        # Arrange
        request = SimpleNamespace(session={'cart': []})
        # Act
        result = cart_total(request)
        # Assert
        self.assertEqual(result['cart_total'], Decimal('0.00'))
        products.assert_called_once_with(id__in={})
