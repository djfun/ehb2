import hashlib
from __init__ import *
from config import conf

from itsdangerous import URLSafeSerializer

def generate_confirmation_token(email):
    serializer = URLSafeSerializer(conf.get('server', 'secret'))
    return serializer.dumps(email, salt=conf.get('server', 'password_salt') + conf.get('application', 'shortname'))


def confirm_token(token):
    serializer = URLSafeSerializer(conf.get('server', 'secret'))
    try:
        email = serializer.loads(
            token,
            salt=conf.get('server', 'password_salt') + conf.get('application', 'shortname')
        )
    except:
        return False
    return email