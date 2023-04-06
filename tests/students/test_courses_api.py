
import pytest
from rest_framework.test import APIClient
from students.models import Course, Student
from django.contrib.auth.models import User
from model_bakery import baker


@pytest.mark.django_db
def test_api():
    
    #Arrange---Подготовка данных
    
    #Получение клиента для отправки запросов в API сервис
    client = APIClient()
    # User.objects.create()
    # course = Course.objects.create(student_id=1)
    
    #Act---Тестируемый функционал
    
    #Запрос в API сервис
    response = client.get('/api/v1/courses/')
    
    #Assert---Проверка того, что действие выполнено корректно (валидный ответ)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
    

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user('test')

@pytest.fixture
def courses_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)
    return factory

@pytest.fixture
def students_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)
    return factory

@pytest.mark.django_db
def test_get_course():
    course = courses_factory(_quantity=8)
    course_id = course[0].pk