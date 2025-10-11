from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseForbidden

class AdminRedirectMiddleware:
    """
    Middleware pour rediriger les superutilisateurs vers l'admin
    et empêcher l'accès aux pages utilisateur
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Pages autorisées pour les admins
        admin_allowed_paths = [
            '/admin/',
            '/logout/',
            '/static/',
            '/media/',
        ]
        
        # Si l'utilisateur est un superutilisateur
        if request.user.is_authenticated and request.user.is_superuser:
            # Vérifier si la requête concerne une page admin autorisée
            is_admin_path = any(request.path.startswith(path) for path in admin_allowed_paths)
            
            # Si ce n'est pas une page admin autorisée, rediriger vers /admin/
            if not is_admin_path:
                return redirect('/admin/')
        
        response = self.get_response(request)
        return response