import json
import matplotlib as mpl
import matplotlib.pyplot as plt
from datetime import datetime as dt
from datetime import timedelta


class Painter:
    def __init__(self, course_id, d):
        self.course_id = course_id
        self.d = d

    def get_start_info(self, date_step=2):
        a = {}
        for students in self.d:
            for course in students['courses']:
                if self.course_id == course['id']:
                    count_steps = 0
                    title = course['title']
                    for section in course['sections']:
                        for lesson in section['lessons']:
                            for step in lesson['steps']:
                                count_steps += 1
                                if step['first_true']:
                                    a.setdefault(course['title'], []).append(step['first_true'])

        earliest = dt.now().date()
        for key, value in a.items():
            for date1 in value:
                date1 = dt.strptime(date1, "%Y-%m-%d").date()
                earliest = min(date1, earliest)
        self.print_graphic(title, earliest, count_steps, date_step)



    def progress_for_date(self, count_steps, date):
        passed_steps = 0

        for students in self.d:
            for course in students['courses']:
                if self.course_id == course['id']:
                    for section in course['sections']:
                        for lesson in section['lessons']:
                            for step in lesson['steps']:
                                if step['first_true']:
                                    date1 = step['first_true']
                                    date1 = dt.strptime(date1, "%Y-%m-%d").date()
                                    if date1 <= date:
                                        passed_steps += 1
        progress = passed_steps*100/(count_steps*len(d))
        return progress


    def print_graphic(self, title,  sdate, count_steps,date_step):
        latest = dt.now().date()
        values = []
        dates = []
        delta = timedelta(days=date_step)
        while (sdate <= latest):
            dates.append(sdate)
            sdate += delta
        for date in dates:
            values.append(self.progress_for_date(count_steps, date))

        dpi = 80
        fig = plt.figure(dpi=dpi, figsize=(1280 / dpi, 1024 / dpi))
        mpl.rcParams.update({'font.size': 10})
        plt.title('Прогресс группы по курсу:' + title)
        ax = plt.axes()
        ax.set_ylim([0, 100])
        plt.ylabel('%')
        plt.xlabel('Дата')
        ax.yaxis.grid(True, zorder=1)
        xs = range(len(dates))
        plt.bar([x for x in xs], values, width=0.2, color='red', alpha=0.7, label=course_id, zorder=2)
        plt.xticks(xs, dates)
        fig.autofmt_xdate(rotation=25)
        plt.legend(loc='upper right')
        fig.savefig('./graphics/' + course_id + '.png')


if __name__ == '__main__':
    with open('./instance/full_info.json') as data:
        d = json.load(data)
    course_id = '37011'
    date_step = 2
    a=Painter(course_id, d)
    a.get_start_info()
    

