from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.config import Config
from kivy.animation import Animation

from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import OneLineListItem
from kivymd.uix.picker import MDDatePicker
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.datatables import MDDataTable

from reportsmanager import ReportsManager

import locale


# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #

Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '720')
Config.set('graphics', 'resizable', '0')
Config.write()

# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


class MenuScreen(Screen):
    """Класс основного экрана приложения."""
    def __init__(self, rm, **kwargs):
        super().__init__(**kwargs)
        self.rm = rm
        self.teacher_menu = MDDropdownMenu(
            caller=self.ids.teacher,
            items=[],
            position="bottom",
            width_mult=6
        )
        self.teacher_menu.bind()
        last_teacher = rm.get_teacher(last=True)
        if last_teacher:
            self.set_teacher(last_teacher)
        self.ids.teacher.bind(
            on_text_validate=self.save_teacher,
        )

# ===================================================================== #

    def save_teacher(self, instance_textfield=None):
        """Инициализируем менеджера до конца для нового учителя и разблокируем кнопки управления."""
        if instance_textfield.text != "":
            if len(instance_textfield.text.split()) == 3:
                self.rm.set_teacher(instance_textfield.text)
                instance_textfield.error = False
                instance_textfield.helper_text = ""
                instance_textfield.helper_text_mode = "none"
                self.ids.nav_button.disabled = False
                if self.rm.is_teacher(instance_textfield.text):
                    self.ids.history_button.disabled = False
                    self.ids.stats_button.disabled = False
                else:
                    self.ids.history_button.disabled = True
                    self.ids.stats_button.disabled = True
            else:
                self.ids.nav_button.disabled = True
                instance_textfield.error = True
                instance_textfield.helper_text = "Пожалуйста, заполните правильно это поле!"
        else:
            self.ids.nav_button.disabled = True
            instance_textfield.error = True
            instance_textfield.helper_text = "Это поле обязательно!"
        self.teacher_menu.dismiss()

# ===================================================================== #

    def set_teacher(self, teacher):
        """Устанавливаем уже существующего менеджера на выбранного учителя."""
        self.ids.teacher.text = teacher
        self.ids.nav_button.disabled = False
        self.rm.set_teacher(teacher)
        self.ids.history_button.disabled = False
        #self.ids.stats_button.disabled = False
        self.teacher_menu.dismiss()

# ===================================================================== #

    def on_pre_enter(self, *args):
        """Перед входом посмотрим, какие у нас есть учителя и есть ли у них отчёты."""
        self.teacher_menu.items = [
            {
                 "viewclass": "MenuListItem",
                 "text": str(i),
                 "height": dp(56),
                 "on_release": lambda x=str(i): self.set_teacher(x),
            } for i in self.rm.get_teacher()
        ] + [
            {
                 "viewclass": "MenuListItem",
                 "text": "Другой (просто пишите свои ФИО)",
                 "height": dp(56),
                 "on_release": lambda x=str(): self.set_teacher(x),
            }
        ]
        if self.rm.get_teacher():
            self.ids.nav_button.disabled = False
            self.ids.history_button.disabled = False
            # self.ids.stats_button.disabled = False


# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


