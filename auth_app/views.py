from django.shortcuts import render
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import login
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
import logging
from allauth.socialaccount.providers.oauth2.views import OAuth2CallbackView

# Logger
logger = logging.getLogger(__name__)

User = get_user_model()

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        data = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        }
        return Response(data)

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.GOOGLE_CALLBACK_URL
    client_class = OAuth2Client

@api_view(['GET'])
def google_login(request):
    return Response({'login_url': f"{settings.BASE_URL}/accounts/google/login/"})

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user has successfully authenticated via a social provider.
        """
        # Check if email is verified
        if sociallogin.account.extra_data.get('verified_email') is False:
            msg = 'The email is not verified'
            return Response({'error': msg}, status=400)

        # Check if user exists
        try:
            user = User.objects.get(email=sociallogin.account.extra_data.get('email'))
        except User.DoesNotExist:
            # Create a new user
            user = User(
                email=sociallogin.account.extra_data.get('email'),
                username=sociallogin.account.extra_data.get('email').split('@')[0],
                first_name=sociallogin.account.extra_data.get('given_name'),
                last_name=sociallogin.account.extra_data.get('family_name'),
            )
            user.save()

            # Connect the social account to the new user
            sociallogin.connect(request, user)

@api_view(['GET'])
def google_callback(request):
    logger.debug(f"Callback URL: {request.build_absolute_uri()}")
    logger.debug(f"Query params: {request.GET}")

    try:
        # Use the OAuth2CallbackView directly
        adapter = GoogleOAuth2Adapter(request)
        callback_view = OAuth2CallbackView.adapter_view(GoogleOAuth2Adapter)
        response = callback_view(request)
        
        # If authentication is successful, create or get a token
        if request.user.is_authenticated:
            refresh = RefreshToken.for_user(request.user)
            return redirect(f"{settings.FRONTEND_URL}/Auth/login")
        else:
            return redirect(f"{settings.FRONTEND_URL}/login-failed")
    except Exception as e:
        logger.error(f"Unexpected error during Google callback: {str(e)}", exc_info=True)
        return redirect(f"{settings.FRONTEND_URL}/login-error")
