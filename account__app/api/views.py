from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from rest_framework import status

from .serializers import RegistrationSerializer
from .models import create_auth_token
# from rest_framework_simplejwt.tokens import RefreshToken ##JWT_Token


@api_view(['POST'])
def registration_view(request):
    serializer = RegistrationSerializer(data=request.data)

    data = {}

    if serializer.is_valid():
        account = serializer.save()

        data["response"] = "Registered Successfully"
        data["username"] = account.username
        data["email"] = account.email
        data["token"] = Token.objects.get(user=account).key

        ##JWT_Token
        # refresh = RefreshToken.for_user(account)
        # data["token"] = {
        #                     'refresh': str(refresh),
        #                     'access': str(refresh.access_token),
        #                 }


    else:
        data["error"] = serializer.errors

    return Response(data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def logout_view(request):
    if not request.user.is_anonymous:
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_401_UNAUTHORIZED)
