from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Student(models.Model):

    name = models.TextField()

    birth_date = models.DateField(
        null=True,
    )


class Course(models.Model):

    name = models.TextField()

    students = models.ManyToManyField(
        Student,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)]
    )
