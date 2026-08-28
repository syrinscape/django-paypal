from __future__ import unicode_literals

import unittest

from django.conf import settings
from django.test.utils import override_settings
from mock import patch


if not settings.configured:
    settings.configure(SECRET_KEY="secret-key", USE_I18N=False)


from paypal.standard.forms import (
    PayPalEncryptedPaymentsForm,
    PayPalSharedSecretEncryptedPaymentsForm,
)


class SharedSecretTextTests(unittest.TestCase):
    @override_settings(SECRET_KEY="secret-key")
    def test_form_adds_the_accepted_shared_secret_to_the_notify_url(self):
        form = PayPalSharedSecretEncryptedPaymentsForm(
            initial={
                "business": "merchant@example.com",
                "item_name": "Sound Set",
                "notify_url": "https://example.test/ipn/",
            }
        )

        self.assertEqual(
            "https://example.test/ipn/"
            "?secret=dea6d37d70f331f37942efd775d9e7d82979427a",
            form.initial["notify_url"],
        )


class EncryptedButtonTextTests(unittest.TestCase):
    @patch.object(
        PayPalEncryptedPaymentsForm,
        "_encrypt",
        autospec=True,
        return_value=(
            b"-----BEGIN PKCS7-----\n"
            b"encoded-payload\n"
            b"-----END PKCS7-----\n"
        ),
    )
    def test_form_renders_the_encrypted_payload_as_plain_text(self, encrypt):
        html = PayPalEncryptedPaymentsForm().as_p()

        self.assertIn(
            'value="-----BEGIN PKCS7-----\nencoded-payload\n-----END PKCS7-----\n"',
            html,
        )
        self.assertNotIn('value="b\'-----BEGIN PKCS7-----', html)
