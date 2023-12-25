from django.conf import settings
from datetime import datetime, timedelta
import jwt
import secrets
import string


def generate_access_token(email):
	token_string = ''.join(secrets.choice(
		string.ascii_uppercase + string.ascii_lowercase)for i in range(31))
	payload = {
		'user_email': email,
		'exp': datetime.utcnow() + timedelta(days=1, minutes=0),
		'iat': datetime.utcnow(),
	}

	access_token = jwt.encode(payload, token_string, algorithm='HS256')
	return access_token
