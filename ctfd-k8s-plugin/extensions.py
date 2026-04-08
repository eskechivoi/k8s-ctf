from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from CTFd.utils.user import get_current_user

def get_user_id_key():
    user = get_current_user()
    if user:
        return str(user.id)
    return get_remote_address()

limiter = Limiter(key_func=get_user_id_key)