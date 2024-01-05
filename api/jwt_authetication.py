# importing typing module
from typing import Optional
# importing request, response and status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

# importing access token from rest framework simplejwt
from rest_framework_simplejwt.tokens import AccessToken
# importing models
from users.models import User
# importing wraps form functools
from functools import wraps


# to authenticate JWT
class JWT:
    # creating a static method ot authenticate the user with token
    @staticmethod
    def authenticate(req: Request) -> Optional[Response]:
        auth_header = req.META.get("HTTP_AUTHORIZATION")
        if not auth_header:
            return Response(
                {"messages": ["Missing Authorization header"]}, status=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return Response({"messages": ["No Token provided"]}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            validated_token = AccessToken(token=token)
        except Exception:
            return Response({"messages": ["Invalid Token"]}, status=status.HTTP_401_UNAUTHORIZED)

        payload = validated_token.payload
        user_id = payload.get("user_id")
        user = User.objects.filter(id=user_id).first()
        req.user = user
        # to pass the request ot the view method
        pass


# decorator to authenticate the user with the token
def authenticate_jwt(view_method) -> Response:
    @wraps(view_method)
    def wrapper(instance, req, *args, **kwargs):
        try:
            auth_header = req.META.get("HTTP_AUTHORIZATION")

            if not auth_header:
                return Response( {"messages": ["Missing Authorization header"]},status=status.HTTP_401_UNAUTHORIZED)
            try: 
                token = auth_header.split(" ")[1]
            except IndexError:
                return Response( {"messages": ["No Token provided"]},status=status.HTTP_401_UNAUTHORIZED)
            # to validate the token
            try:
                validated_token = AccessToken(token=token)
            except Exception:
                return Response({"messages": ["Invalid Token"]}, status=status.HTTP_401_UNAUTHORIZED)
            # extracting the user id from the payload
            payload = validated_token.payload
            user_id = payload.get("user_id")
            user = User.objects.filter(id=user_id).first()
            if not user:
                return Response( {"messages": ["User not found!"]}, status=status.HTTP_401_UNAUTHORIZED)
            # setting the user in the req object
            req.user = user
            return view_method(instance, req, *args, **kwargs)
        except Exception as e:
            return Response( {"messages": ["Internal server error"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return wrapper
