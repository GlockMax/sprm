import json, os
from reportmaker import ReportMaker
import glob


# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


class Report:
    """Класс отчёта."""
    __slots__ = ("index", "course", "n_class", "humans", "report_type", "date",
                 "curr_humans", "n_quarter", "e", "statistics", "no_stats", "from_str")

    def __init__(self, kwargs, from_str=False):
        if not from_str:
            self.index = kwargs["index"]
            self.course = kwargs["course"]
            self.n_class = kwargs["n_class"]
            self.humans = kwargs["humans"]
            self.report_type = kwargs["report_type"]
            if self.report_type == "Контрольная работа":
                self.date = kwargs["date"]
                self.curr_humans = kwargs["curr_humans"]
                self.n_quarter = "-"
            else:
                self.n_quarter = kwargs["n_quarter"]
                self.date = "-"
                self.curr_humans = "-"
            self.e = kwargs["e"]
            self.statistics = kwargs["statistics"]
        else:
            self.e = {}
            self.index, self.course, self.n_class, self.humans, self.report_type = kwargs[:5]
            print(kwargs[-4:12])
            if self.report_type == "Контрольная работа" or self.report_type == "КР":
                self.date = kwargs[-7]
                self.curr_humans = kwargs[-6]
                self.n_quarter = kwargs[-5]
                self.e = dict(zip(["2", "3", "4", "5"], kwargs[-4:12][::-1]))
            elif self.report_type == "Четверть" or self.report_type == "Ч":
                self.n_quarter = kwargs[-5]
                self.date = kwargs[-7]
                self.curr_humans = kwargs[-6]
            self.statistics = "-"

# ===================================================================== #

    def to_list(self, no_stats=False, split_stats=False, split_e=True, all_params=True, order=-1, short_type=False):
        """Преобразует отчёт в список."""
        return ([self.index, self.course, self.n_class, self.humans,
                 (self.report_type[0]+self.n_quarter if self.report_type == "Четверть" or self.report_type == "Год"
                  else "КР") if short_type else self.report_type, self.date, self.curr_humans] +
                ([self.e["5"], self.e["4"], self.e["3"], self.e["2"]][::order] if split_e else [self.e]) + (
            [] if no_stats else (
                [self.statistics["Успеваемость"], self.statistics["Качество"],
                 self.statistics["Средний балл"], self.statistics["СОК"]] if split_stats else [self.statistics]))
                ) if all_params else (
                ([self.index, self.course, self.n_class, self.humans,
                  (self.report_type[0]+self.n_quarter if self.report_type == "Четверть" or self.report_type == "Год"
                   else "КР") if short_type else self.report_type, self.date, self.curr_humans]
                 if self.report_type == "Контрольная работа" else
                 [self.index, self.course, self.n_class, self.humans,
                  (self.report_type[0]+self.n_quarter if self.report_type == "Четверть" or self.report_type == "Год"
                   else "КР") if short_type else self.report_type, self.n_quarter]) +
                ([self.e["5"], self.e["4"], self.e["3"], self.e["2"]][::order]
                 if split_e else [self.e]) +
                ([] if no_stats else
                 ([self.statistics["Успеваемость"], self.statistics["Качество"],
                   self.statistics["Средний балл"], self.statistics["СОК"]] if split_stats else [self.statistics])))

# ===================================================================== #

    def to_dict(self):
        """Преобразует отчёт в словарь."""
        return dict(zip(
            ["index", "course", "n_class", "humans", "report_type", "date", "curr_humans", "e", "statistics"],
            self.to_list(split_e=False, all_params=False))) if self.report_type == "Контрольная работа" else (
            dict(zip(["index", "course", "n_class", "humans", "report_type", "n_quarter", "e", "statistics"],
                     self.to_list(split_e=False, all_params=False))))


# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


class ReportsManager:
    """Класс менеджера отчётов."""
    def __init__(self, teacher=""):
        self.teacher = teacher
        self.maker = ReportMaker()

        if self.teacher != "":
            self.__create()
            self.maker = ReportMaker(self.teacher + ".json")

# ===================================================================== #

    def set_teacher(self, teacher):
        """Метод для задания учителя 'задним числом'.
        Использовать только тогда, когда учителя нужно задать позже создания менеджера."""
        self.teacher = teacher
        self.maker = ReportMaker(self.teacher + ".json")
        self.__create()

# ===================================================================== #

    @staticmethod
    def get_teacher(last=False):
        """Получить имеющихся учителя. Параметр last определяет выдачу последнего учителя """
        files = glob.glob("*.json")
        if files:
            return max(files, key=os.path.getctime).split(".")[0] if last else [i.split(".")[0] for i in files]
        return []

