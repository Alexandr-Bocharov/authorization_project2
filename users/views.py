from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework import status, generics
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from users.models import User
from users.permissions import IsUser
from users.serializers import UserSerializer, ProfileSerializer

from users.services import create_unique_invite_code, send, generate_sms_code


class UserCreateAPIView(CreateAPIView):
    """Обработка создания пользователей, сохраняет пользователя,присваивает инвайт-код и высылает СМС-код для входа."""
    serializer_class = UserSerializer  # Указываем сериализатор для обработки данных
    queryset = User.objects.all()
    permission_classes = (AllowAny,)  # Разрешаем доступ всем пользователям

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)  # Получаем сериализатор с данными запроса
        data_dict = {}  # Словарь для хранения ответов
        try:
            # Проверяем данные, если невалидные - выбрасываем исключение
            serializer.is_valid(raise_exception=True)
            user = serializer.save()  # Сохраняем пользователя

            # Генерируем и присваиваем уникальный пригласительный код
            user.invite_code = create_unique_invite_code()
            data_dict['invite_code'] = user.invite_code  # Добавляем код в ответ

            # Генерируем код для авторизации и устанавливаем его как пароль пользователя
            code = generate_sms_code()  # Генерируем код для авторизации
            user.set_password(code)  # Устанавливаем сгенерированный пароль
            user.save()  # Сохраняем изменения в пользователе



        except Exception as e:
            # Обработка других ошибок по типу не уникальности номера телефона
            user = User.objects.filter(phone=request.data.get('phone')).first()
            if user:
                data_dict['invite_code'] = user.invite_code  # Возвращает код существующего пользователя
            else:
                data_dict['error'] = str(e)  # Возвращает сообщение об ошибке

        # Возвращает ответ с кодом 201
        return Response(data_dict, status=status.HTTP_201_CREATED)


class UserProfileRetrieveAPIView(RetrieveAPIView):
    """Обработка отображения данных пользователя"""
    serializer_class = ProfileSerializer  # Указываем сериализатор для отображения профиля
    queryset = User.objects.all()  # Определяем, что будем работать со всеми пользователями
    permission_classes = (IsAuthenticated, IsUser)  # Только аутентифицированные пользователи с правами

    def get_object(self, *args, **kwargs):
        return get_object_or_404(User, pk=self.kwargs['pk'])


class UserUpdateAPIView(UpdateAPIView):
    """Обработка обновления данных пользователя"""
    serializer_class = UserSerializer  # Указываем сериализатор для обработки данных
    queryset = User.objects.all()  # Определяем, что будем работать со всеми пользователями
    permission_classes = (IsAuthenticated, IsUser)  # Только аутентифицированные пользователи с правами

    def get_object(self, *args, **kwargs):
        return get_object_or_404(User, pk=self.kwargs['pk'])


class UserListAPIView(ListAPIView):
    """Обработка списка данных пользоватеей"""
    serializer_class = ProfileSerializer  # Указываем сериализатор для обработки данных
    queryset = User.objects.all()  # Определяем, что будем работать со всеми пользователями
    permission_classes = (IsAuthenticated,)  # Только аутентифицированные пользователи