import os

from kivy.uix.screenmanager import Screen
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.lang.builder import Builder

from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.snackbar import Snackbar

from locale import setlocale, LC_ALL

from .dropdownmenuitem import MenuListItem


# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


Builder.load_file(os.path.join(os.path.dirname(os.path.dirname(__file__)), "kv", "createreport.kv"))


# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


class CreateReportScreen(Screen):
    """Экран создания отчёта. Если у учителя уже создан отчёт, старый дополняется новыми данными."""
    def __init__(self, rm, **kwargs):
        super().__init__(**kwargs)

        """========= Инициализация менеджера отчётов ========="""
        self.rm = rm

        self.user_pref = ""

        """========= Создание меню выбора предмета ========="""
        self.course_menu = MDDropdownMenu(
            caller=self.ids.course,
            items=[],
            hor_growth="right",
            ver_growth="up",
            width_mult=6
        )
        self.course_menu.bind()

        """========= Создание меню выбора класса ========="""
        self.n_class_menu = MDDropdownMenu(
            caller=self.ids.n_class,
            items=[],
            hor_growth="right",
            ver_growth="up",
            width_mult=6
        )
        self.n_class_menu.bind()

        """========= Создание меню выбора типа отчёта ========="""
        report_menu_items = [
            {
                "viewclass": "MenuListItem",
                "text": "Контрольная работа",
                "height": dp(56),
                "on_release": lambda x="Контрольная работа": self.set_report_type(x),
            },
            {
                "viewclass": "MenuListItem",
                "text": "Четверть",
                "height": dp(56),
                "on_release": lambda x="Четверть": self.set_report_type(x),
            },
            {
                "viewclass": "MenuListItem",
                "text": "Год",
                "height": dp(56),
                "on_release": lambda x="Год": self.set_report_type(x),
            }
        ]
        self.report_type = MDDropdownMenu(
            caller=self.ids.report_type,
            items=report_menu_items,
            hor_growth="right",
            ver_growth="up",
            width_mult=4,
        )
        self.report_type.bind()

        """========= Создание меню выбора четвертей ========="""
        quarters = [
            {
                "viewclass": "MenuListItem",
                "text": str(i),
                "height": dp(56),
                "on_release": lambda x=str(i): self.set_quarter(x),
            } for i in range(1, 5)
        ]
        self.n_quarter = MDDropdownMenu(
            caller=self.ids.n_quarter,
            items=quarters,
            hor_growth="right",
            ver_growth="up",
            width_mult=4,
        )
        self.n_quarter.bind()
        self.more_reports = False

# ===================================================================== #

    def set_course(self, item):
        """Устанавливает предмет из меню выбора."""
        self.ids.course.text = item if item != "Другой (просто пишите название предмета)" else ""
        self.course_menu.dismiss()

# ===================================================================== #

    def switch_focus(self, textfield):
        available_textfields = ['course', 'n_class', 'letter', 'humans', "report_type", 'date', 'curr_humans',
                                "n_quarter", 'i5', 'i4', 'i3', 'i2', 'create_button']
        for j in range(len(available_textfields) - 1):
            if self.ids[available_textfields[j]] == textfield:
                if available_textfields[j] in available_textfields[:3]:
                    self.course_menu.dismiss()
                    self.n_class_menu.dismiss()
                elif available_textfields[j + 1] == "create_button":
                    self.create_report()
                elif available_textfields[j + 1] == "report_type":
                    textfield.focus = False
                    self.report_type.open()
                self.ids[available_textfields[j + 1]].focus = True
                break

# ===================================================================== #

    def set_n_class(self, item):
        """Устанавливает класс и кол-во человек из меню выбора."""
        if item == "":
            self.ids.n_class.text = ""
            self.ids.humans.text = ""
            self.ids.humans.disabled = False
            self.ids.letter.disabled = False
        else:
            tmp = item.split()
            if len(tmp) > 1:
                self.ids.n_class.text = tmp[0]
                self.ids.humans.text = str(self.rm.pull(show_humans=True, n_class=item))
                self.ids.humans.disabled = True
                self.ids.letter.text = tmp[1]
                self.ids.letter.disabled = True
            else:
                self.ids.n_class.text = item
                self.ids.humans.text = str(self.rm.pull(show_humans=True, n_class=item))
                self.ids.humans.disabled = True
                self.ids.letter.text = ""
                self.ids.letter.disabled = True
        self.n_class_menu.dismiss()

