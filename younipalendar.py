import os
import datetime
from bs4 import BeautifulSoup
from icalendar import Calendar, Event

weekdays = ['mo', 'tu', 'we', 'th', 'fr', 'sa']

weekday_period_stime = [
    (9, 20, 0), (11, 10, 0), (13, 40, 0), (15, 30, 0), (17, 20, 0)
]

sat_period_stime = [
    (9, 0, 0), (10, 40, 0), (13, 10, 0), (14, 50, 0), (16, 30, 0), (18, 10, 0), (19, 50, 0)
]

weekday_period_duration = 100
sat_period_duration = 90

class ClassClass:
    def __init__(self, name, day, time, place, teacher):
        self.name = name
        self.day = day
        self.time = time
        self.place = place
        self.teacher = teacher


def generate_ics(input_file:str, term:int=1, output_file:str='classes.ics'):
    with open(input_file, encoding='utf-8') as unipa_page_file:
        unipa_page = unipa_page_file.read()
        unipa_page_soup = BeautifulSoup(unipa_page, 'html.parser')
    classes_data = get_classes(unipa_page_soup)
    if term == '2':
        classes_data = classes_data[48:]
    classes = generate_class_class(classes_data)
    cal = Calendar()
    for i in classes:
        cal.add_component(generate_event(i))
    with open(output_file, 'wb') as output:
        output.write(cal.to_ical())


def get_classes(soup):
    return soup.find_all('td', 'colYobi')


def generate_class_class(classes):
    class_classes = []
    for time in range(6):
        for day in range(6):
            class_data = classes[time*6+day]
            data = extract_data(class_data)
            if data is None:
                continue
            for d in data:
                name = d['name']
                place = d['place']
                teacher = d['teacher']
                class_classes.append(
                    ClassClass(name, day, time, place, teacher))
    return class_classes


def extract_data(class_data):
    if 'noClass' in class_data.div['class']:
        return None
    c = class_data.find_all('div', 'jugyo-info jugyo-normal')
    data = []
    for i in c:
        name = i.find_all('div')[0].string
        place = i.find_all('div')[2].span.string
        teacher = i.find_all('div')[1].string
        d = {'name': name,
             'place': place,
             'teacher': teacher}
        data.append(d)
    return data


def generate_time(weekday, time):
    today = datetime.date.today()
    date = today - datetime.timedelta(days=today.weekday()-weekday)
    year = date.year
    month = date.month
    day = date.day

    hms = weekday_period_stime[time] if weekday<5 else sat_period_stime[time]
    duration = weekday_period_duration if weekday<5 else sat_period_duration

    stime = datetime.datetime(year, month, day, *hms)
    time_delta = datetime.timedelta(minutes=duration)
    etime = stime + time_delta
    return stime, etime


def generate_event(the_class):
    event = Event()
    event.add('summary', the_class.name)
    event.add('rrule', {'freq': 'weekly', 'byday': weekdays[the_class.day]})
    if the_class.place is not None:
        event.add('location', the_class.place)
    stime, etime = generate_time(the_class.day, the_class.time)
    event.add('dtstart', stime)
    event.add('dtend', etime)
    event.add('attendee', the_class.teacher)
    return event


from guietta import _, Gui, R1, Quit, QFileDialog, QMessageBox

gui = Gui(
	[  "Input file",      "__a__",  ['Select input file'] ],
	[ "Output file",      "__b__", ['Select output file'] ],
    [ "Select term",            _,             ["Do it!"] ],
	[   R1('First'), R1('Second'),                   Quit ]
)
gui.b = 'classes.ics'
gui.First.setChecked(True)


def get_filename(type):
    def decorator(func):
        def file_selector(gui, *args):
            if type == 'IF':
                s = "HTML source file (*.html)"
            elif type == 'OF':
                s = "ICS calendar file (*.ics)"
            filename = QFileDialog.getOpenFileName(None, "Open File",
                                                   os. getcwd(),
                                                   s)[0]
            if filename != '':
                func(filename)
        return file_selector
    return decorator


@get_filename('IF')
def get_input_filename(filename):
    gui.a = filename


@get_filename('OF')
def get_output_filename(filename):
    gui.b = filename


def excute(gui, *args):
    if gui.First.isChecked():
        term = 1
    else:
        term = 2
    generate_ics(gui.a,term,gui.b)
    QMessageBox.information(None, 'SUCCEED!', 'The ics file has been generated!')


gui.events(
    [  _ ,  _ ,   get_input_filename ],
    [  _ ,  _ ,  get_output_filename ],
    [  _ ,  _ ,               excute ],
    [  _ ,  _ ,                    _ ]
)

gui.run()