class MenuListItem(OneLineListItem):
    """Шаблон отображения элементов всех менюшек"""


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
        locale.setlocale(locale.LC_ALL, "ru_RU")
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
            instance_textfield.helper_text_mode = "none"

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
            """========= ВЫСТАВИТЬ ФЛАГ ПРЕДУПРЕЖДЕНИЯ ========="""
            set_failure_status(warning=True)
            return False
        if optional:
            """========= ОПЦИОНАЛЬНО ========="""
            set_success_status()
            return True
        if instance_textfield.text != "":
            if only_digits:
                """========= ЦИФРЫ ДОЛЖНЫ БЫТЬ ========="""
                if instance_textfield.text.isdigit():
                    """========= Цифры написаны ========="""
                    set_success_status()
                    return True
                else:
                    """========= ЦИФРЫ НЕ НАПИСАНЫ ========="""
                    set_failure_status("Пожалуйста, заполните правильно это поле!")
                    return False
            else:
                """========= ЦИФР НЕ ДОЛЖНО БЫТЬ, НО ЧТО-ТО НАПИСАНО БЫТЬ ДОЛЖНО ========="""
                set_success_status()
                return True
        else:
            """========= НИЧЕГО НЕ НАПИСАНО ========="""
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
        """========= Не зря это чеклист: в эту переменную мы ложим все возвращаемые значения valid_field. 
        Если хоть одно значение будет ложным, мы не создадим отчёт ========="""

        """========= ПРОВЕРКА ПРЕДМЕТА ========="""
        checklist["course"] = self.valid_field("course")

        """========= ПРОВЕРКА КЛАССА ========="""
        checklist["n_class"] = self.valid_field("n_class", only_digits=True)

        """========= ПРОВЕРКА ЛИТЕРЫ ========="""
        checklist["letter"] = self.valid_field("letter", optional=True)

        """========= ПРОВЕРКА КОЛ-ВА ЧЕЛОВЕК ========="""
        checklist["humans"] = self.valid_field("humans", only_digits=True)
        if self.ids.humans.text != "":
            humans = int(self.ids.humans.text)
        else:
            humans = 0
        """========= ПРОВЕРКА ТИПА ОТЧЁТА ========="""
        report_type = self.ids.report_type.current_item
        if report_type == "Контрольная работа":
            """>>>>>>>>> ВЕТКА КОНТРОЛЬНЫХ РАБОТ >>>>>>>>>"""
            self.ids.report_type_label.color = (0, 0, 0, 1)
            self.ids.report_type_label.text = "[color=#4caf50][font=segemj]✔️[/font][/color]  " + "Тип отчёта:"
            checklist["report_type"] = True

            """========= ПРОВЕРКА ДАТЫ КР ========="""
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

            """========= ПРОВЕРКА КОЛ-ВА ЧЕЛОВЕК НА КР ========="""
            checklist["curr_humans"] = self.valid_field("curr_humans", only_digits=True)
            if self.ids.curr_humans.text != "":
                curr_humans = int(self.ids.curr_humans.text)
            else:
                curr_humans = 0

            """========= ПРОВЕРКА НА РАЗНИЦУ МЕЖДУ ТЕКУЩИМ И ОБЩИМ КОЛ-ВОМ ЧЕЛОВЕК ========="""
            if curr_humans > humans:
                self.create_error_snackbar("Ошибка: человек на контрольной работе больше, чем есть в классе!")
                checklist["curr_humans"] = self.valid_field("curr_humans", force_warning=True)
                checklist["humans"] = self.valid_field("humans", force_warning=True)

            """========= ПРОВЕРКА ОЦЕНОК ========="""
            checklist["e"] = [self.valid_field("i"+str(i), only_digits=True) for i in range(2, 6)]
            checklist["e"] = all(checklist["e"])
            if checklist["e"]:
                e = dict(zip([2, 3, 4, 5], [int(self.ids["i"+str(i)].text) for i in range(2, 6)]))

                """========= ПРОВЕРКА НА РАЗНИЦУ МЕЖДУ КОЛ-ВОМ ОЦЕНОК И ТЕКУЩИМ КОЛ-ВОМ ЧЕЛОВЕК ========="""
                if sum(e.values()) < curr_humans or sum(e.values()) > curr_humans:
                    self.create_error_snackbar(
                        f"Ошибка: количество оценок {'выше' if sum(e.values()) > curr_humans else 'ниже'}, чем количество человек на контрольной работе!")
                    checklist["curr_humans"] = self.valid_field("curr_humans", force_warning=True)
                    checklist["e"] = [self.valid_field("i"+str(i), only_digits=True,
                                                       force_warning=True) for i in range(2, 6)]
            """<<<<<<<<< КОНЕЦ ВЕТКИ КОНТРОЛЬНЫХ РАБОТ <<<<<<<<<"""
        elif report_type == "Четверть" or report_type == "Год":
            """>>>>>>>>> ВЕТКА ДЛЯ ЧЕТВЕРТЕЙ И ГОДА >>>>>>>>>"""
            self.ids.report_type_label.color = (0, 0, 0, 1)
            self.ids.report_type_label.text = "[color=#4caf50][font=segemj]✔️[/font][/color]  " + "Тип отчёта:"
            checklist["report_type"] = True

            """========= ПРОВЕРКА ЧЕТВЕРТИ (ПРИ УСЛОВИИ, ЕСЛИ ЭТО НЕ ГОД) ========="""
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

            """========= ПРОВЕРКА ОЦЕНОК ========="""
            checklist["e"] = [self.valid_field("i"+str(i), only_digits=True) for i in range(2, 6)]
            checklist["e"] = all(checklist["e"])
            if checklist["e"]:
                e = dict(zip([2, 3, 4, 5], [int(self.ids["i"+str(i)].text) for i in range(2, 6)]))
                """========= ПРОВЕРКА НА РАЗНИЦУ МЕЖДУ КОЛ-ВОМ ОЦЕНОК И КОЛ_ВОМ ЧЕЛОВЕК ========="""
                if sum(e.values()) != humans:
                    self.create_error_snackbar(
                        f"Ошибка: количество оценок {'выше' if sum(e.values()) > humans else 'ниже'}, чем количество человек в классе!")
                    checklist["humans"] = self.valid_field("humans", force_warning=True)
                    checklist["e"] = [self.valid_field("i"+str(i), only_digits=True,
                                                       force_warning=True) for i in range(2, 6)]
            """<<<<<<<<< КОНЕЦ ВЕТКИ ЧЕТВЕРТЕЙ И ГОДА <<<<<<<<<"""
        else:
            """>>>>>>>>> ВЕТКА ПУСТОГО ЗНАЧЕНИЯ >>>>>>>>>"""
            self.ids.report_type_label.color = (1, 0, 0, 1)
            self.ids.report_type_label.text = "[font=segemj]❌[/font]  " + "Тип отчёта:"
            checklist["report_type"] = False
            """<<<<<<<<< КОНЕЦ ВЕТКИ ПУСТОГО ЗНАЧЕНИЯ <<<<<<<<<"""

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


# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


class ReportTable(MDDataTable):
    """Класс для таблицы отчётов. Наследуется от MDDataTable и ничем примечательным не отличается, кроме включения и
    отключения кнопок удаления, печати и сохранения в джипег."""
    def __init__(self, sc, **kwargs):
        super().__init__(**kwargs)
        self.sc = sc

# ===================================================================== #

    def on_check_press(self, a):
        """Вызывается, когда нажат чекбокс, и делает видимыми кнопки управления."""
        if self.get_row_checks():
            self.sc.ids.delete.disabled = False
            self.sc.ids.print.disabled = False
            self.sc.ids.sjpg.disabled = False
        else:
            self.sc.ids.delete.disabled = True
            self.sc.ids.print.disabled = True
            self.sc.ids.sjpg.disabled = True


# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


class HistoryOfReports(Screen):
    """Экран архива отчётов. Недоступен, если не существует ни одного отчёта (что логично)."""
    def __init__(self, rm, **kwargs):
        super().__init__(**kwargs)

        self.rm = rm

        self.data_tables = ReportTable(
            check=True,
            column_data=[
                ("[size=14]№[/size]", dp(20)),
                ("[size=14]Предмет[/size]", dp(37)),
                ("[size=14]Класс[/size]", dp(13)),
                ("[size=14]Кол-во человек[/size]", dp(15)),
                ("[size=14]За[/size]", dp(9)),
                ("[size=14]Дата[/size]", dp(20)),
                ("[size=14]Человек\n  на К/Р[/size]", dp(17)),
                ("[size=14]5[/size]", dp(9)),
                ("[size=14]4[/size]", dp(9)),
                ("[size=14]3[/size]", dp(9)),
                ("[size=14]2[/size]", dp(9)),
                ("[size=14]Усп-сть[/size]", dp(16)),
                ("[size=14]Качество[/size]", dp(16)),
                ("[size=14]Ср. балл[/size]", dp(16)),
                ("[size=14]СОК[/size]", dp(16)),
            ],
            elevation=2,
            sc=self,
            rows_num=10000,
        )
        self.ids.history.add_widget(self.data_tables)

