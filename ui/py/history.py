import os
import inspect

from kivy.uix.screenmanager import Screen
from kivy.metrics import dp
from kivy.lang.builder import Builder
from kivy.clock import Clock

from kivymd.uix.datatables import MDDataTable
from kivymd.uix.snackbar import Snackbar

from .table import Table


# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


Builder.load_file(os.path.join(os.path.dirname(os.path.dirname(__file__)), "kv", "history.kv"))


# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


class HistoryOfReports(Screen):
    """Экран архива отчётов. Недоступен, если не существует ни одного отчёта (что логично)."""
    def __init__(self, rm, **kwargs):
        super().__init__(**kwargs)

        self.rm = rm
        self.table = Table(
            table_header=["№", "Предмет", "Класс", "Кол-во человек", "За", "Дата", "Человек\nна КР",
                          "5", "4", "3", "2", "У", "К", "СрБ", "СОК"]
        )
        self.ids.history.add_widget(self.table)

# ===================================================================== #

    def on_pre_enter(self, *args):
        """Вызывается перед переходом на этот экран и обновляет таблицу отчётов."""
        self.update_table()

# ===================================================================== #

    def update_table(self):
        """Обновляет таблицу"""
        pull = self.rm.pull()
        self.table.set_table_content(
            [i.to_list(no_stats=False, split_stats=True, order=1, short_type=True) for i in pull])

# ===================================================================== #

    def delete_report(self):
        """Удаляет выбранные отчёты."""
        if not self.table.get_marked():
            es = Snackbar(
                text="Не выбрано ни одного отчёта для удаления!", snackbar_x="10dp",
                snackbar_y="10dp", size_hint_x=.5, radius=[2, 2, 2, 2]
            )
            es.theme_cls.material_style = "M3"
            es.bg_color = "grey"
            es.style = "elevated"
            es.line_color = (0, 0, 0, 1)
            es.shadow_softness = 14
            es.shadow_offset = 0, 0
            es.open()
            return
        for i in sorted(self.table.get_marked(), reverse=True):
            print(self.rm.delete(i))
            self.table.remove_marked()
            self.table.change_indexes()

# ===================================================================== #

    def print_report(self):
        """Выводит на печать выбранные отчёты."""
        pass

# ===================================================================== #

    def save_in_jpeg(self):
        """Сохраняет в джипег выбранные отчёты."""
        pass

# ===================================================================== #
