from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_with_roles(request):
    user = request.user
    role_bindings = []
    
    for rb in user.role_bindings.all():
        role_bindings.append({
            'id': str(rb.id),
            'role': {
                'id': str(rb.role.id),
                'name': rb.role.name
            }
        })
    
    return Response({
        'id': str(user.id),
        'username': user.username,
        'name': user.name,
        'email': user.email,
        'is_superuser': user.is_superuser,
        'role_bindings': role_bindings
    })
