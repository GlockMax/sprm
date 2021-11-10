from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.config import Config

from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import OneLineListItem
from kivymd.uix.picker import MDDatePicker
from kivymd.uix.snackbar import Snackbar

from reportsmanager import ReportsManager


# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #

Config.set('graphics', 'width', '1024')
Config.set('graphics', 'height', '768')
Config.set('graphics', 'resizable', '0')
Config.write()

# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


class MenuScreen(Screen):
    def __init__(self, rm, **kwargs):
        super().__init__(**kwargs)
        self.rm = rm
        last_teacher = rm.get_last_teacher()
        if last_teacher != "NOBODY":
            self.set_last_teacher(last_teacher)
        self.ids.teacher.bind(
            on_text_validate=self.save_teacher,
            on_focus=self.save_teacher,
        )

    def save_teacher(self, instance_textfield=None):
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

    def set_last_teacher(self, teacher):
        self.ids.teacher.text = teacher
        self.ids.nav_button.disabled = False
        self.rm.set_teacher(teacher)
        self.ids.history_button.disabled = False
        self.ids.stats_button.disabled = False


# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


class MenuListItem(OneLineListItem):
    pass


# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


class SuccessScreen(Screen):
    pass


# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


class CreateReportScreen(Screen):
    """Экран создания отчёта. Если у учителя уже создан отчёт, старый дополняется новыми данными."""
    def __init__(self, rm, **kwargs):
        super().__init__(**kwargs)

        self.rm = rm

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
            }
        ]
        """Список элеметов для выпадающего меню выбора типа отчёта"""

        self.report_type = MDDropdownMenu(
            caller=self.ids.report_type,
            items=report_menu_items,
            position="center",
            width_mult=4,
        )
        """Выпадающее меню выбора типа отчёта"""
        self.report_type.bind()

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
            position="center",
            width_mult=4,
        )
        """Выпадающее меню выбора четвертей"""
        self.n_quarter.bind()

# ===================================================================== #

    def set_report_type(self, item):
        """Устанавливает тип отчёта."""
        self.ids.report_type.set_item(item)
        if item == "Контрольная работа":
            self.ids.tests.disabled = False
            self.ids.quarters.disabled = True
        else:
            self.ids.quarters.disabled = False
            self.ids.tests.disabled = True
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
        date_dialog = MDDatePicker(language="ru_RU")
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()

