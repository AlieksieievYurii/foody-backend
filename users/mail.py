from typing import List

import requests
from django.urls import reverse

from foody.settings import env
from users import views
from users.models import User, UserRole


class EmailManager(object):
    END_POINT: str = 'https://api.mailgun.net/v3/{domain_name}/messages'

    def __init__(self, api_key: str, domain_name: str) -> None:
        self._full_url = self.END_POINT.format(domain_name=domain_name)
        self._api_key: str = api_key
        self._from: str = f'Test Foody <mailgun@{domain_name}>'

    def send_email(self, to: List[str], subject: str, message: str) -> None:
        response = requests.post(self._full_url, auth=('api', self._api_key), data={
            'from': self._from,
            'to': to,
            'subject': subject,
            'html': message,
        })
        response.raise_for_status()

    def send_email_confirmation_to_client(self, request, client: User, token: str) -> None:
        confirmation_endpoint = request.build_absolute_uri(reverse(views.confirm_user, kwargs={
            'email': client.email, 'token': token
        }))

        self.send_email([client.email], "Confirm Email", message=f"""
            <html>
                <h3>Hi {client.full_name}</h3></br>
                <p>Thanks for the registration. Go on the link to confirm your email.</p></br>
                </br>
                <p>{confirmation_endpoint}</p>
            </html>
        """)

    def send_executor_request_to_administrators(self, user_role: UserRole):
        administrators = UserRole.objects.filter(role=UserRole.UserRoleChoice.administrator.name)
        for admin in administrators:
            self.send_email(admin.user.email, "Executor request", message=f"""
            <html>
                <h3>Dear {admin.user.full_name}</h3></br>
                <p>{user_role.user.full_name} requested to become an Executor!</p></br>
                <p>Go to the application and accept him :)</p></br>
                </br>
            </html>
            """)


email_manager_instance = EmailManager(
    api_key=env('MAILGUN_API_KEY'),
    domain_name=env('MAILGUN_DOMAIN_NAME')
)
