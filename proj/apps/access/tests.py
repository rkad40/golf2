from django.core import mail
from django.core.mail import EmailMessage
from django.test import TestCase


DEBUG = True

DO_EMAIL_TEST = False

class EmailTest(TestCase):
    def test_001_send_email(self):
        if DO_EMAIL_TEST: # pragma: no cover
            mail.send_mail(
                'Subject here', 
                'Here is the message.',
                'rkad40@yahoo.com', 
                ['rodney.kadura@gmail.com'],
                fail_silently=False)
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].subject, 'Subject here')
            email = EmailMessage('email_subject', 'message', to=['rkad40@yahoo.com'])
            email.send()

