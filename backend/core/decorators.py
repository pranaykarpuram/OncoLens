from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def role_required(*roles):
    acceptable = set(roles)

    def decorator(view_fn):
        @wraps(view_fn)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("accounts:login")
            role = getattr(getattr(request.user, "profile", None), "role", None)
            if role not in acceptable:
                messages.error(request, "You do not have access to this area.")
                return redirect("core:review_queue")
            return view_fn(request, *args, **kwargs)

        return _wrapped

    return decorator
