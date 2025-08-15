from rest_framework.response import Response

def api_response(data=None, message="", status=404,success=None):
    return Response({
        "success":success,
        "status": status,
        "message": message,
        "data": data if isinstance(data, list) else [data] if data else []
    }, status=status)
