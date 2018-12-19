from mongoengine import *

## student

class Student(Document):
    id = IntField(required=True, primary_key=True)
    name_stepic = StringField(max_length=50, required=True)
    name_google = StringField(max_length=50)
    progress_courses = DictField(default={})
    progress_sections = DictField(default={})
    progress_lessons = DictField(default={})

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

    @queryset_manager
    def add_correct_date(doc_cls, queryset, student=None, lesson=None, section=None, course=None, date=None):
        if not student or date is None:
            return None
        if lesson:
            return queryset.filter(id=student).update_one(**{'progress_lessons__date' + str(lesson): date})

        if section:
            return queryset.filter(id=student).update_one(**{'progress_sections__date' + str(section): date})

        if course:
            return queryset.filter(id=student).update_one(**{'progress_courses__date' + str(course): date})


## course

class Step(Document):
    id = IntField(required=True, primary_key=True)
    lesson = IntField(required=True)
    position = IntField(required=True)
    count_passed = IntField(default=0)


class Lesson(Document):
    id = IntField(required=True, primary_key=True)
    title = StringField(max_length=100, required=True)
    section = IntField(required=True)
    steps = ListField(IntField(), required=True)


class Section(Document):
    id = IntField(required=True, primary_key=True)
    title = StringField(max_length=100, required=True)
    course = IntField(required=True)
    lessons = ListField(IntField(), required=True)


class Course(Document):
    id = IntField(required=True, primary_key=True)
    title = StringField(max_length=100, required=True)
    sections = ListField(IntField(), required=True)


## grade

class Grade(Document):
    student = IntField(required=True)
    step = IntField(required=True)
    is_passed = BooleanField(required=True)
    wrong_date = DateTimeField()
    correct_date = DateTimeField()

    @queryset_manager
    def progress(doc_cls, queryset, student=None, steps=None):
        if steps is not None and student is not None:
            return queryset.filter(student=student, step__in=steps).item_frequencies('is_passed', normalize=True).get(
                True, 0.0) * 100
        elif steps is not None:
            return queryset.filter(step__in=steps).item_frequencies('is_passed', normalize=True).get(
                True, 0.0) * 100
        elif student is not None:
            return queryset.filter(student=student).item_frequencies('is_passed', normalize=True).get(
                True, 0.0) * 100
        else:
            return queryset.item_frequencies('is_passed', normalize=True).get(
                True, 0.0) * 100

    @queryset_manager
    def first_correct_date(doc_cls, queryset, student=None, steps=None):
        if steps is not None and student is not None:
            grade = queryset.filter(student=student, step__in=steps).order_by('-correct_date').first()
            return grade.correct_date if grade else None
        elif steps is not None:
            grade = queryset.filter(step__in=steps).order_by('-correct_date').first()
            return grade.correct_date if grade else None
        elif student is not None:
            grade = queryset.filter(student=student).order_by('-correct_date').first()
            return grade.correct_date if grade else None
        else:
            grade = queryset.order_by('-correct_date').first()
            return grade.correct_date if grade else None


## incorrect

class Incorrect(Document):
    id = IntField(required=True, primary_key=True)
    unknown_student = ListField(StringField(),default=[])
    unknown_course = ListField(IntField(), default=[])
    no_permission_course = ListField(IntField(), default=[])


## user

class User(Document):
    id = IntField(required=True, primary_key=True)
    last_update = DateTimeField()


## config

class GTable(EmbeddedDocument):
    URL = URLField(required=True)
    Sheet = IntField(required=True)
    FIO_Col = StringField(max_length=3)
    FIO_Rows = ListField(IntField(), required=True)
    ID_Col = StringField(max_length=3)
    ID_Rows = ListField(IntField(), required=True)


class Stepic(EmbeddedDocument):
    id_course = ListField(IntField(), required=True)


class Config(Document):
    id = IntField(required=True, primary_key=True)
    google_table = EmbeddedDocumentField(GTable)
    stepic = EmbeddedDocumentField(Stepic)
    students=ListField(IntField())
    courses=ListField(IntField())