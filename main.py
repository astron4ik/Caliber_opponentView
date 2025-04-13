#!/usr/bin/python
"""
Description
en: This script collects information about opponents from the screenshot of the application, collects it into a file,
and counts the number of meetings, and the last meeting (ally enemy)

Описание
ru: Этот скрипт собирает информацию об оппонентах со скриншота приложения, собирает в файл, и считает количество
встреч, и последняя встреча (союзник враг)

Ожидание клавиш:
PrintScreen - выполнение функции скрипта
ctrl+c -  завершить работу скрипта

Переменны для заполнения:
list_owner_and_teammate - Список, в котором указаны ники запускающего скрипт и его друзей по команде
"""

# DONE: Снятие скриншота с экрана/игры - Загрузочный экран
# TODO: Добавить проверку что скриншот снят с загрузочного экрана (иначе может начаться коллапс в result.csv)
# DONE: Сделать ожидание клавиши, для снятия скришота
# DONE: Разбивка скриншота на левую и правую часть, для идентификации команды
# DONE: Распознавание текста, в переменные
# DONE: Определение стороны - союзник/враг
# DONE: Загрузка cvs в память для обработки
# DONE: Добавить исключения для игрока, кто собирает информацию, и его друзей (Только для команды союзников)
# DONE: Выполнение условий, поиск по базе:
# DONE: * Если в базе ников нету, внести и выставить счетчик в 1.
# DONE: * Если есть в базе, счетчик +1
# DONE: Упаковка в файл csv

from pprint import pprint
from PIL import Image, ImageGrab

import win32gui
import cv2
import easyocr
import csv
import keyboard
import time
import random

file_csv = 'result.csv'

# Информация для исключений
list_owner_and_teammate = ['Astron4ik', 'Niondrago', 'TuLSkiY___oRuZHEynik', 'NoVy4ok', 'inxoteb', 'GawrGuras', 'Gomer3334']

# Списки игроков за команды
team_left = []
team_right = []

toplist, winlist = [], []


def search_text(scr, debug=False):
    image = cv2.imread(scr)
    reader = easyocr.Reader(['en'])
    text = reader.readtext(image, low_text=0.5, width_ths=2, contrast_ths=0.5)

    if scr == 'tmp_left.jpg':
        for nickname in text:
            team_left.append(nickname[1])
    elif scr == 'tmp_right.jpg':
        for nickname in text:
            team_right.append(nickname[1])

    if debug:
        # DEBUG DRAW BOUNDING BOX
        for t in text:
            print(t)
            bbox, text, score = t
            l_bbox = bbox[0][0]
            l_bbox1 = bbox[0][1]
            r_bbox = bbox[2][0]
            r_bbox1 = bbox[2][1]

            cv2.rectangle(image, (int(l_bbox), int(l_bbox1)), (int(r_bbox), int(r_bbox1)), (0, 255, 0), 2)
            cv2.putText(image, text, (int(l_bbox), int(l_bbox1)), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)

        # SAVE Pic AND OUTPUT WINDOW
        name = "pic"+str(random.randint(0, 5))+".jpg"
        cv2.imwrite(name, image)
        cv2.imshow("Out", image)
        cv2.waitKey(0)


def enum_cb(hwnd, results):
    winlist.append((hwnd, win32gui.GetWindowText(hwnd)))


# Функция снятия скриншота
def take_screenshot():
    win32gui.EnumWindows(enum_cb, toplist)
    for hwnd, title in winlist:
        if 'Caliber' in title:
            print("found")
            app_hwnd = hwnd
    win32gui.SetForegroundWindow(app_hwnd)
    bbox = win32gui.GetWindowRect(app_hwnd)
    img = ImageGrab.grab(bbox)
    img.save("load_screen.jpg")


# Функции обработки скриншота
def search_team(scr, side):
    im = Image.open(scr)

    if side == "left":
        ratio_width = 6.91
        ratio_height = 3.06
        ratio_end_width = 9.84
        ratio_end_height = 2.91

        cord_start = [int(im.width / ratio_width), int(im.height / ratio_height)]
        print("start point:", cord_start)

        a = cord_start[0] + int(im.width / ratio_end_width)
        b = cord_start[1] + int(im.height / ratio_end_height)
        cord_stop = [a, b]
        print("end point", cord_stop)
    elif side == "right":
        ratio_width = 5.23
        ratio_height = 3.06
        ratio_end_width = 11.15
        ratio_end_height = 2.91

        w_start_point = im.width - int(im.width / ratio_width)
        h_start_point = int(im.height / ratio_height)

        w_end_point = im.width - int(im.width / ratio_end_width)
        h_end_point = h_start_point + int(im.height / ratio_end_height)

        cord_start = [w_start_point, h_start_point]
        print("start point:", cord_start)
        cord_stop = [w_end_point, h_end_point]
        print("end point", cord_stop)

    im_crop = im.crop((cord_start[0], cord_start[1], cord_stop[0], cord_stop[1]))
    # im_crop.show()
    im_crop.save(f"tmp_{side}.jpg")


# Обработка csv файла
def filling_information():
    new_rows, tmp_rows = [], []

    with open(file_csv, 'r', newline='') as file:
        reader = csv.reader(file, delimiter=',', quotechar=',',
                            quoting=csv.QUOTE_MINIMAL)
        rows = list(reader)

        for name in team_left:
            for row in rows[1:]:
                if name == row[0]:
                    row[1] = str(int(row[1]) + 1)
                    row[2] = 'left'
                    break
            else:
                new_rows.append([name, '1', 'left', '-'])
                continue

        for row in new_rows:
            if row[0] not in list_owner_and_teammate:
                tmp_rows.append(row)
        new_rows = tmp_rows

        for name in team_right:
            for row in rows[1:]:
                if name == row[0]:
                    row[1] = str(int(row[1]) + 1)
                    row[2] = 'right'
                    break
            else:
                new_rows.append([name, '1', 'right', '-'])
                continue

    with open(file_csv, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',', quotechar=',',
                            quoting=csv.QUOTE_MINIMAL)
        writer.writerows(rows)
        for line in new_rows:
            writer.writerow(line)
        print('finish filling')


if __name__ == '__main__':
    team = ['left', 'right']

    while True:
        try:
            if keyboard.is_pressed('print screen'):
                take_screenshot()
                for t in team:
                    search_team('load_screen.jpg', t)
                search_text("tmp_left.jpg")
                search_text("tmp_right.jpg")
                # pprint(team_left)
                # pprint(team_right)
                filling_information()
                time.sleep(0.5)
                break
            if keyboard.is_pressed('ctrl+c'):
                exit(100)
        except KeyboardInterrupt:
            break