# ===================================================================== #

    def on_pre_enter(self, *args):
        """Вызывается перед переходом на этот экран и обновляет таблицу отчётов."""
        self.update_table()

# ===================================================================== #

    def update_table(self):
        """Обновляет таблицу"""
        pull = self.rm.pull()
        self.data_tables.row_data = (
            [i.to_list(no_stats=False, split_stats=True, order=1, short_type=True) for i in pull] if len(pull) > 1 else
            ([pull[0].to_list(no_stats=False, split_stats=True, order=1, short_type=True), ["-" for i in range(15)]]
                if len(pull) == 1 else [["-" for i in range(15)], ["-" for i in range(15)]]))

# ===================================================================== #

    def delete_report(self):
        """Удаляет выбранные отчёты."""
        print(*[self.rm.delete(i[0]) for i in self.data_tables.get_row_checks()], sep="\n")
        self.update_table()

# ===================================================================== #

    def print_report(self):
        """Выводит на печать выбранные отчёты."""

# ===================================================================== #

    def save_in_jpeg(self):
        """Сохраняет в джипег выбранные отчёты."""


# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


class ImportReport(Screen):
    pass


# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


class Statistics(Screen):
    pass


# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


class SprmApp(MDApp):
    """Класс основного приложения."""
    def __init__(self):
        MDApp.__init__(self)
        self.sm = ScreenManager(transition=SlideTransition())
        self.rm = ReportsManager()
        """========= Мы пока не пишем имя учителя, ибо оно будет известно только в MenuScreen ========="""

# ===================================================================== #

    def back(self):
        """Метод, возвращающий пользователя на главный экран."""
        self.sm.current = "menu"
        self.sm.transition.direction = "right"

# ===================================================================== #

    def build(self):
        """'Постройка' нашего приложения"""
        Window.bind(on_key_down=self.on_keyboard)
        self.sm.add_widget(MenuScreen(name="menu", rm=self.rm))
        self.sm.add_widget(CreateReportScreen(name="create_report", rm=self.rm))
        self.sm.add_widget(HistoryOfReports(name="history", rm=self.rm))
        self.sm.add_widget(ImportReport(name="import"))
        self.sm.add_widget(Statistics(name="stats"))
        #self.sm.add_widget(SuccessScreen(name="success", rm=self.rm))
        return self.sm

# ===================================================================== #

    def on_stop(self):
        """По выходу из приложения удаляет мусорные отчёты."""
        self.rm.delete_trash_reports()

# ===================================================================== #

    def on_keyboard(self, window, key, scancode, codepoint, modifier):
        if codepoint == "r" or codepoint == "x" or codepoint == "u":
            if self.sm.current_screen.name == "create_report" and len(Window.children) > 1:
                if Window.children[0] == self.sm.get_screen("create_report").report_type:
                    self.sm.get_screen("create_report").set_report_type(codepoint)
        if codepoint == "1" or codepoint == "2" or codepoint == "3" or codepoint == "4":
            if self.sm.current_screen.name == "create_report" and len(Window.children) > 1:
                if Window.children[0] == self.sm.get_screen("create_report").n_quarter:
                    self.sm.get_screen("create_report").set_quarter(codepoint)


# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


if __name__ == '__main__':
    app = SprmApp()
    app.run()
