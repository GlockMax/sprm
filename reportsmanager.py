import json, os
from reportmaker import ReportMaker
import glob


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

    def __exist(self, report):
        reports = self.maker.take(stats_off=True)
        rt = report["report_type"]
        checklist = {}
        """Чеклист здесь отличается от чеклиста в гуе. Здесь мы отмечаем совпадения по тем или иным ключам"""
        for i in reports:
            if i["report_type"] == rt:
                for k in i.keys():
                    if i[k] == report[k]:
                        checklist[k] = True
                    else:
                        checklist[k] = False
        if checklist:
            if checklist["course"] and checklist["n_class"]:
                if not checklist["humans"]:
                    return -1
                if rt == "Контрольная работа":
                    if checklist["date"] and (not checklist["e"] or not checklist["curr_humans"]):
                        return -1
                    elif checklist["date"] and checklist["e"] and checklist["curr_humans"]:
                        return True
                else:
                    return -1 if checklist["n_quarter"] and not checklist["e"] else True
        return False

    def push(self, **kwargs):
        result_of_operation = self.__exist(kwargs)
        if result_of_operation == -1 or result_of_operation:
            return "ERROR"
        elif not result_of_operation:
            self.maker.make(**kwargs)
            return "SUCCESS"

    def pull(self, **kwargs):
        self.maker.take()


if __name__ == "__main__":
    rm = ReportsManager("teacher")
    rm.push(
        course="Математика",
        n_class=5,
        humans=27,
        report_type="Контрольная работа",
        date="17.02.2021",
        curr_humans=20,
        e={2: 1, 3: 10, 4: 7, 5: 2}
    )
