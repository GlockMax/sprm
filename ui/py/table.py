import os

from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, ListProperty, StringProperty, BooleanProperty
from kivy.metrics import dp

from kivymd.uix.card import MDCard


# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #

Builder.load_file(os.path.join(os.path.dirname(os.path.dirname(__file__)), "kv", "table.kv"))

# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


class Header(BoxLayout):
    """Ячейка заголовка таблицы"""
    text = StringProperty()
    dps = NumericProperty()
    """Размер ячейки. При dps = 0 у ячейки будет автоматический размер"""

# ===================================================================== #

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.dps:
            self.size_hint_x = None
            self.width = dp(self.dps)


# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


class Cell(BoxLayout):
    """Ячейка таблицы"""
    text = StringProperty()
    dps = NumericProperty()
    """Размер ячейки. При dps = 0 у ячейки будет автоматический размер"""
    with_check = BooleanProperty()
    """Параметр, определяющий ячейку с чекбоксом"""

# ===================================================================== #

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.dps:
            self.size_hint_x = None
            self.width = dp(self.dps)
        if not self.with_check:
            """Если чекбокса не должно быть, удаляем его"""
            self.remove_widget(self.ids.check)


# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


class Table(MDCard):
    """Таблица отчётов"""
    table_header = ListProperty()
    """Заголовок таблицы"""

    table_content = ListProperty()
    """Строки таблицы"""

# ===================================================================== #

    def __init__(self, **kwargs):
        super(Table, self).__init__(**kwargs)

        self.theme_cls.material_style = "M3"

        """Заполняем количество колонок таблицы"""
        self.ids['header'].cols = len(self.table_header)
        self.ids['body'].cols = len(self.table_header)

        """Заполняем заголовок..."""
        for i in range(len(self.table_header)):
            head = Header(text=self.table_header[i],
                          dps=self.get_dp_for_column(i))
            self.ids['header'].add_widget(head)

        """Заполняем строки"""
        self.set_table_content(self.table_content)

        self.__queue = []
        """Список, в котором собираются все отмеченные строки"""

# ===================================================================== #

    def add_row(self, s):
        """Добавить строку в таблицу"""
        for j in range(len(s)):
            body = Cell(text=str(s[j]), dps=self.get_dp_for_column(j), with_check=(j == 0))
            self.ids['body'].add_widget(body)

# ===================================================================== #

    def remove_marked(self):
        """Удалить отмеченные строки из таблицы"""
        for i in range(len(self.ids["body"].children)-1, 13, -15):
            if int(self.ids["body"].children[i].text) in self.__queue:
                for j in range(i, i-15, -1):
                    self.ids["body"].remove_widget(self.ids["body"].children[j])
        self.__queue = []

# ===================================================================== #

    def on_check_active(self, checkbox, value):
        """Метод, заносящий отмеченные строки в очередь"""
        if value:
            self.__queue.append(int(checkbox.parent.text))
        else:
            self.__queue.remove(int(checkbox.parent.text))

# ===================================================================== #

    def set_table_content(self, content):
        """Заполнить таблицу данными"""
        if self.table_content == content:
            return
        self.table_content = content
        for i in range(len(self.ids["body"].children) - 1, 13, -15):
            for j in range(i, i - 15, -1):
                self.ids["body"].remove_widget(self.ids["body"].children[j])
        for i in self.table_content:
            for j in range(len(i)):
                body = Cell(text=str(i[j]), dps=self.get_dp_for_column(j), with_check=(j == 0))
                self.ids['body'].add_widget(body)

# ===================================================================== #

    @staticmethod
    def get_dp_for_column(index):
        """Получить размеры для колонок"""
        target_dps = 0
        if index == 0:
            target_dps = 74
        elif index == 1:
            target_dps = 256
        elif index == 3 or index == 6:
            target_dps = 80
        return target_dps

# ===================================================================== #

    def get_marked(self):
        """Получить отмеченные строки"""
        return self.__queue

# ===================================================================== #

    def change_indexes(self):
        """Поменять индексы из колонки на реальные индексы в файле"""
        for i in range(len(self.ids["body"].children) - 1, 13, -15):
            self.ids["body"].children[i].text = str((len(self.ids["body"].children)+1)//15 - (i+1)//15 + 1)
