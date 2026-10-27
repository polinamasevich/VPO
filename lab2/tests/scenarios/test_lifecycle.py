from django.urls import reverse
from main.models import Review
from lab2.tests.helpers import StoreCase, checkout_data


class ReviewLifecycleTests(StoreCase):
    def test_review_created_edited_deleted_by_owner(self):
        # Arrange: S0 — записи ещё нет; автор вошёл.
        self.client.force_login(self.owner)
        self.assertFalse(Review.objects.filter(user=self.owner).exists())
        # Act T1: публикация.
        response = self.client.post(reverse('reviews'), {'rating': 5, 'text': 'Первая версия'})
        # Assert: S1 — опубликован.
        self.assertRedirects(response, reverse('reviews'))
        review = Review.objects.get(user=self.owner)
        self.assertEqual(review.user_name, 'owner')
        self.assertContains(self.client.get(reverse('reviews')), 'Первая версия')
        # Act T3: редактирование.
        response = self.client.post(reverse('edit_review', args=[review.pk]), {'rating': 4, 'text': 'Новая версия'})
        # Assert: S2 — опубликован после редактирования, ID сохранён.
        self.assertRedirects(response, reverse('reviews'))
        review.refresh_from_db()
        self.assertEqual((review.rating, review.text), (4, 'Новая версия'))
        self.assertContains(self.client.get(reverse('reviews')), 'Новая версия')
        # Act T6: удаление.
        self.client.post(reverse('delete_review', args=[review.pk]))
        # Assert: S3 — удалён (конечное состояние).
        self.assertFalse(Review.objects.filter(pk=review.pk).exists())
        self.assertNotContains(self.client.get(reverse('reviews')), 'Новая версия')
        self.assertEqual(self.client.get(reverse('edit_review', args=[review.pk])).status_code, 404)

    def test_invalid_create_and_edit_do_not_change_state(self):
        # Arrange
        self.client.force_login(self.owner)
        # Act T2: невалидная публикация.
        response = self.client.post(reverse('reviews'), {'rating': 0, 'text': 'abc'})
        # Assert: остаёмся в S0.
        self.assertTrue(response.context['form'].errors)
        self.assertFalse(Review.objects.filter(user=self.owner).exists())
        # Arrange: успешная публикация S1.
        self.client.post(reverse('reviews'), {'rating': 5, 'text': 'Хорошая пицца'})
        review = Review.objects.get(user=self.owner)
        # Act T4: невалидное изменение.
        response = self.client.post(reverse('edit_review', args=[review.pk]), {'rating': 6, 'text': 'abc'})
        # Assert: остаёмся в S1; значения в БД прежние.
        self.assertTrue(response.context['form'].errors)
        review.refresh_from_db()
        self.assertEqual((review.rating, review.text), (5, 'Хорошая пицца'))
        self.assertEqual(self.client.get(reverse('edit_review', args=[review.pk])).status_code, 200)

    def test_stranger_cannot_change_published_review(self):
        # Arrange: S1, вошёл другой пользователь.
        review = Review.objects.create(user=self.owner, user_name='owner', rating=5, text='Оригинал')
        self.client.force_login(self.other)
        # Act T5: чужое изменение и удаление.
        edit = self.client.post(reverse('edit_review', args=[review.pk]), {'rating': 1, 'text': 'Подмена'})
        delete = self.client.post(reverse('delete_review', args=[review.pk]))
        # Assert: остаёмся в S1.
        self.assertRedirects(edit, reverse('reviews'))
        self.assertRedirects(delete, reverse('reviews'))
        review.refresh_from_db()
        self.assertEqual((review.rating, review.text), (5, 'Оригинал'))

    def test_staff_can_edit_and_delete_another_users_review(self):
        # Arrange: S1.
        review = Review.objects.create(user=self.owner, user_name='owner', rating=5, text='Оригинал')
        self.client.force_login(self.staff)
        # Act T3
        self.client.post(reverse('edit_review', args=[review.pk]), {'rating': 4, 'text': 'Исправлено'})
        # Assert S2
        review.refresh_from_db()
        self.assertEqual(review.text, 'Исправлено')
        # Act T6 / Assert S3
        self.client.post(reverse('delete_review', args=[review.pk]))
        self.assertFalse(Review.objects.filter(pk=review.pk).exists())


    def test_edited_review_repeated_updates_and_rejections(self):
        # Arrange: создать S1 и перейти в S2 через HTTP.
        self.client.force_login(self.owner)
        self.client.post(reverse('reviews'), {'rating': 5, 'text': 'Оригинал'})
        review = Review.objects.get(user=self.owner)
        url = reverse('edit_review', args=[review.pk])
        self.client.post(url, {'rating': 4, 'text': 'Версия два'})
        # Act T3: S2 → S2, ещё одно допустимое изменение.
        self.client.post(url, {'rating': 3, 'text': 'Версия три'})
        # Assert
        review.refresh_from_db()
        self.assertEqual(review.text, 'Версия три')
        # Act T4: невалидное изменение S2.
        response = self.client.post(url, {'rating': 9, 'text': 'abc'})
        # Assert
        self.assertTrue(response.context['form'].errors)
        review.refresh_from_db()
        self.assertEqual((review.rating, review.text), (3, 'Версия три'))
        # Act T5: чужой пользователь не может изменить/удалить S2.
        self.client.force_login(self.other)
        self.client.post(url, {'rating': 1, 'text': 'Чужая версия'})
        self.client.post(reverse('delete_review', args=[review.pk]))
        # Assert
        review.refresh_from_db()
        self.assertEqual((review.rating, review.text), (3, 'Версия три'))

    def test_published_review_deleted_without_editing(self):
        # Arrange: S0 → S1.
        self.client.force_login(self.owner)
        self.client.post(reverse('reviews'), {'rating': 5, 'text': 'Оригинал'})
        review = Review.objects.get(user=self.owner)
        # Act T6: S1 → S3.
        self.client.post(reverse('delete_review', args=[review.pk]))
        # Assert
        self.assertFalse(Review.objects.filter(pk=review.pk).exists())


