#!/usr/bin/python

"""
Скрипт служит для отладки определения на скриншотах, если имена криво определяются
"""
from pprint import pprint

import main


if __name__ == '__main__':
    team = ['left', 'right']
    print('debug enable')
    for t in team:
        main.search_team('load_screen.jpg', t)
    main.search_text("tmp_left.jpg", debug=True)
    main.search_text("tmp_right.jpg", debug=True)
    print('debug end')