# ===================================================================== #

    def valid_field(self, instance_textfield=None, only_digits=False, label=None, force_warning=False):
        """Проверяет instance_textfield, изменяет его и сопутствующий с ним label
         и выдаёт True, если поле заполнено правильно. name_field присутствует для правильного форматирования label."""
        def set_success_status():
            instance_textfield.line_color_normal = (0, 0, 0, 1)
            instance_textfield.line_color_focus = (0, 0, 0, 1)
            instance_textfield.helper_text = ""
            instance_textfield.helper_text_mode = "none"

            label.color = (0, 0, 0, 1)
            label.text = "[color=#4caf50][font=segemj]✔️[/font][/color]  " + name_field

        def set_failure_status(helper_text="Это поле обязательно!", warning=False):
            instance_textfield.line_color_normal = (1, 0, 0, 1)
            instance_textfield.line_color_focus = (1, 0, 0, 1)
            instance_textfield.helper_text = helper_text
            instance_textfield.helper_text_mode = "persistent"

            label.color = (1, 0, 0, 1)
            label.text = f"[font=segemj]{'❗' if warning else '❌'}[/font]  " + name_field

        name_field = label.text.split("  ")[-1]
        if force_warning:
            """ ========= ВЫСТАВИТЬ ФЛАГ ПРЕДУПРЕЖДЕНИЯ ========= """
            set_failure_status(warning=True)
            return False
        if instance_textfield.text != "":
            if only_digits:
                """ ========= ЦИФРЫ ДОЛЖНЫ БЫТЬ ========= """
                if instance_textfield.text.isdigit():
                    """Цифры написаны"""
                    set_success_status()
                    return True
                else:
                    """ ========= ЦИФРЫ НЕ НАПИСАНЫ ========= """
                    set_failure_status("Пожалуйста, заполните правильно это поле!")
                    return False
            else:
                """ ========= ЦИФР НЕ ДОЛЖНО БЫТЬ, НО ЧТО-ТО НАПИСАНО БЫТЬ ДОЛЖНО ========= """
                set_success_status()
                return True
        else:
            """ ========= НИЧЕГО НЕ НАПИСАНО ========= """
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
        """Не зря это чеклист: в эту переменную мы ложим все возвращаемые значения valid_field. 
        Если хоть одно значение будет ложным, мы не создадим отчёт"""

        """ ========= ПРОВЕРКА ПРЕДМЕТА ========= """
        checklist["course"] = self.valid_field(instance_textfield=self.ids.course, label=self.ids.course_label)

        """ ========= ПРОВЕРКА КЛАССА ========= """
        checklist["n_class"] = self.valid_field(instance_textfield=self.ids.n_class, only_digits=True,
                                                label=self.ids.n_class_label)
        """ ========= ПРОВЕРКА КОЛ-ВА ЧЕЛОВЕК ========= """
        checklist["humans"] = self.valid_field(instance_textfield=self.ids.humans, only_digits=True,
                                               label=self.ids.humans_label)
        if self.ids.humans.text != "":
            humans = int(self.ids.humans.text)
        else:
            humans = 0
        """ ========= ПРОВЕРКА ТИПА ОТЧЁТА ========= """
        report_type = self.ids.report_type.current_item
        if report_type == "Контрольная работа":
            """ >>>>>>>>> ВЕТКА КОНТРОЛЬНЫХ РАБОТ >>>>>>>>> """
            self.ids.report_type_label.color = (0, 0, 0, 1)
            self.ids.report_type_label.text = "[color=#4caf50][font=segemj]✔️[/font][/color]  " + "Тип отчёта:"
            checklist["report_type"] = True

            """ ========= ПРОВЕРКА ДАТЫ КР ========= """
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

            """ ========= ПРОВЕРКА КОЛ-ВА ЧЕЛОВЕК НА КР ========= """
            checklist["curr_humans"] = self.valid_field(instance_textfield=self.ids.curr_humans, only_digits=True,
                                                        label=self.ids.curr_humans_label)
            if self.ids.curr_humans.text != "":
                curr_humans = int(self.ids.curr_humans.text)
            else:
                curr_humans = 0

            """ ========= ПРОВЕРКА НА РАЗНИЦУ МЕЖДУ ТЕКУЩИМ И ОБЩИМ КОЛ-ВОМ ЧЕЛОВЕК ========= """
            if curr_humans > humans:
                self.create_error_snackbar("Ошибка: человек на контрольной работе больше, чем есть в классе!")
                checklist["curr_humans"] = self.valid_field(instance_textfield=self.ids.curr_humans,
                                                            label=self.ids.curr_humans_label, force_warning=True)
                checklist["humans"] = self.valid_field(instance_textfield=self.ids.humans,
                                                       label=self.ids.humans_label, force_warning=True)

            """ ========= ПРОВЕРКА ОЦЕНОК ========= """
            checklist["e"] = [self.valid_field(instance_textfield=self.ids[str(i)], only_digits=True,
                                               label=self.ids[str(i) + "_label"]) for i in range(2, 6)]
            checklist["e"] = all(checklist["e"])
            if checklist["e"]:
                e = dict(zip([2, 3, 4, 5], [int(self.ids[str(i)].text) for i in range(2, 6)]))

                """ ========= ПРОВЕРКА НА РАЗНИЦУ МЕЖДУ КОЛ-ВОМ ОЦЕНОК И ТЕКУЩИМ КОЛ-ВОМ ЧЕЛОВЕК ========= """
                if sum(e.values()) != curr_humans:
                    self.create_error_snackbar(
                        f"Ошибка: количество оценок {'выше' if sum(e.values()) > curr_humans else 'ниже'}, чем количество человек на контрольной работе!")
                    checklist["curr_humans"] = self.valid_field(instance_textfield=self.ids.curr_humans,
                                                                label=self.ids.curr_humans_label, force_warning=True)
                    checklist["e"] = [self.valid_field(
                        instance_textfield=self.ids[str(i)], only_digits=True, label=self.ids[str(i) + "_label"],
                        force_warning=True) for i in range(2, 6)]

        elif report_type == "Четверть":
            """ >>>>>>>>> ВЕТКА ДЛЯ ЧЕТВЕРТЕЙ >>>>>>>>> """
            self.ids.report_type_label.color = (0, 0, 0, 1)
            self.ids.report_type_label.text = "[color=#4caf50][font=segemj]✔️[/font][/color]  " + "Тип отчёта:"
            checklist["report_type"] = True

            """ ========= ПРОВЕРКА ЧЕТВЕРТИ ========= """
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

            """ ========= ПРОВЕРКА ОЦЕНОК ========= """
            checklist["e"] = [self.valid_field(instance_textfield=self.ids[str(i)], only_digits=True,
                                               label=self.ids[str(i) + "_label"]) for i in range(2, 6)]
            checklist["e"] = all(checklist["e"])
            if checklist["e"]:
                e = dict(zip([2, 3, 4, 5], [int(self.ids[str(i)].text) for i in range(2, 6)]))
                """ ========= ПРОВЕРКА НА РАЗНИЦУ МЕЖДУ КОЛ-ВОМ ОЦЕНОК И КОЛ_ВОМ ЧЕЛОВЕК ========= """
                if sum(e.values()) != humans:
                    self.create_error_snackbar(
                        f"Ошибка: количество оценок {'выше' if sum(e.values()) > humans else 'ниже'}, чем количество человек в классе!")
                    checklist["humans"] = self.valid_field(instance_textfield=self.ids.humans,
                                                           label=self.ids.humans_label, force_warning=True)
                    checklist["e"] = [self.valid_field(
                        instance_textfield=self.ids[str(i)], only_digits=True, label=self.ids[str(i) + "_label"],
                        force_warning=True) for i in range(2, 6)]

        else:
            """ >>>>>>>>> ВЕТКА ДЛЯ ПУСТОГО ЗНАЧЕНИЯ >>>>>>>>> """
            self.ids.report_type_label.color = (1, 0, 0, 1)
            self.ids.report_type_label.text = "[font=segemj]❌[/font]  " + "Тип отчёта:"
            checklist["report_type"] = False

        return checklist

