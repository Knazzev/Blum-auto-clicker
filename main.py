import os
import time
import random
import cv2
import keyboard
import numpy as np
import pygetwindow as gw
import pyautogui
from pynput.mouse import Button, Controller
from pywinauto import Application
from mss import mss

CHECK_INTERVAL = 5

mouse = Controller()

time.sleep(0.5)

print("\nВыберете язык:")
print("1. English")
print("2. Русский")

while True:
    try:
        language_choice = int(input("Введите номер вашего языка: "))
        if language_choice in [1, 2]:
            break
        else:
            print("Неверный выбор. Пожалуйста, введите 1 или 2.")
    except ValueError:
        print("Неверный ввод. Пожалуйста, введите число.")

messages = {
    1: {
        "window_input": "\nEnter window name (1 - TelegramDesktop): ",
        "window_not_found": "[❌] | Window - {} not found!",
        "window_found": "[✅] | Window found - {}\nPress 'z' to pause.",
        "pause_message": "Pause\nPress 'z' again to continue",
        "continue_message": "Continue working."
    },
    2: {
        "window_input": "\nВведите название окна (1 - TelegramDesktop): ",
        "window_not_found": "[❌] | Окно - {} не найдено!",
        "window_found": "[✅] | Окно найдено - {}\nНажмите 'z' для паузы.",
        "pause_message": "Пауза \nНажмите снова 'z' что бы продолжить",
        "continue_message": "Продолжение работы."
    }
}

msg = messages[language_choice]

def click(x, y):
    mouse.position = (x, y + random.randint(1, 3))
    mouse.press(Button.left)
    mouse.release(Button.left)

def check_and_click_play_button(sct, monitor):
    templates = [
        cv2.imread(os.path.join("assets", "play_button2.png"), cv2.IMREAD_GRAYSCALE),
        cv2.imread(os.path.join("assets", "play_button1.png"), cv2.IMREAD_GRAYSCALE),
        cv2.imread(os.path.join("assets", "close_button.png"), cv2.IMREAD_GRAYSCALE),
        cv2.imread(os.path.join("assets", "captcha.png"), cv2.IMREAD_GRAYSCALE) 
    ]

    for template in templates:
        if template is None:
            print("Не удалось загрузить файл шаблона.")
            continue

        template_height, template_width = template.shape

        img = np.array(sct.grab(monitor))
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)

        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= 0.8)

        matched_points = list(zip(*loc[::-1]))

        if matched_points:
            pt_x, pt_y = matched_points[0]
            cX = pt_x + template_width // 2 + monitor["left"]
            cY = pt_y + template_height // 2 + monitor["top"]

            click(cX, cY)
            print(f'Нажал на кнопку: {cX} {cY}')
            break  

window_name = input(msg["window_input"])

window_name_map = {
    '1': "TelegramDesktop",
    '2': "KotatogramDesktop"
}
window_name = window_name_map.get(window_name, window_name)

check = gw.getWindowsWithTitle(window_name)
if not check:
    print(msg["window_not_found"].format(window_name))
else:
    print(msg["window_found"].format(window_name))

telegram_window = check[0] if check else None
paused = False

with mss() as sct:
    last_check_time = time.time()

    while telegram_window:
        if keyboard.is_pressed('z'):
            paused = not paused
            print(msg["pause_message"] if paused else msg["continue_message"])
            time.sleep(0.2)

        if paused:
            continue

        window_rect = (
            telegram_window.left, telegram_window.top, telegram_window.width, telegram_window.height
        )

        try:
            telegram_window.activate()
        except:
            telegram_window.minimize()
            telegram_window.restore()

        current_time = time.time()
        if current_time - last_check_time >= CHECK_INTERVAL:
            last_check_time = current_time
            monitor = {
                "top": window_rect[1],
                "left": window_rect[0],
                "width": window_rect[2],
                "height": window_rect[3]
            }
            check_and_click_play_button(sct, monitor)

        scrn = pyautogui.screenshot(region=(window_rect[0], window_rect[1], window_rect[2], window_rect[3]))

        width, height = scrn.size
        pixel_found = False

        for x in range(0, width, 20):
            for y in range(0, height, 20):
                r, g, b = scrn.getpixel((x, y))
                if (b in range(0, 125)) and (r in range(102, 220)) and (g in range(200, 255)):
                    screen_x = window_rect[0] + x
                    screen_y = window_rect[1] + y
                    click(screen_x, screen_y)
                    pixel_found = True
                    break
            if pixel_found:
                break