# ===================================================================== #

    def on_pre_enter(self, *args):
        """Перед переходом на этот экран этот метод заполняет меню классов и предметов."""
        self.course_menu.items = [
            {
                "viewclass": "MenuListItem",
                "text": str(i),
                "height": dp(56),
                "on_release": lambda x=str(i): self.set_course(x),
            } for i in self.rm.pull(only_courses=True)
        ] + [
            {
                "viewclass": "MenuListItem",
                "text": "Другой (просто пишите название предмета)",
                "height": dp(56),
                "on_release": lambda x=str(): self.set_course(x),
            }
        ]

        self.n_class_menu.items = [
            {
                "viewclass": "MenuListItem",
                "text": str(i),
                "height": dp(56),
                "on_release": lambda x=str(i): self.set_n_class(x),
            } for i in self.rm.pull(only_classes=True)
        ] + [
            {
                "viewclass": "MenuListItem",
                "text": "Другой (просто пишите номер класса)",
                "height": dp(56),
                "on_release": lambda x=str(): self.set_n_class(x),
            }
        ]

# ===================================================================== #

    def set_report_type(self, item):
        """Устанавливает тип отчёта."""
        self.ids.report_type.set_item(item if len(item) > 1 else (
            "Контрольная работа" if item == "r" else (
                "Четверть" if item == "x" else "Год")))
        if item == "Контрольная работа" or item == "r":
            self.ids.tests.disabled = False
            self.ids.quarters.disabled = True
        elif item == "Четверть" or item == "x":
            self.ids.quarters.disabled = False
            self.ids.tests.disabled = True
        elif item == "Год" or item == "u":
            self.ids.tests.disabled = True
            self.ids.quarters.disabled = True
        self.report_type.dismiss()

# ===================================================================== #

    def set_quarter(self, item):
        """Устанавливает номер четверти."""
        self.ids.n_quarter.set_item(item)
        self.n_quarter.dismiss()

# ===================================================================== #

    def on_save(self, instance, value, date_range):
        """Сохраняет выбранную дату и отображает на экране."""
        date_test = ".".join(str(value).split("-")[::-1])
        self.ids.date_label.text = "Дата:    " + f"[size=18][i]{date_test}[/i][/size]"

# ===================================================================== #

    def on_cancel(self, instance, value, date_range=0):
        """Вызывается при отмене выбора пользователем. Существует как заглушка классу DatePicker, который требует его
        для своей работы."""
        pass

# ===================================================================== #

    def show_date_picker(self):
        """Вызывается кнопкой выбора даты и показывает DatePicker."""
        setlocale(LC_ALL, "ru_RU")
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()

# ===================================================================== #

    def valid_field(self, name, only_digits=False, force_warning=False, optional=False):
        """Проверяет instance_textfield, изменяет его и сопутствующий с ним label
         и выдаёт True, если поле заполнено правильно."""
        def set_success_status():
            """По сути, добавляет зелёную галочку к лейблу."""
            instance_textfield.line_color_normal = (0, 0, 0, 1)
            instance_textfield.line_color_focus = (0, 0, 0, 1)
            instance_textfield.helper_text = ""
            instance_textfield.helper_text_mode = "persistent"

            label.color = (0, 0, 0, 1)
            label.text = "[color=#4caf50][font=segemj]✔️[/font][/color]  " + name_field

        def set_failure_status(helper_text="Это поле обязательно!", warning=False):
            """По сути, добавляет красный крестик или восклицательный знак к лейблу."""
            instance_textfield.line_color_normal = (1, 0, 0, 1)
            instance_textfield.line_color_focus = (1, 0, 0, 1)
            instance_textfield.helper_text = helper_text
            instance_textfield.helper_text_mode = "persistent"

            label.color = (1, 0, 0, 1)
            label.text = f"[font=segemj]{'❗' if warning else '❌'}[/font]  " + name_field

        instance_textfield = self.ids[name]
        label = self.ids[name + "_label"]
        name_field = label.text.split("  ")[-1]
        if force_warning:
            """||||||||| ВЫСТАВИТЬ ФЛАГ ПРЕДУПРЕЖДЕНИЯ |||||||||"""
            set_failure_status(warning=True)
            return False
        if optional:
            """||||||||| ОПЦИОНАЛЬНО |||||||||"""
            set_success_status()
            return True
        if instance_textfield.text != "":
            if only_digits:
                """||||||||| ЦИФРЫ ДОЛЖНЫ БЫТЬ |||||||||"""
                if instance_textfield.text.isdigit():
                    """||||||||| Цифры написаны |||||||||"""
                    set_success_status()
                    return True
                else:
                    """||||||||| ЦИФРЫ НЕ НАПИСАНЫ |||||||||"""
                    set_failure_status("Пожалуйста, заполните правильно это поле!")
                    return False
            else:
                """||||||||| ЦИФР НЕ ДОЛЖНО БЫТЬ, НО ЧТО-ТО НАПИСАНО БЫТЬ ДОЛЖНО |||||||||"""
                set_success_status()
                return True
        else:
            """||||||||| НИЧЕГО НЕ НАПИСАНО |||||||||"""
            set_failure_status()
            return False

