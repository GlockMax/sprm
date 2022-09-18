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
        Window.bind(on_key_down=self.on_keyboard)
        self.sm.add_widget(MenuScreen(name="menu", rm=self.rm))
        self.sm.add_widget(CreateReportScreen(name="create_report", rm=self.rm))
        self.sm.add_widget(HistoryOfReports(name="history", rm=self.rm))
        self.sm.add_widget(ImportReport(name="import"))
        self.sm.add_widget(Statistics(name="stats"))
        return self.sm

# ===================================================================== #

    def on_stop(self):
        """По выходу из приложения удаляет мусорные отчёты."""
        self.rm.delete_trash_reports()

# ===================================================================== #

    # TODO: РЕАЛИЗОВАТЬ ПРОБРОСКУ СОБЫТИЙ С КЛАВИАТУРЫ
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
