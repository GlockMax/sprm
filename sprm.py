from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.config import Config

from kivymd.app import MDApp

from rm import ReportsManager

from ui import MenuScreen, CreateReportScreen, HistoryOfReports, Statistics, ImportReport


# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '720')
Config.set('graphics', 'resizable', '0')
Config.write()

LabelBase.register(name="segemj", fn_regular="fonts/segemj.ttf")

# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


class SprmApp(MDApp):
    """Класс основного приложения."""
    def __init__(self):
        MDApp.__init__(self)
        self.sm = ScreenManager(transition=SlideTransition())
        self.rm = ReportsManager()
        """Менеджер отчётов, привязывающийся только к одному учителю."""

# ===================================================================== #

    def back(self):
        """Метод, возвращающий пользователя на главный экран."""
        self.sm.current = "menu"
        self.sm.transition.direction = "right"

# ===================================================================== #

    def build(self):
        """'Постройка' нашего приложения"""
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_palette = "Teal"
        self.theme_cls.primary_hue = "50"
        self.theme_cls.accent_hue = "100"
        self.sm.add_widget(MenuScreen(name="menu", rm=self.rm))
        self.sm.add_widget(CreateReportScreen(name="create_report", rm=self.rm, tc=self.theme_cls))
        self.sm.add_widget(HistoryOfReports(name="history", rm=self.rm))
        self.sm.add_widget(Statistics(name="stats"))
        return self.sm

# ===================================================================== #

    def on_stop(self):
        """По выходу из приложения удаляет мусорные отчёты."""
        self.rm.delete_trash_reports()


# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


if __name__ == '__main__':
    app = SprmApp()
    app.run()
