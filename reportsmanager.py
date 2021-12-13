import json, os
from reportmaker import ReportMaker
import glob


class Report:
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
            if self.report_type == "Контрольная работа":
                self.date = kwargs[-7]
                self.curr_humans = kwargs[-6]
                self.n_quarter = kwargs[-5]
                self.e = dict(zip(["2", "3", "4", "5"], kwargs[-4:12][::-1]))
            else:
                self.n_quarter = kwargs[-5]
                self.date = kwargs[-7]
                self.curr_humans = kwargs[-6]
            self.statistics = "-"

    def to_list(self, no_stats=False, split_e=True, all_params=True, order=-1):
        return ([self.index, self.course, self.n_class, self.humans, self.report_type, self.date, self.curr_humans,
                self.n_quarter] +
                ([self.e["5"], self.e["4"], self.e["3"], self.e["2"]][::order] if split_e else [self.e]) + (
            [] if no_stats else [self.statistics])
                ) if all_params else ((
                    [self.index, self.course, self.n_class, self.humans, self.report_type, self.date, self.curr_humans]
                    if self.report_type == "Контрольная работа" else
                    [self.index, self.course, self.n_class, self.humans, self.report_type, self.n_quarter]) +
                                      ([self.e["5"], self.e["4"], self.e["3"], self.e["2"]][::order]
                                       if split_e else [self.e]) + ([] if no_stats else [self.statistics]))

    def to_dict(self):
        return dict(zip(["index", "course", "n_class", "humans", "report_type", "date", "curr_humans", "e", "statistics"],
                    self.to_list(split_e=False, all_params=False))) if self.report_type == "Контрольная работа" else (
            dict(zip(["index", "course", "n_class", "humans", "report_type", "n_quarter", "e", "statistics"],
                     self.to_list(split_e=False, all_params=False))))


class ReportsManager:
    def __init__(self, teacher=""):
        self.teacher = teacher
        self.maker = ReportMaker()

        if self.teacher != "":
            self.__create()
            self.maker = ReportMaker(self.teacher + ".json")

    def set_teacher(self, teacher):
        self.teacher = teacher
        self.maker = ReportMaker(self.teacher + ".json")
        self.__create()

    @staticmethod
    def get_last_teacher():
        files = glob.glob("*.json")
        return max(files, key=os.path.getctime).split(".")[0] if files != [] else "NOBODY"

    @staticmethod
    def is_teacher(teacher):
        return True if (teacher + ".json" in glob.glob("*.json") and ReportMaker(teacher + ".json").take() != []
                        ) else False

    @staticmethod
    def delete_trash_reports():
        [os.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)), i)) for i in glob.glob("*.json")
         if ReportMaker(i).take() == []]

    def __create(self):
        if not os.path.isfile(self.teacher + ".json"):
            with open(self.teacher + ".json", "w") as f:
                json.dump(
                    {"teacher": self.teacher, "reports": []}, f)

    def len(self):
        return len(self.pull())

    def __exist(self, report):
        reports = self.maker.take()
        rt = report["report_type"]
        checklist = {}
        """Чеклист здесь отличается от чеклиста в гуе. Здесь мы отмечаем совпадения по тем или иным ключам"""
        for i in reports:
            if i["report_type"] == rt:
                for k in i.keys():
                    if k != "index" and k != "statistics":
                        if i[k] == report[k]:
                            checklist[k] = True
                        else:
                            checklist[k] = False
        if checklist:
            if checklist["course"] and checklist["n_class"]:
                if checklist["humans"]:
                    return -1
                if rt == "Контрольная работа":
                    if checklist["date"] and (not checklist["e"] or not checklist["curr_humans"]):
                        return -1
                    elif checklist["date"] and checklist["e"] and checklist["curr_humans"]:
                        return True
                else:
                    return -1 if checklist["n_quarter"] and not checklist["e"] else False
            elif not checklist["course"] and checklist["n_class"] and not checklist["humans"]:
                return -1
        return False

    def push(self, **kwargs):
        result_of_operation = self.__exist(kwargs)
        if result_of_operation == -1 or result_of_operation:
            return "ERROR"
        elif not result_of_operation:
            self.maker.make(**kwargs)
            return "SUCCESS"

    def pull(self, last_report=False, **kwargs):
        reports = self.maker.take()
        if last_report:
            return Report(reports[-1])
        return [Report(i) for i in reports]

    def delete(self, report, from_str=False):
        print(report)
        self.maker.burn(Report(report, from_str=from_str).to_dict())


if __name__ == "__main__":
    rm = ReportsManager("Глок Максим Игоревич")
    rm.push(
        course="Математика",
        n_class=5,
        humans=27,
        report_type="Контрольная работа",
        date="17.02.2021",
        curr_humans=20,
        e={2: 1, 3: 10, 4: 7, 5: 2}
    )