# ===================================================================== #

    def create_error_snackbar(self, text):
        """Создаёт снэкбар с содержанием ошибки и отображает его на экран."""
        error_snackbar = Snackbar(
            text=text,
            snackbar_x="10dp",
            snackbar_y="10dp",
        )
        error_snackbar.size_hint_x = (1024 - (error_snackbar.snackbar_x * 2)) / 1024
        error_snackbar.open()

# ===================================================================== #

    def get_checklist(self):
        """Возвращает чеклист на основе ввода пользователя."""
        checklist = {}
        """Не зря это чеклист: в эту переменную мы кладём все возвращаемые значения valid_field. 
        Если хоть одно значение будет ложным, мы не создадим отчёт"""

        """||||||||| ПРОВЕРКА ПРЕДМЕТА |||||||||"""
        checklist["course"] = self.valid_field("course")

        """||||||||| ПРОВЕРКА КЛАССА |||||||||"""
        checklist["n_class"] = self.valid_field("n_class", only_digits=True)

        """||||||||| ПРОВЕРКА ЛИТЕРЫ |||||||||"""
        checklist["letter"] = self.valid_field("letter", optional=True)

        """||||||||| ПРОВЕРКА КОЛ-ВА ЧЕЛОВЕК |||||||||"""
        checklist["humans"] = self.valid_field("humans", only_digits=True)
        if self.ids.humans.text != "":
            humans = int(self.ids.humans.text)
        else:
            humans = 0
        """||||||||| ПРОВЕРКА ТИПА ОТЧЁТА |||||||||"""
        report_type = self.ids.report_type.current_item
        if report_type == "Контрольная работа":
            """|>|>|>|>| ВЕТКА КОНТРОЛЬНЫХ РАБОТ |>|>|>|>|"""
            self.ids.report_type_label.color = (0, 0, 0, 1)
            self.ids.report_type_label.text = "[color=#4caf50][font=segemj]✔️[/font][/color]  " + "Тип отчёта:"
            checklist["report_type"] = True

            """||||||||| ПРОВЕРКА ДАТЫ КР |||||||||"""
            if len(self.ids.date_label.text.split("[i]")) > 1:
                date = str(self.ids.date_label.text).split("[i]")[1].split("[/i]")[0]
                """Дата КР у нас лежит в лейбле, так что нужно её оттуда достать"""
                self.ids.date_label.color = (0, 0, 0, 1)
                self.ids.date_label.text = "[color=#4caf50][font=segemj]✔️[/font][/color]  " + \
                                           "Дата:    " + f"[size=18][i]{date}[/i][/size]"
                checklist["date"] = True
            else:
                self.ids.date_label.color = (1, 0, 0, 1)
                self.ids.date_label.text = "[font=segemj]❌[/font]  " + "Дата:"
                checklist["date"] = False

            """||||||||| ПРОВЕРКА КОЛ-ВА ЧЕЛОВЕК НА КР |||||||||"""
            checklist["curr_humans"] = self.valid_field("curr_humans", only_digits=True)
            if self.ids.curr_humans.text != "":
                curr_humans = int(self.ids.curr_humans.text)
            else:
                curr_humans = 0

            """||||||||| ПРОВЕРКА НА РАЗНИЦУ МЕЖДУ ТЕКУЩИМ И ОБЩИМ КОЛ-ВОМ ЧЕЛОВЕК |||||||||"""
            if curr_humans > humans:
                self.create_error_snackbar("Ошибка: человек на контрольной работе больше, чем есть в классе!")
                checklist["curr_humans"] = self.valid_field("curr_humans", force_warning=True)
                checklist["humans"] = self.valid_field("humans", force_warning=True)

            """||||||||| ПРОВЕРКА ОЦЕНОК |||||||||"""
            checklist["e"] = [self.valid_field("i"+str(i), only_digits=True) for i in range(2, 6)]
            checklist["e"] = all(checklist["e"])
            if checklist["e"]:
                e = dict(zip([2, 3, 4, 5], [int(self.ids["i"+str(i)].text) for i in range(2, 6)]))

                """||||||||| ПРОВЕРКА НА РАЗНИЦУ МЕЖДУ КОЛ-ВОМ ОЦЕНОК И ТЕКУЩИМ КОЛ-ВОМ ЧЕЛОВЕК |||||||||"""
                if sum(e.values()) < curr_humans or sum(e.values()) > curr_humans:
                    self.create_error_snackbar(
                        f"Ошибка: количество оценок {'выше' if sum(e.values()) > curr_humans else 'ниже'}, чем количество человек на контрольной работе!")
                    checklist["curr_humans"] = self.valid_field("curr_humans", force_warning=True)
                    checklist["e"] = [self.valid_field("i"+str(i), only_digits=True,
                                                       force_warning=True) for i in range(2, 6)]
            """<|<|<|<|| КОНЕЦ ВЕТКИ КОНТРОЛЬНЫХ РАБОТ <|<|<|<||"""
        elif report_type == "Четверть" or report_type == "Год":
            """|>|>|>|>| ВЕТКА ДЛЯ ЧЕТВЕРТЕЙ И ГОДА |>|>|>|>|"""
            self.ids.report_type_label.color = (0, 0, 0, 1)
            self.ids.report_type_label.text = "[color=#4caf50][font=segemj]✔️[/font][/color]  " + "Тип отчёта:"
            checklist["report_type"] = True

            """||||||||| ПРОВЕРКА ЧЕТВЕРТИ (ПРИ УСЛОВИИ, ЕСЛИ ЭТО НЕ ГОД) |||||||||"""
            if report_type != "Год":
                if self.ids.n_quarter.current_item != "":
                    quarter = int(self.ids.n_quarter.current_item)
                else:
                    quarter = 0
                if quarter in [1, 2, 3, 4]:
                    self.ids.n_quarter_label.color = (0, 0, 0, 1)
                    self.ids.n_quarter_label.text = "[color=#4caf50][font=segemj]✔️[/font][/color]  " + "Четверть:"
                    checklist["n_quarter"] = True
                else:
                    self.ids.n_quarter_label.color = (1, 0, 0, 1)
                    self.ids.n_quarter_label.text = "[font=segemj]❌[/font]  " + "Четверть:"
                    checklist["n_quarter"] = False

            """||||||||| ПРОВЕРКА ОЦЕНОК |||||||||"""
            checklist["e"] = [self.valid_field("i"+str(i), only_digits=True) for i in range(2, 6)]
            checklist["e"] = all(checklist["e"])
            if checklist["e"]:
                e = dict(zip([2, 3, 4, 5], [int(self.ids["i"+str(i)].text) for i in range(2, 6)]))
                """||||||||| ПРОВЕРКА НА РАЗНИЦУ МЕЖДУ КОЛ-ВОМ ОЦЕНОК И КОЛ_ВОМ ЧЕЛОВЕК |||||||||"""
                if sum(e.values()) != humans:
                    self.create_error_snackbar(
                        f"Ошибка: количество оценок {'выше' if sum(e.values()) > humans else 'ниже'}, чем количество человек в классе!")
                    checklist["humans"] = self.valid_field("humans", force_warning=True)
                    checklist["e"] = [self.valid_field("i"+str(i), only_digits=True,
                                                       force_warning=True) for i in range(2, 6)]
            """<|<|<|<|| КОНЕЦ ВЕТКИ ЧЕТВЕРТЕЙ И ГОДА <|<|<|<||"""
        else:
            """|>|>|>|>| ВЕТКА ПУСТОГО ЗНАЧЕНИЯ |>|>|>|>|"""
            self.ids.report_type_label.color = (1, 0, 0, 1)
            self.ids.report_type_label.text = "[font=segemj]❌[/font]  " + "Тип отчёта:"
            checklist["report_type"] = False
            """<|<|<|<|| КОНЕЦ ВЕТКИ ПУСТОГО ЗНАЧЕНИЯ <|<|<|<||"""

        return checklist

