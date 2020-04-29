import sys
import datetime
from bs4 import BeautifulSoup
from icalendar import Calendar, Event

weekdays = ['mo','tu','we','th','fr','sa']

class class_class:
    def __init__(self, name, day, time, place):
        self.name = name
        self.day = day
        self.time = time
        self.place = place

def get_classes(soup):
    return soup.find_all('td','colYobi')

def generate_class_class(classes):
    class_classes = []
    for time in range(6):
        for day in range(6):
            class_data = classes[time*6+day]
            name, place = extract_data(class_data)
            if name!=None:
                class_classes.append(class_class(name, day, time, place))
    return class_classes

def extract_data(class_data):
    if 'noClass' in class_data.div['class']:
        return None, None
    name = class_data.find_all('div')[1].string
    place = class_data.find_all('div')[3].span.string
    return name, place

def generate_time(day,time):
    today = datetime.date.today()
    date = today - datetime.timedelta(days=today.weekday()-day)
    if time==0:
        stime = datetime.datetime(date.year,date.month,date.day,9,20,0)
        etime = datetime.datetime(date.year,date.month,date.day,11,0,0)
    if time==1:
        stime = datetime.datetime(date.year,date.month,date.day,11,10,0)
        etime = datetime.datetime(date.year,date.month,date.day,12,50,0)
    if time==2:
        stime = datetime.datetime(date.year,date.month,date.day,13,40,0)
        etime = datetime.datetime(date.year,date.month,date.day,15,20,0)
    if time==3:
        stime = datetime.datetime(date.year,date.month,date.day,15,30,0)
        etime = datetime.datetime(date.year,date.month,date.day,17,10,0)
    if time==4:
        stime = datetime.datetime(date.year,date.month,date.day,17,20,0)
        etime = datetime.datetime(date.year,date.month,date.day,19,0,0)
    return stime, etime



def generate_event(the_class):
    event = Event()
    event.add('summary', the_class.name)
    event.add('rrule',{'freq':'weekly', 'byday':weekdays[the_class.day]})
    event.add('location',the_class.place)
    stime, etime = generate_time(the_class.day,the_class.time)
    event.add('dtstart', stime)
    event.add('dtend',etime)
    return event
    

if __name__ == "__main__":
    term = sys.argv[1]
    unipa_page_file = open(sys.argv[2])
    unipa_page = unipa_page_file.read()
    unipa_page_soup = BeautifulSoup(unipa_page, "html.parser")
    classes_data = get_classes(unipa_page_soup)
    if term==2:
        classes_data = classes_data[48:]
    classes = generate_class_class(classes_data)
    cal = Calendar()
    for i in classes:
        cal.add_component(generate_event(i))
    output = open('classes.ics','wb')
    output.write(cal.to_ical())

    