from django.http import JsonResponse
from .models import Question
from query_snitch.decorators import n_plus_one_threshold


@n_plus_one_threshold(1)
def index(request):
    queryset = Question.objects.all()
    data = [
        {
            "question": str(question),
            "choices": [str(choice) for choice in question.choice_set.all()],
        }
        for question in queryset
    ]
    return JsonResponse({"data": data})