# ===================================================================== #

    def set_default_values(self):
        """Выставляет пустые значения для всех полей."""
        self.ids.course.text = ""
        self.ids.course_label.text = "Предмет:"

        self.ids.n_class.text = ""
        self.ids.n_class_label.text = "Класс:"

        self.ids.letter.text = ""
        self.ids.letter_label.text = "Литера:"
        self.ids.letter.disabled = False

        self.ids.humans.text = ""
        self.ids.humans_label.text = "Количество человек:"
        self.ids.humans.disabled = False

        self.ids.report_type.set_item("Выберете тип отчёта")
        self.ids.report_type_label.text = "Тип отчёта:"

        self.ids.date_label.text = "Дата:"

        self.ids.curr_humans.text = ""
        self.ids.curr_humans_label.text = "Сколько человек было на контрольной работе:"

        self.ids.n_quarter.set_item("Выберете четверть")
        self.ids.n_quarter_label.text = "Четверть:"

        for i in range(2, 6):
            self.ids["i"+str(i)].text = ""
            self.ids["i"+str(i) + "_label"].text = str(i) + ":"

        self.ids.quarters.disabled = True
        self.ids.tests.disabled = True

        self.ids.perf.text = ""
        self.ids.qual.text = ""
        self.ids.aver.text = ""
        self.ids.sok.text = ""