# ===================================================================== #

    @staticmethod
    def is_teacher(teacher):
        """Проверить, существует ли такой учитель."""
        return True if (teacher + ".json" in glob.glob("*.json") and ReportMaker(teacher + ".json").take() != []
                        ) else False

# ===================================================================== #

    @staticmethod
    def delete_trash_reports():
        """Удалить пустые бланки отчётов."""
        [os.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)), i)) for i in glob.glob("*.json")
         if ReportMaker(i).take() == []]

# ===================================================================== #

    def __create(self):
        """Внутренний метод для создания файла на имя учителя, куда будут складываться отчёты."""
        if not os.path.isfile(self.teacher + ".json"):
            with open(self.teacher + ".json", "w") as f:
                json.dump(
                    {"teacher": self.teacher, "reports": []}, f)

# ===================================================================== #

    def len(self):
        """Сколько отчётов у менеджера на руках в данный момент."""
        return len(self.pull())

# ===================================================================== #

    def __exist(self, report):
        """Внутренний метод, проверяющий существование отчёта. Я не ебу, как он работает, но он работает."""
        reports = self.maker.take()
        rt = report["report_type"]
        checklist = {}
        """========= Чеклист здесь отличается от чеклиста в гуе. 
        Здесь мы отмечаем совпадения по тем или иным ключам ========="""
        """========= Первоначально заполним чеклист, не глядя на индекс и статистику ========="""
        for i in reports:
            if i["report_type"] == rt:
                for k in i.keys():
                    if k != "index" and k != "statistics":
                        if i[k] == report[k]:
                            checklist[k] = True
                        else:
                            checklist[k] = False
        if checklist:
            """========= При наличии чеклиста ========="""
            if checklist["course"] and checklist["n_class"]:
                """========= Если совпал предмет и класс... ========="""
                if checklist["humans"]:
                    """========= А эта строчка хз зачем, но если удалить, то программа крашится ========="""
                    return -1
                if rt == "Контрольная работа":
                    """========= ...Отчёт идёт за кр... ========="""
                    if checklist["date"] and (not checklist["e"] or not checklist["curr_humans"]):
                        """========= ...Совпала дата, но не совпали оценки и люди, присутствующие на кр... ========="""
                        return -1
                    elif checklist["date"] and checklist["e"] and checklist["curr_humans"]:
                        """========= ...а если всё совпало ========="""
                        return True
                else:
                    """========= ...А если отчёт за четверть, четверть совпала, но оценки нет... ========="""
                    return -1 if checklist["n_quarter"] and not checklist["e"] else False
            elif not checklist["course"] and checklist["n_class"] and not checklist["humans"]:
                """========= Если не совпал предмет, кол-во человек, но класс совпал ========="""
                return -1
        return False

# ===================================================================== #

    def push(self, **kwargs):
        """Создаёт и 'пихает' новый отчёт в фаил с именем учителя."""
        result_of_operation = self.__exist(kwargs)
        if result_of_operation == -1 or result_of_operation:
            return " [!] ERROR"
        elif not result_of_operation:
            self.maker.make(**kwargs)
            return " [v] SUCCESSFUL PUSHING"

# ===================================================================== #

    def pull(self, last_report=False, only_classes=False, only_courses=False, show_humans=False, n_class=0):
        """'Вытягивает' отчёты из файла. Возвращает массив с Report-объектами, в противном случае, при last_report=True
        выдаёт последний отчёт, а с параметрами only_classes или only_courses
        выдаёт список имеющихся классов и предметов соотвтственно. Чтобы посмотреть кол-во человек в классе,
        выставите show_humans в True и укажите класс в n_class."""
        reports = self.maker.take()
        if show_humans:
            return list(set([Report(i).humans for i in reports if Report(i).n_class == n_class]))[0]
        return (list(set([Report(i).n_class for i in reports])) if only_classes else (
            list(set([Report(i).course for i in reports])) if only_courses else (
                Report(reports[-1]) if last_report else
                list(set([Report(i).humans for i in reports if Report(i).n_class == n_class]))[0]
                if show_humans else[Report(i) for i in reports])))

# ===================================================================== #

    def delete(self, index):
        """Удаляет отчёт ПО ЕГО НОМЕРУ."""
        self.maker.burn(int(index))
        return " [v] SUCCESSFUL DELETION"


# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


if __name__ == "__main__":
    pass
