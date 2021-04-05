import gi
gi.require_version("Gtk","3.0")
from gi.repository import Gtk

import sys
import datetime
from bs4 import BeautifulSoup
from icalendar import Calendar, Event

weekdays = ['mo', 'tu', 'we', 'th', 'fr', 'sa']

def main_gui():
    window = MainWindow()
    window.show_all()
    
    Gtk.main()

def main_cli():
    term = sys.argv[1]
    input_file = sys.argv[2]
    generate_ics(input_file, term)
    

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

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="younipalendar")
        self.grid = Gtk.Grid()
        self.add(self.grid)

        self.input_filename = 'page.html'
        self.output_filename = 'classes.ics'
        self.term = 1

        self.connect("destroy", Gtk.main_quit)

        self.input_entry = Gtk.Entry()
        self.input_entry.set_text("Select input file. Default is \"page.html\".")

        self.output_entry = Gtk.Entry()
        self.output_entry.set_text("Select output file. Default is \"classes.ics\".")

        self.input_button = Gtk.Button(label="open")
        self.output_button = Gtk.Button(label="open")
        self.generate_button = Gtk.Button(label="generate")

        self.input_button.connect('clicked', self.select_input_file)
        self.output_button.connect('clicked', self.select_output_file)
        self.generate_button.connect('clicked', self.execute)

        self.term1_radio = Gtk.RadioButton.new_with_label_from_widget(None, "Term 1")
        self.term1_radio.connect("toggled", self.set_term, 1)

        self.term2_radio = Gtk.RadioButton.new_from_widget(self.term1_radio)
        self.term2_radio.set_label("Term 2")
        self.term2_radio.connect("toggled", self.set_term, 2)

        self.grid.attach(self.input_button, 20, 0, 5, 5)
        self.grid.attach(self.output_button, 20, 5, 5, 5)
        self.grid.attach(self.generate_button, 20, 15, 5, 5)

        self.grid.attach(self.input_entry, 0, 0, 20, 5)
        self.grid.attach(self.output_entry, 0, 5, 20, 5)

        self.grid.attach(self.term1_radio,0, 10, 5, 5)
        self.grid.attach(self.term2_radio,5, 10, 5, 5)

    def select_input_file(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Please choose a file", parent=self, action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.input_filename = dialog.get_filename()
            self.input_entry.set_text(self.input_filename)
        dialog.destroy()

    def select_output_file(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Please choose a file", parent=self, action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.output_filename = dialog.get_filename()
            self.output_entry.set_text(self.output_filename)
        dialog.destroy()

    def execute(self,widget):
        generate_ics(self.input_filename, self.term, self.output_filename)
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Congratulations!",
        )
        dialog.format_secondary_text(
            "The ics file has been generated."
        )
        dialog.run()
        dialog.destroy()

    def set_term(term:int):
        self.term = term


class ClassClass:
    def __init__(self, name, day, time, place, teacher):
        self.name = name
        self.day = day
        self.time = time
        self.place = place
        self.teacher = teacher


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
    if weekday < 5:
        if time == 0:
            stime = datetime.datetime(year, month, day, 9, 20, 0)
            etime = datetime.datetime(year, month, day, 11, 0, 0)
        if time == 1:
            stime = datetime.datetime(year, month, day, 11, 10, 0)
            etime = datetime.datetime(year, month, day, 12, 50, 0)
        if time == 2:
            stime = datetime.datetime(year, month, day, 13, 40, 0)
            etime = datetime.datetime(year, month, day, 15, 20, 0)
        if time == 3:
            stime = datetime.datetime(year, month, day, 15, 30, 0)
            etime = datetime.datetime(year, month, day, 17, 10, 0)
        if time == 4:
            stime = datetime.datetime(year, month, day, 17, 20, 0)
            etime = datetime.datetime(year, month, day, 19, 0, 0)
    else:
        if time == 0:
            stime = datetime.datetime(year, month, day, 9, 0, 0)
            etime = datetime.datetime(year, month, day, 10, 30, 0)
        if time == 1:
            stime = datetime.datetime(year, month, day, 10, 40, 0)
            etime = datetime.datetime(year, month, day, 12, 10, 0)
        if time == 2:
            stime = datetime.datetime(year, month, day, 13, 10, 0)
            etime = datetime.datetime(year, month, day, 14, 40, 0)
        if time == 3:
            stime = datetime.datetime(year, month, day, 14, 50, 0)
            etime = datetime.datetime(year, month, day, 16, 20, 0)
        if time == 4:
            stime = datetime.datetime(year, month, day, 16, 30, 0)
            etime = datetime.datetime(year, month, day, 18, 0, 0)
        if time == 5:
            stime = datetime.datetime(year, month, day, 18, 10, 0)
            etime = datetime.datetime(year, month, day, 19, 40, 0)
        if time == 6:
            stime = datetime.datetime(year, month, day, 19, 50, 0)
            etime = datetime.datetime(year, month, day, 21, 20, 0)
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


if __name__ == "__main__":
    if len(sys.argv) != 1:
        main_cli()
    else:
        main_gui()
