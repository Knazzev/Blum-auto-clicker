import pyautogui
import pygetwindow as gw
import time
import keyboard
import random
from pynput.mouse import Button, Controller
import colorama
from colorama import Fore
import asyncio

colorama.init(autoreset=True)
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

window_name = input(msg["window_input"])

window_name_map = {
    '1': "TelegramDesktop",
    '2': "KotatogramDesktop"
}
window_name = window_name_map.get(window_name, window_name)

check = gw.getWindowsWithTitle(window_name)
if not check:
    print(msg["window_not_found"].format(window_name))
    exit()
else:
    print(msg["window_found"].format(window_name))

telegram_window = check[0]
paused = False

async def find_and_click_objects():
    scrn = pyautogui.screenshot(region=(telegram_window.left, telegram_window.top + 50, telegram_window.width, telegram_window.height - 100))
    width, height = scrn.size

    for x in range(0, width, 10):
        for y in range(0, height, 10):
            r, g, b = scrn.getpixel((x, y))

            if (b in range(50, 255)) and (r in range(150, 255)) and (g in range(0, 255)):
                if not (r > 240 and g > 240 and b > 240):
                    screen_x = telegram_window.left + x
                    screen_y = telegram_window.top + 50 + y
                    click(screen_x + 4, screen_y)
                    await asyncio.sleep(0.001)

async def check_pause():
    global paused
    while True:
        if keyboard.is_pressed('z'):
            paused = not paused
            print(msg["pause_message"] if paused else msg["continue_message"])
            await asyncio.sleep(0.2)
        await asyncio.sleep(0.1)

async def main_loop():
    while True:
        if paused:
            await asyncio.sleep(0.1)
            continue

        window_rect = (
            telegram_window.left, telegram_window.top, telegram_window.width, telegram_window.height
        )

        try:
            telegram_window.activate()
        except:
            telegram_window.minimize()
            telegram_window.restore()

        await find_and_click_objects()

async def main():
    await asyncio.gather(main_loop(), check_pause())

asyncio.run(main())
