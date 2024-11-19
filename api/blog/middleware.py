from django.http import JsonResponse
import requests
import aiohttp
import os
import re
from dotenv import load_dotenv

load_dotenv()

NON_SECURE_PATHS = [
    r"/auth/logout",
    r"/auth/register",
    r"/auth/login",
    r"/blog/posts/",
    r"/blog/posts/\d+/details/",  
    r"/blog/posts/\d+/like/",     
    r"/blog/posts/\d+/images/",   
    r"/blog/posts/\d+/comments/", 
    r"/blog/notifications/",
    r"/subscribe/"
]

SSO_URL = os.getenv('SSO_URL')

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        for path in NON_SECURE_PATHS:
            if re.match(f"^{path}$", request.path): 
                return self.get_response(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JsonResponse({"error": "Authorization header is missing or malformed"}, status=400)

        token = auth_header.split("Bearer ")[1]

        try:
            response = requests.post(SSO_URL, headers={"Authorization": f"Bearer {token}"})
            if response.status_code != 200 or response.json().get("EC") != 1:
                return JsonResponse({"error": "User not authenticated"}, status=401)
        except Exception as e:
            return JsonResponse({"error": "Error while validating token: " + str(e)}, status=500)

        return self.get_response(request)

    async def async_call(self, request):
        for path in NON_SECURE_PATHS:
            if re.match(f"^{path}$", request.path):  
                return await self.get_response(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JsonResponse({"error": "Authorization header is missing or malformed"}, status=400)

        token = auth_header.split("Bearer ")[1]

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(SSO_URL, headers={"Authorization": f"Bearer {token}"}) as response:
                    if response.status != 200 or (await response.json()).get("EC") != 1:
                        return JsonResponse({"error": "User not authenticated"}, status=401)
        except Exception as e:
            return JsonResponse({"error": "Error while validating token: " + str(e)}, status=500)

        return await self.get_response(request)
