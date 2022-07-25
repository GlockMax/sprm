from kivy.uix.screenmanager import Screen
from kivy.metrics import dp
from kivy.lang.builder import Builder

from kivymd.uix.menu import MDDropdownMenu

from ui.dropdownmenuitem import MenuListItem


# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


Builder.load_file("ui/menu.kv")


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