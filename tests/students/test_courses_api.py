
import pytest
from rest_framework.test import APIClient
from students.models import Course, Student
from django.contrib.auth.models import User
from model_bakery import baker
from django.urls import reverse
import random
from django_testing.settings import MAX_STUDENTS_PER_COURSE as max_students


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

#Проверяем получение 1ого курса
@pytest.mark.django_db
def test_get_course(user, client, courses_factory):
    #Задаем количество создаваемых курсов рандомно
    course = courses_factory(_quantity=random.randint(5, 20))
    # print(f'{course}')
    #Сохраняем в переменную id 1ый
    course_id = course[0].pk
    # print(f'{course_id}')
    #Формируем адрес запроса по вьюхе???
    url = reverse ('courses-detail', args=[course_id])
    # print(f'Ссылка:{url}')
    #Делаем сам запрос
    response = client.get(url)
    #Проверяем статус ответа
    
    assert response.status_code == 200
    #Получаем данные с запроса
    response_data = response.json()
    response_course_name = response_data.get('name')
    # print(f'Название курса: {response_course_name}')
    #Проверяем правильность данных
    
    assert response_course_name == course[0].name

#Проверяем получение нескольких курсов 
@pytest.mark.django_db
def test_get_few_course(user, client, courses_factory):
    course = courses_factory(_quantity=random.randint(5, 20))
    url = reverse('courses-list')
    # print(f'Ссылка: {url}')
    response = client.get(url)
    # print(f'Ответ АПИ: {response}')
    
    assert response.status_code == 200

    courses_list = response.json()
    # print(f'Джисон: {courses_list}')

    for ind, course_data in enumerate(courses_list):
        # print(course_data)
        assert course_data.get('name') == course[ind].name

#Проверка фильтра по Id
@pytest.mark.django_db
def test_filter_id(user, client, courses_factory):
    course = courses_factory(_quantity=random.randint(5, 20))
    course_id = course[0].pk
    url = reverse('courses-list')
    filter_data = {'pk': course_id}
    response = client.get(url, data=filter_data)

    assert response.status_code == 200

    data = response.json()

    assert data[0].get('id') == course_id

#Проверка фильтра по имени
@pytest.mark.django_db
def test_filter_name(user, client, courses_factory):
    course = courses_factory(_quantity=random.randint(5, 20))
    course_id = course[0].pk
    course_name = course[0].name
    url = reverse('courses-list')
    print(f'Ссылка: {url}')
    filter_data = {'pk': course_id, 'name': course_name}
    response = client.get(url, data=filter_data)
    assert response.status_code == 200
    data = response.json()
    assert data[0].get('name') == course_name

#Проверка успешного создания курса
@pytest.mark.django_db
def test_course_create(user, client):
    data = {'name': 'Разработчик на Django'}
    response = client.post(
        path='/api/v1/courses/',
        data=data,
        # format='json',
        )
    assert response.status_code == 201
    response_data = response.json()
    assert response_data.get('name') == data.get('name')

#Проверка успешного изменения курса
@pytest.mark.django_db
def test_course_update(courses_factory, client, user):
    courses = courses_factory(_quantity=random.randint(5, 10))
    course_id = courses[0].pk
    url = reverse('courses-detail', args=[course_id])
    new_data = {
        'pk': course_id,
        'name': 'new_name',
    }
    response_patch = client.patch(
        path=url,
        data=new_data,
        )
    assert response_patch.status_code == 200

    response_get = client.get(path=url)
    data = response_get.json()

    assert data.get('name') == new_data.get('name')

#Проверка успешного удаления курса
@pytest.mark.django_db
def test_course_delete(courses_factory, client, user):
    courses = courses_factory(_quantity=random.randint(5, 30))
    count = Course.objects.count()
    course_id = courses[0].pk
    url = reverse('courses-detail', args=[course_id])
    response = client.delete(path=url)

    assert response.status_code == 204

    count_next = Course.objects.count()

    assert count_next == count - 1

#Проверка ограничения на количество студентов на курсе

@pytest.mark.parametrize(
    ['count_students', 'status'],
    (
        (max_students+1, 400),
        (max_students, 201),
    )
)
@pytest.mark.django_db
def test_quantity_students(students_factory, client, status, count_students):
    # print(f'Максимальное количество студентов - {(max_students + 1)}')
    student = students_factory(_quantity=1)
    #Создаем список из нужного количества элементов
    student_list = [student[0].pk] * count_students
    url = reverse('courses-list')
    #Создаем курс с заданным количеством студентов
    data_response = {
        'name': 'Питончик',
        'students': student_list,
    }
    response = client.post(url, data=data_response)
    assert response.status_code == status
