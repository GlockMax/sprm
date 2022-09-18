import os

from kivy.uix.screenmanager import Screen
from kivy.metrics import dp
from kivy.lang.builder import Builder

from kivymd.uix.datatables import MDDataTable


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

        self.data_tables = MDDataTable(
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
            rows_num=10000,
        )
        self.data_tables.bind(on_check_press=self.on_check_press)
        self.ids.history.add_widget(self.data_tables)

# ===================================================================== #

    def on_pre_enter(self, *args):
        """Вызывается перед переходом на этот экран и обновляет таблицу отчётов."""
        self.update_table()

# ===================================================================== #

    def on_check_press(self, instance_table, current_row):
        """Вызывается, когда нажат чекбокс, и делает видимыми кнопки управления."""
        if self.data_tables.get_row_checks():
            self.ids.delete.disabled = False
            self.ids.print.disabled = False
            self.ids.sjpg.disabled = False
        else:
            self.ids.delete.disabled = True
            self.ids.print.disabled = True
            self.ids.sjpg.disabled = True

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
