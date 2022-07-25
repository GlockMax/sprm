from kivy.uix.screenmanager import Screen
from kivy.metrics import dp
from kivy.lang.builder import Builder

from kivymd.uix.datatables import MDDataTable


# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


Builder.load_file("ui/history.kv")


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
