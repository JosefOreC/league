from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def test(request, *args, **kwargs):
    return JsonResponse({"message": "Acción completada con éxito"})