# ===================================================================== #

    def set_default_values(self):
        self.ids.course.text = ""
        self.ids.course_label.text = "Предмет:"

        self.ids.n_class.text = ""
        self.ids.n_class_label.text = "Класс:"

        self.ids.humans.text = ""
        self.ids.humans_label.text = "Количество человек:"

        self.ids.report_type.set_item("Выберете тип отчёта")
        self.ids.report_type_label.text = "Тип отчёта:"

        self.ids.date_label.text = "Дата:"

        self.ids.curr_humans.text = ""
        self.ids.curr_humans_label.text = "Сколько человек было на контрольной работе:"

        self.ids.n_quarter.set_item("Выберете четверть")
        self.ids.n_quarter_label.text = "Четверть:"

        for i in range(2, 6):
            self.ids[str(i)].text = ""
            self.ids[str(i) + "_label"].text = str(i) + ":"

        self.ids.quarters.disabled = True
        self.ids.tests.disabled = True

# ===================================================================== #

    def create_report(self):
        """Создаёт новый отчёт"""
        if all(self.get_checklist().values()):
            if self.ids.report_type.current_item == "Контрольная работа":
                result_of_operation = self.rm.push(
                    course=self.ids.course.text,
                    n_class=int(self.ids.n_class.text),
                    humans=int(self.ids.humans.text),
                    report_type=self.ids.report_type.current_item,
                    date=self.ids.date_label.text.split("[i]")[1].split("[/i]")[0],
                    curr_humans=int(self.ids.curr_humans.text),
                    e=dict(zip([2, 3, 4, 5], [int(self.ids[str(i)].text) for i in range(2, 6)]))
                )
                print(result_of_operation)
                if result_of_operation == "SUCCESS":
                    self.parent.current = "success"
                    self.parent.transition.direction = "left"
                    self.set_default_values()
                else:
                    self.create_error_snackbar("Извините, но отчёт уже существует или неправильно заполнен!")
                    self.set_default_values()

            else:
                result_of_operation = self.rm.push(
                    course=self.ids.course.text,
                    n_class=int(self.ids.n_class.text),
                    humans=int(self.ids.humans.text),
                    report_type=self.ids.report_type.current_item,
                    n_quarter=self.ids.n_quarter.current_item,
                    e=dict(zip([2, 3, 4, 5], [int(self.ids[str(i)].text) for i in range(2, 6)]))
                )
                print(result_of_operation)
                if result_of_operation == "SUCCESS":
                    self.parent.current = "success"
                    self.parent.transition.direction = "left"
                    self.set_default_values()
                else:
                    self.create_error_snackbar("Извините, но отчёт уже существует или неправильно заполнен!")
                    self.set_default_values()


# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


class HistoryOfReports(Screen):
    """Экран архива отчётов. Недоступен, если не существует ни одного отчёта (что логично)."""
    pass


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

    def back(self):
        """Метод, возвращающий пользователя на главный экран."""
        self.sm.current = "menu"
        self.sm.transition.direction = "right"

    def build(self):
        self.sm.add_widget(MenuScreen(name="menu", rm=self.rm))
        self.sm.add_widget(CreateReportScreen(name="create_report", rm=self.rm))
        self.sm.add_widget(HistoryOfReports(name="history"))
        self.sm.add_widget(ImportReport(name="import"))
        self.sm.add_widget(Statistics(name="stats"))
        self.sm.add_widget(SuccessScreen(name="success"))
        return self.sm

    def on_stop(self):
        self.rm.delete_trash_reports()


# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


if __name__ == '__main__':
    app = SprmApp()
    app.run()