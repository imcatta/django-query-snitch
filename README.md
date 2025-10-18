# 👀 Django Query Snitch

**Don't let your queries snitch on you!**

A Django middleware that detects N+1 query problems and reports them before they snitch on your performance in production.

## 🎯 What It Does

Query Snitch monitors your Django views and catches those sneaky N+1 queries that happen when you:
- Forget to use `.select_related()` for ForeignKey fields
- Forget to use `.prefetch_related()` for ManyToMany or reverse ForeignKey fields
- Loop through querysets and trigger additional queries

When duplicate queries are detected, Query Snitch:
- Logs a warning with details about the repeating queries
- Adds a custom header `x-query-snitch-detected: true` to the response

## 🚀 Quick Start

### 1. Add to Middleware

Add `query_snitch.middleware.n_plus_one_detector` to your `MIDDLEWARE` in `settings.py`:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # ... other middleware ...
    *(['query_snitch.middleware.n_plus_one_detector'] if DEBUG else []),  # add this
]
```

### 2. That's It!

Query Snitch will now monitor your views and warn you about N+1 problems:

```shell
Query Snitch detected N+1 queries on GET '/polls/'
{'SELECT "polls_choice"."id", "polls_choice"."question_id", "polls_choice"."choice_text", "polls_choice"."votes" FROM "polls_choice" WHERE "polls_choice"."question_id" = %s': 20}
```

## 🎛️ Configuration

### Custom Threshold

By default, Query Snitch reports queries that repeat more than once. You can customize this per-view:

```python
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from query_snitch.decorators import n_plus_one_threshold

# Function-based view
@n_plus_one_threshold(3) # Allow up to 3 duplicate queries before reporting
def my_view(request):
    ...

# Class-based view
@method_decorator(n_plus_one_threshold(3), method="dispatch")
class MyView(View):
    ...
```

## 💡 What are N+1 Queries?

N+1 queries happen when you retrieve a set of objects — such as a list of posts — and then access a related object for each item, like the author of each post. Rather than fetching all related objects in a single query, Django will run one query to get the main objects and then make an additional query for each related object. If there are N items in your collection, you end up with N extra queries. This can quickly add up, resulting in a significant number of database queries and negatively affecting your application's performance.

### N+1 Problem

```python
# views.py
def post_list(request):
    posts = Post.objects.all()  # 1 query
    data = []
    for post in posts:
        data.append({
            'title': post.title,
            'author': post.author.name,  # N additional queries! 😱
        })
    return JsonResponse(data, safe=False)
```

### Fix

```python
# views.py
def post_list(request):
    posts = Post.objects.select_related('author').all()  # 1 query with JOIN
    data = []
    for post in posts:
        data.append({
            'title': post.title,
            'author': post.author.name,  # No additional queries! 🎉
        })
    return JsonResponse(data, safe=False)
```
