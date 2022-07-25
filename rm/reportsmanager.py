import json
import os
import glob
from rm.reportmaker import ReportMaker
from rm.reporttype import Report


# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


class ReportsManager:
    """Класс менеджера отчётов."""
    def __init__(self, teacher=""):
        self.rpath = os.path.abspath("reports")
        if not os.path.exists(self.rpath):
            os.mkdir(self.rpath)
        if teacher:
            self.set_teacher(teacher)
        else:
            self.teacher = teacher
            self.maker = ReportMaker()

# ===================================================================== #

    def set_teacher(self, teacher):
        """Метод для задания учителя 'задним числом'.
        Использовать только тогда, когда учителя нужно задать позже создания менеджера."""
        self.teacher = teacher
        self.maker = ReportMaker(os.path.join(self.rpath, f"{self.teacher}.json"))
        self.__create()

# ===================================================================== #

    def get_teacher(self, last=False):
        """Получить имеющихся учителей. Параметр last определяет выдачу последнего учителя """
        files = glob.glob(os.path.join(self.rpath, "*.json"))
        return ((
            os.path.basename(max(files, key=os.path.getctime)).split(".")[0]
            if last else [os.path.basename(i).split(".")[0] for i in files]
        ) if files else [])

# ===================================================================== #

    def is_teacher(self, teacher):
        """Проверить, существует ли такой учитель."""
        return True if (f"{self.teacher}.json" in glob.glob(os.path.join(self.rpath, "*.json"))
                        and ReportMaker(os.path.join(self.rpath, f"{self.teacher}.json")).take() != []
                        ) else False

# ===================================================================== #

    def delete_trash_reports(self):
        """Удалить пустые бланки отчётов."""
        [os.remove(os.path.join(self.rpath, i)) for i in glob.glob(os.path.join(self.rpath, "*.json"))
         if ReportMaker(os.path.join(self.rpath, i)).take() == []]

# ===================================================================== #

    def __create(self):
        """Внутренний метод для создания файла на имя учителя, куда будут складываться отчёты."""
        theory_name = os.path.join(self.rpath, f"{self.teacher}.json")
        if not os.path.isfile(theory_name):
            with open(theory_name, "w") as f:
                json.dump(
                    {"teacher": self.teacher, "reports": []}, f)

# ===================================================================== #

    def len(self):
        """Сколько отчётов у менеджера на руках в данный момент."""
        return len(self.pull())

# ===================================================================== #

    # TODO: ПЕРЕДЕЛАТЬ НАХУЙ!
    # FIXME!
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
                if not checklist["humans"]:
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