class CartScenarioTests(StoreCase):
    def test_cart_quantity_transitions(self):
        # Arrange
        key = str(self.pizza.pk)
        # Act / Assert: пусто → 1 → 2 → 1 → пусто.
        self.client.post(reverse('add_to_cart', args=[self.pizza.pk]))
        self.assertEqual(self.client.session['cart'][key], 1)
        self.client.post(reverse('update_cart', args=[self.pizza.pk]), {'action': 'increase'})
        self.assertEqual(self.client.session['cart'][key], 2)
        self.client.post(reverse('update_cart', args=[self.pizza.pk]), {'action': 'decrease'})
        self.assertEqual(self.client.session['cart'][key], 1)
        self.client.post(reverse('update_cart', args=[self.pizza.pk]), {'action': 'remove'})
        self.assertNotIn(key, self.client.session['cart'])

    def test_checkout_error_corrected_then_success(self):
        # Arrange: заполненная корзина.
        self.client.post(reverse('add_to_cart', args=[self.pizza.pk]))
        # Act: переход к форме.
        page = self.client.get(reverse('checkout'))
        # Assert
        self.assertTemplateUsed(page, 'main/checkout.html')
        # Act: доставка без адреса.
        failed = self.client.post(reverse('checkout'), checkout_data(fulfillment_method='delivery'))
        # Assert: оформление не завершено, товары сохранены.
        self.assertIn('address', failed.context['form'].errors)
        self.assertTrue(self.client.session['cart'])
        # Act: исправление данных.
        success = self.client.post(reverse('checkout'), checkout_data(fulfillment_method='delivery', address='Минск, 1'))
        # Assert: страница успеха и пустая корзина; повторное оформление невозможно.
        self.assertTemplateUsed(success, 'main/checkout_success.html')
        self.assertEqual(self.client.session['cart'], {})
        self.assertRedirects(self.client.post(reverse('checkout'), checkout_data()), reverse('cart'))
