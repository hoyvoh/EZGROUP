from django.http import JsonResponse
import requests
import jwt
import os
import re
from dotenv import load_dotenv

load_dotenv()

NON_SECURE_PATHS = [
    r"/api/v1/auth/logout",
    r"/api/v1/auth/register",
    r"/api/v1/auth/login",
    r"/api/v1/blog/posts/$", 
    r"/api/v1/blog/posts/\d+/$",  
    r"/api/v1/blog/posts/\d+/comments/$",  
    r"/api/v1/blog/posts/\d+/images/$",  
    r"/api/docs/",
    r"/"
    r"/api/v1/blogs/posts", 
    r"/api/v1/blogs/posts/\d+",
    r"/api/v1/blogs/posts/\d+/likes",  
    r"/api/v1/blogs/posts/\d+/comments",  
    r"/api/v1/blogs/posts/\d+/images",
    r"/api/docs"  
]


SSO_URL = os.getenv('SSO_URL')

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path.rstrip('/')
        print(f"\nProcessing request for path: {path}")

        if self.should_skip_auth(path):
            print(f"Skipping auth for path: {path}")
            return self.get_response(request)
        for pattern in NON_SECURE_PATHS:
            print(f"Checking pattern {pattern} against path {path}")
            if re.match(pattern, path):
                print(f"Path {path} matches pattern {pattern}, skipping auth")
                return self.get_response(request)
    
        print(f"Path {path} requires authentication")
            
        token = self.extract_token(request)
        print("Token in JWT authen:", token)
        if not token:
            return JsonResponse({
                "EC": -1,
                "EM": "Bearer token is required",
                "DT": ""
            }, status=401)

        try:
            verify_url = SSO_URL
            print(f"Verifying token at: {verify_url}")
            
            response = requests.post(
                verify_url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                timeout=5
            )
            
            data = response.json()
            print(f"SSO Response Data: {data}")

            if response.status_code == 200 and data.get("EC") == 1:
                try:
                    decoded = jwt.decode(token, options={"verify_signature": False})
                    print(f"Decoded token: {decoded}")
                    
                    request.user_data = {
                        'id': decoded.get('user_id'),
                        'email': decoded.get('email'),
                        'full_name': f"{decoded.get('first_name', '')} {decoded.get('last_name', '')}".strip(),
                        'role': decoded.get('roleWithPermission', {}),
                        'permissions': [
                            perm['url'] for perm in decoded.get('roleWithPermission', {}).get('Permissions', [])
                        ]
                    }
                    print(f"Attached user data: {request.user_data}")
                    
                    current_path = path.replace('/api/v1', '')
                    if current_path in request.user_data['permissions']:
                        print(f"User has permission for path: {current_path}")
                        request.auth_token = token
                        return self.get_response(request)
                    else:
                        print(f"User lacks permission for path: {current_path}")
                        return JsonResponse({
                            "EC": -1,
                            "EM": "Permission denied",
                            "DT": ""
                        }, status=403)
                    
                except jwt.InvalidTokenError as e:
                    print(f"Token decode error: {str(e)}")
                    return JsonResponse({
                        "EC": -1,
                        "EM": "Invalid token format",
                        "DT": ""
                    }, status=401)
            
            return JsonResponse({
                "EC": -1,
                "EM": data.get("EM", "Invalid token"),
                "DT": ""
            }, status=401)

        except requests.RequestException as e:
            print(f"Request error: {str(e)}")
            return JsonResponse({
                "EC": -1,
                "EM": f"SSO service error: {str(e)}",
                "DT": ""
            }, status=503)
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return JsonResponse({
                "EC": -1,
                "EM": f"Authentication error: {str(e)}",
                "DT": ""
            }, status=500)

    def extract_token(self, request):
        auth_header = request.headers.get("Authorization")
        print("Authorization at extract token:", auth_header)
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            print(f"Extracted token: {token[:30]}...")
            return token
        return None

    def should_skip_auth(self, path):
        for pattern in NON_SECURE_PATHS:
            if re.match(pattern, path):
                return True
        return False