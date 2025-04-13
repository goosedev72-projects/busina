import flet as ft
import asyncio
from catprinter import ble, cmds, img
import logging

# Выключить логи Flet
logging.basicConfig(level=logging.ERROR)

# Конфигурация приложения
PRINT_WIDTH = 384

# Алгоритмы преобразования в grayscale
ALGO_CHOICES = [
    ft.dropdown.Option("Mean Threshold"),
    ft.dropdown.Option("Floyd-Steinberg"),
    ft.dropdown.Option("Atkinson"),
    ft.dropdown.Option("Halftone"),
    ft.dropdown.Option("None"),
]

async def main(page: ft.Page):
    page.title = "Мини-принтер"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.CrossAxisAlignment.CENTER

    # Поле для вывода пути к изображению
    img_path_text = ft.Text(value="")

    # Кнопка для выбора изображения
    def select_img(e):
        def file_picker_result(e):
            if e.files:
                img_path_text.value = e.files[0].path
                page.update()

        file_picker = ft.FilePicker(on_result=file_picker_result)
        page.overlay.append(file_picker)
        page.update()  
        file_picker.pick_files()  

    select_img_button = ft.ElevatedButton("Выбрать изображение", on_click=select_img)

    # Выбор алгоритма преобразования в grayscale
    algo_choice = ft.Dropdown(
        options=ALGO_CHOICES,
        hint_text="Алгоритм преобразования в grayscale",
        width=300,
    )

    # Поле для вывода журнала отладки
    debug_log_text = ft.Text(
        value="",
        width=580,
        height=200,
        text_align=ft.TextAlign.LEFT,
        selectable=True
    )

    # Кнопка для печати
    def print_img(e):
        img_path = img_path_text.value
        algo = algo_choice.value
        if img_path and algo:
            debug_log_text.value = ""
            page.update()
            asyncio.run(print_image(img_path, algo, debug_log_text))
        else:
            print("Пожалуйста, выберите изображение и алгоритм.")

    print_button = ft.ElevatedButton("Печать", on_click=print_img)

    # Добавить элементы на страницу
    page.controls = [
        ft.Column(
            [
                select_img_button,
                img_path_text,
                algo_choice,
                print_button,
                debug_log_text,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    ]

    # Функция для печати изображения
    async def print_image(img_path, algo, debug_log_text):
        try:
            debug_log_text.value += f"Принтер: Путь к изображению - {img_path}\n"
            debug_log_text.value += f"Принтер: Алгоритм преобразования в grayscale - {algo}\n"
            page.update()

            algo_map = {
                "Mean Threshold": "mean-threshold",
                "Floyd-Steinberg": "floyd-steinberg",
                "Atkinson": "atkinson",
                "Halftone": "halftone",
                "None": "none",
            }
            algo = algo_map[algo]
            debug_log_text.value += f"Принтер: Выбран алгоритм преобразования в grayscale (map) - {algo}\n"
            page.update()

            debug_log_text.value += f"Принтер: Преобразование изображения в grayscale...\n"
            page.update()
            bin_img = img.read_img(img_path, PRINT_WIDTH, algo)
            debug_log_text.value += f"Принтер: Изображение преобразовано успешно. Размер - {bin_img.shape}\n"
            page.update()

            debug_log_text.value += f"Принтер: Подготовка данных для печати...\n"
            page.update()
            data = cmds.cmds_print_img(bin_img, energy=0xFFFF)
            debug_log_text.value += f"Принтер: Данные подготовлены успешно. Размер данных - {len(data)}\n"
            page.update()

            debug_log_text.value += f"Принтер: Печать изображения...\n"
            page.update()
            await ble.run_ble(data, device=None)
            debug_log_text.value += f"Принтер: Изображение напечатано успешно.\n"
            page.update()
        except Exception as e:
            debug_log_text.value += f"Принтер: Ошибка печати изображения - {str(e)}\n"
            page.update()

    page.update()

ft.app(target=main)