# ===================================================================== #

    def create_report(self, *args):
        """Создаёт новый отчёт."""
        if self.more_reports:
            self.set_default_values()
            self.display_success_widget(show=False)
            self.ids.create_button.text = "Создать"
            self.ids.create_button.icon = "creation"
            self.more_reports = False
            return
        if all(self.get_checklist().values()):
            if self.ids.report_type.current_item == "Контрольная работа":
                result_of_operation = self.rm.push(
                    course=self.ids.course.text,
                    n_class=(self.ids.n_class.text + " " + self.ids.letter.text).rstrip(),
                    humans=int(self.ids.humans.text),
                    report_type=self.ids.report_type.current_item,
                    date=self.ids.date_label.text.split("[i]")[1].split("[/i]")[0],
                    curr_humans=int(self.ids.curr_humans.text),
                    e=dict(zip([2, 3, 4, 5], [int(self.ids["i"+str(i)].text) for i in range(2, 6)]))
                )
            else:
                result_of_operation = self.rm.push(
                    course=self.ids.course.text,
                    n_class=(self.ids.n_class.text + " " + self.ids.letter.text).rstrip(),
                    humans=int(self.ids.humans.text),
                    report_type=self.ids.report_type.current_item,
                    n_quarter=(self.ids.n_quarter.current_item
                               if self.ids.report_type.current_item == "Четверть" else "Г"),
                    e=dict(zip([2, 3, 4, 5], [int(self.ids["i"+str(i)].text) for i in range(2, 6)]))
                )

            print(result_of_operation)
            if result_of_operation == " [v] SUCCESSFUL PUSHING":
                last_report = self.rm.pull(last_report=True)
                self.ids.perf.text = last_report.statistics["Успеваемость"]
                self.ids.qual.text = last_report.statistics["Качество"]
                self.ids.aver.text = str(last_report.statistics["Средний балл"])
                self.ids.sok.text = last_report.statistics["СОК"]
                self.ids.create_button.text = "Создать ещё"
                self.ids.create_button.icon = "timeline-plus"
                self.more_reports = True
                self.display_success_widget()
            else:
                self.create_error_snackbar("Извините, но отчёт уже существует или неправильно заполнен!")
                self.set_default_values()

# ===================================================================== #

    def display_success_widget(self, show=True):
        anim = Animation(x=int(-1280//6 if show else 0), duration=.5, t="out_circ")
        anim.start(self.ids.main_layout)
        anim2 = Animation(opacity=(1 if show else 0), duration=.5, t="out_circ")
        anim2.start(self.ids.success)

# ===================================================================== #

    def on_leave(self, *args):
        self.set_default_values()
        self.display_success_widget(show=False)
