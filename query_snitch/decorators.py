import functools
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def n_plus_one_threshold(threshold: int):
    """
    Decorator to set a custom threshold for the n_plus_one_detector middleware.

    By default, Query Snitch reports any query that repeats more than once.
    Use this decorator to allow a higher threshold for specific views.

    No-op if the middleware is not in settings.MIDDLEWARE.

    Args:
        threshold: Number of times a query can repeat before being reported.

    Usage:
        # Function-based view
        @n_plus_one_threshold(3)
        def my_view(request):
            ...

        # Class-based view
        from django.utils.decorators import method_decorator

        @method_decorator(n_plus_one_threshold(3), method="dispatch")
        class MyView(View):
            ...
    """

    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            response = view_func(*args, **kwargs)
            response.n_plus_one_threshold = threshold
            return response

        return wrapper

    def noop_decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            return view_func(*args, **kwargs)

        return wrapper

    middleware_list = getattr(settings, "MIDDLEWARE", [])
    is_active = "query_snitch.middleware.n_plus_one_detector" in middleware_list

    return decorator if is_active else noop_decorator
