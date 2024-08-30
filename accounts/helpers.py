from django.core.paginator import Paginator
from datetime import datetime
import re

from accounts.models import FriendRequest

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    if re.match(pattern, email):
        return True
    else:
        return False


def paginate_queryset(queryset, page=1):
    paginator = Paginator(queryset, 10)
    return paginator.get_page(page)


def check_friend_request_limit(user_id):

    current_time_limit = datetime.now().replace(second=0, microsecond=0)
    recent_requests_count = FriendRequest.objects.filter(sender__id=user_id, created_at__gte=current_time_limit).count()
    print("recent_requests_count :", recent_requests_count)

    if recent_requests_count >= 3:
        return False
    else:
        return True


