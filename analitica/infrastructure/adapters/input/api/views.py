from django.http import JsonResponse


def test(request):
    return JsonResponse({"message": "Módulo analitica — lógica movida a competencia/infrastructure/ia/"})
