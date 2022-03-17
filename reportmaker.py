import json


# ===================================================================== #
# ///////////////////////////////////////////////////////////////////// #
# ===================================================================== #


class ReportMaker:
    """Класс создателя отчётов."""
    def __init__(self, filename=""):
        self.filename = filename

# ===================================================================== #

    @staticmethod
    def a_performance(e, humans):
        """Возвращает успеваемость по четверти или КР."""
        return round((e[5] + e[4] + e[3]) / humans * 100)

# ===================================================================== #

    @staticmethod
    def quality(e, humans):
        """Возвращает качество выполнения четверти или КР."""
        return round((e[5] + e[4]) / humans * 100)

# ===================================================================== #

    @staticmethod
    def average_score(e, humans):
        """Возвращает средний балл четверти или КР."""
        return round((5 * e[5] + 4 * e[4] + 3 * e[3] + 2 * e[2]) / humans, 3)

# ===================================================================== #

    @staticmethod
    def sok(e, humans):
        """Возвращает СОК четверти или КР."""
        return round((e[5] * 1 + e[4] * 0.64 + e[3] * 0.36 + e[2] * 0.14) / humans * 100)

# ===================================================================== #

    def make(self, **kwargs):
        """Создать отчёт, положить в файлик."""
        report = kwargs
        report["statistics"] = {
            "Успеваемость": str(self.a_performance(report["e"], (
                report["humans"] if report["report_type"] == "Четверть" or report["report_type"] == "Год"
                else report["curr_humans"]))) + "%",
            "Качество": str(self.quality(report["e"], (
                report["humans"] if report["report_type"] == "Четверть" or report["report_type"] == "Год"
                else report["curr_humans"]))) + "%",
            "Средний балл": self.average_score(report["e"], (
                report["humans"] if report["report_type"] == "Четверть" or report["report_type"] == "Год"
                else report["curr_humans"])),
            "СОК": str(self.sok(report["e"], (
                report["humans"] if report["report_type"] == "Четверть" or report["report_type"] == "Год"
                else report["curr_humans"]))) + "%",
        }
        with open(self.filename, "r") as f:
            r = json.load(f)
        report["index"] = len(r["reports"]) + 1
        with open(self.filename, "w") as f:
            r["reports"].append(report)
            json.dump(r, f)

# ===================================================================== #

    def take(self):
        """Взять всё то, что лежит в файлике."""
        with open(self.filename, "r") as f:
            reports = json.load(f)["reports"]
        return reports

# ===================================================================== #

    def burn(self, index):
        """Удалить из файлика отчёт. На вход даётся ТОЛЬКО ИНДЕКС ОТЧЁТА"""
        with open(self.filename, "r") as f:
            r = json.load(f)

        del r["reports"][index-1]

        """========= Переписывем индексы. ========="""
        for i in range(len(r["reports"])):
            r["reports"][i]["index"] = i + 1

        with open(self.filename, "w") as f:
            json.dump(r, f)
