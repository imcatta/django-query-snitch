from collections import Counter
import logging
import pprint

from django.db import connection

logger = logging.getLogger("query_snitch")


def n_plus_one_detector(get_response):
    """
    Middleware to detect N+1 query problems.

    Logs a warning when duplicate queries are detected and adds a custom
    header 'x-n-plus-one-queries' to the response.

    Configure the threshold by setting 'query_snitch_threshold' attribute
    on the response object (default: 1).
    """

    class QueryLogger:
        def __init__(self):
            self.select_queries = []

        def __call__(self, execute, sql, params, many, context):
            if sql.startswith("SELECT"):
                self.select_queries.append(sql)
            return execute(sql, params, many, context)

    def middleware(request):
        query_logger = QueryLogger()
        with connection.execute_wrapper(query_logger):
            response = get_response(request)

        query_counts = Counter(query_logger.select_queries)
        threshold = getattr(response, "n_plus_one_threshold", 1)
        repeating_queries = {
            query: count for query, count in query_counts.items() if count > threshold
        }
        if repeating_queries:
            logger.warning(
                "Query Snitch detected N+1 queries on %s '%s'\n%s",
                request.method,
                request.get_full_path(),
                pprint.pformat(repeating_queries),
            )
            response["x-n-plus-one-queries"] = "true"
        return response
    
    return middleware
