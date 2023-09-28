from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.views import generic
from django.urls import reverse_lazy
from logging import getLogger
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import UserInfo, Message
from .utils import send_to_bot


logger = getLogger(__name__)


def index(request):
    errors = []
    if request.method == "POST" and request.user.is_authenticated:
        if request.POST.get("token"):
            request.user.userinfo.generate_token()
        elif request.POST.get("sendmsg"):
            chat_id = request.user.userinfo.tg_chat_id
            if chat_id:
                message_data = request.POST["sendmsg"]
                user = request.user
                message = Message(text=message_data, user=user)
                message.save()
                send_to_bot(chat_id=chat_id, message=message_data)
            else:
                errors = ["Send generated token to telegram bot @factory_bot"]

    messages = []
    if request.user.is_authenticated:
        messages = Message.objects.filter(user=request.user)

    return render(request, "messages_bot/index.html", {"errors": errors, "messages": messages})


class Update(APIView):
    def post(self, request):
        req_data = request.data

        if "token_update" in req_data:
            chat_id = req_data["token_update"].get("chat_id")
            token = req_data["token_update"].get("token")

            logger.info("updating chat_id for token: %s, %s", chat_id, token)

            if chat_id and token:
                try:
                    user = UserInfo.objects.get(token=token)
                    user.tg_chat_id = chat_id
                    user.save()
                    send_to_bot(chat_id=chat_id, message="Token updated!")
                    return Response(status=status.HTTP_200_OK)
                except ObjectDoesNotExist:
                    logger.error("Failed to find user with token %s and chat_id %s", token, chat_id)
                    errormsg = f"User not found, go to {settings.PRODUCTION_HOST} and generate new, then paste it here"
                    send_to_bot(chat_id=chat_id, message=errormsg)
                    return Response(errormsg, status=status.HTTP_400_BAD_REQUEST)
                except:
                    logger.error("Couldn't update chat_id for user with token %s", token)
                    errormsg = "couldn't update token"
                    send_to_bot(chat_id=chat_id, message=errormsg)
                    return Response(errormsg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_200_OK)


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"
