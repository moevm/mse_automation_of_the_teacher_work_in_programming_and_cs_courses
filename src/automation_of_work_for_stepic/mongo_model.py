from mongoengine import *

from mongoengine import *


class Student(Document):
    id = IntField(required=True, primary_key=True)
    name_stepic = StringField(max_length=50, required=True)
    name_google = StringField(max_length=50)
    progress_courses = MapField(field=FloatField(), default={})
    progress_sections = MapField(field=FloatField(), default={})
    progress_lessons = MapField(field=FloatField(), default={})

    @queryset_manager
    def add_progress(doc_cls, queryset, student=None, lesson=None, section=None, course=None, progress=None):
        if not student or progress is None:
            return None

        if lesson:
            return queryset.filter(id=student).update_one(**{'progress_lessons__' + str(lesson): progress})

        if section:
            return queryset.filter(id=student).update_one(**{'progress_sections__' + str(section): progress})

        if course:
            return queryset.filter(id=student).update_one(**{'progress_courses__' + str(course): progress})


class Step(Document):
    id = IntField(required=True, primary_key=True)
    lesson = IntField(required=True)
    position = IntField(required=True)


class Lesson(Document):
    id = IntField(required=True, primary_key=True)
    title = StringField(max_length=100, required=True)
    section = IntField(required=True)
    steps = ListField(IntField(),required=True)


class Section(Document):
    id = IntField(required=True, primary_key=True)
    title = StringField(max_length=100, required=True)
    course = IntField(required=True)
    lessons = ListField(IntField(), required=True)


class Course(Document):
    id = IntField(required=True, primary_key=True)
    title = StringField(max_length=100, required=True)
    sections = ListField(IntField(), required=True)

class Grade(Document):
    student = IntField(required=True)
    step = IntField(required=True)
    is_passed = BooleanField(required=True)
    wrong_date = DateTimeField()
    correct_date = DateTimeField()

    @queryset_manager
    def progress(doc_cls, queryset, student=None, steps=None):
        if steps and student:
            return queryset.filter(student=student, step__in=steps).item_frequencies('is_passed', normalize=True).get(
                True, 0.0) * 100
        elif steps:
            return queryset.filter(step__in=steps).item_frequencies('is_passed', normalize=True).get(
                True, 0.0) * 100
        elif student:
            return queryset.filter(student=student).item_frequencies('is_passed', normalize=True).get(
                True, 0.0) * 100
        else:
            return queryset.item_frequencies('is_passed', normalize=True).get(
                True, 0.0) * 100


class Incorrect(Document):
    unknown_student = IntField(required=True)
    unknown_course = IntField(required=True)
    no_permissions_course = ListField(IntField(), required=True)


class User(Document):
    id = IntField(required=True, primary_key=True)
    last_update = DateTimeField(required=True)
