import requests
import responses
from django.test import TestCase
from main.models import Partner
from lab2.integrations.partner_status import check_partner_website


class PartnerHTTPIntegrationTests(TestCase):
    """Реальная БД + реальный HTTP-клиент; responses заменяет транспорт requests."""
    @responses.activate
    def test_partner_http_statuses(self):
        for status, expected in [(200, True), (404, False), (503, False), (302, False)]:
            with self.subTest(status=status):
                # Arrange
                partner = Partner.objects.create(name='Partner', website=f'https://partner.example/{status}')
                responses.get(partner.website, status=status, body='Partner site')
                # Act
                available = check_partner_website(Partner.objects.get(pk=partner.pk))
                # Assert
                self.assertEqual(available, expected)
                self.assertEqual(responses.calls[-1].request.method, 'GET')
                self.assertEqual(responses.calls[-1].request.url, partner.website)
                self.assertEqual(responses.calls[-1].request.req_kwargs['timeout'], 3)
        self.assertEqual(len(responses.calls), 4)

    @responses.activate
    def test_transport_failure_and_timeout(self):
        for i, error in enumerate([requests.Timeout('slow'), requests.ConnectionError('offline')]):
            with self.subTest(error=type(error).__name__):
                # Arrange
                partner = Partner.objects.create(name='Partner', website=f'https://partner.example/error/{i}')
                responses.get(partner.website, body=error)
                # Act
                result = check_partner_website(partner)
                # Assert
                self.assertFalse(result)
        self.assertEqual(len(responses.calls), 2)

    @responses.activate
    def test_invalid_scheme_makes_no_http_request(self):
        # Arrange
        partner = Partner.objects.create(name='Invalid', website='file:///tmp/test')
        # Act / Assert
        with self.assertRaises(ValueError):
            check_partner_website(partner)
        self.assertEqual(len(responses.calls), 0)
