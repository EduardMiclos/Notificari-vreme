# ---- IMPORTS ----
import os
import random
import tkinter
import tkinter.messagebox
from notifypy import Notify
import requests as rq
import datetime
from tkinter import *
# -----------------





# ---- GLOBAL -----
API = ''
CITY = ''
link = ''
response = ''

IMAGES_PATH = 'photos'
SOUNDS_PATH = 'sounds'
sent = 0

TO_RESTART = 0
# -----------------





# ----- FILE MANIPULATION -----
with open('credentials.txt', 'r', encoding='utf-8') as f:
    API = f.readline()[:-1]
    CITY = f.readline()
    f.close()
# -----------------------------





# ----- NOTIFICATIONS -----
notification = Notify()
# -------------------------





# ----- FUNCTIONS -----
def is_available(city):
    global response
    link = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric&lang=RO'
    response = rq.get(link)

    return response.status_code == 200

def get_city(entry, root):
    global CITY
    CITY = entry.get()

    if is_available(CITY):
        root.destroy()
        with open('credentials.txt', 'a', encoding='utf-8') as f:
            f.seek(0, 2)
            f.write(str(CITY))
            f.close()

def clear_city():
    global CITY
    CITY = ''
    with open('credentials.txt', 'w', encoding='utf-8') as f:
        f.write(API)
        f.write('\n')
        f.close()

def restart_app(root):
    global TO_RESTART, CITY
    clear_city()
    TO_RESTART = 1
    root.destroy()

def UI(status):
    root = tkinter.Tk()
    canvas = tkinter.Canvas(root, width=400, height=300)
    canvas.pack()
    img = PhotoImage(file=IMAGES_PATH + '/logo.png')
    canvas.create_image(200, 10, anchor=N, image=img)

    if status == 'input_handle':
        root.title('Vremea. Selectarea orașului')
        txt = "Introduceți orașul în care vă aflați."
        entry = tkinter.Entry()
        canvas.create_window(200, 140, window=entry)
        button = tkinter.Button(text='Trimite', command=lambda: get_city(entry, root))
    else:
        root.title('Vremea')
        txt = "Programul a pornit."
        button = tkinter.Button(text='Ok, super!', command=root.destroy)
        canvas.create_window(200, 190, window=button)
        button2 = tkinter.Button(text='Doresc să introduc alt oraș', command=lambda: restart_app(root))
        canvas.create_window(200, 220, window=button2)

    canvas.create_text(200, 100, text=txt)
    canvas.create_window(200, 190, window=button)
    root.mainloop()


def type_of_sound(icon):
    index = int(icon[:2])
    if index <= 4:
        return 'birds'
    elif index > 4 and index <= 10:
        return 'rain'
    elif index == 1:
        return 'lightning'
    elif index == 13:
        return 'snow'
    else:
        return 'mistery'

def random_sound(path):
    n = len(os.listdir(path))
    return str(int(random.random()*n))

def error_message(error_code):
    notification.message = f'Error: {error_code}'

def data_message(data, hour):
    weather = data["weather"][0]
    description = weather["description"]
    icon = weather["icon"]
    temp = round(data["main"]["temp"])

    hour_string = (hour if hour >= 10 else '0' + str(hour))
    notification.title = f'{CITY}. Vremea pentru ora {hour_string}:00.'
    notification.message = f'{description.capitalize()}.\nTemperatură: {temp} °C. '
    notification.icon = IMAGES_PATH + '/' + icon + '@2x.png'

    path = SOUNDS_PATH + '/' + type_of_sound(icon)
    notification.audio = path + '/' + random_sound(path) + '.wav'

def main():
    while (1):
        TIME = datetime.datetime.now()

        if TIME.minute == 0 and TIME.second == 0 and not sent:
            if response.status_code == 200:
                data_message(response.json(), TIME.hour)
            else:
                error_message(response.status_code)
            notification.send()
            sent = 1
        elif TIME.second == 5:
            sent = 0
# ----------------





# ----- MAIN LOOP -----
def loop():
    global TO_RESTART
    TO_RESTART = 0
    if not is_available(CITY):
        UI('input_handle')
        UI('working')
    else:
        UI('working')

    if not TO_RESTART:
        main()
    else:
        loop()

loop()
# ----------------

