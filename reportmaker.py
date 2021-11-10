import json


def a_performance(e, humans):
    """Возвращает успеваемость по четверти или КР"""
    return (e[5] + e[4] + e[3]) / humans * 100


def quality(e, humans):
    """Возвращает качество выполнения четверти или КР"""
    return (e[5] + e[4]) / humans * 100


def average_score(e, humans):
    """Возвращает средний балл четверти или КР"""
    return (5 * e[5] + 4 * e[4] + 3 * e[3] + 2 * e[2]) / humans


def sok(e, humans):
    """Возвращает СОК четверти или КР"""
    return (e[5] * 1 + e[4] * 0.64 + e[3] * 0.36 + e[2] * 0.14) / humans * 100


class ReportMaker:
    def __init__(self, filename=""):
        self.filename = filename

    def make(self, **kwargs):
        report = kwargs
        report["statistics"] = {
            "Успеваемость": str(a_performance(report["e"], report["humans"])) + "%",
            "Качество": str(quality(report["e"], report["humans"])) + "%",
            "Средний балл": average_score(report["e"], report["humans"]),
            "СОК": str(sok(report["e"], report["humans"])) + "%"
        }
        with open(self.filename, "r") as f:
            r = json.load(f)
        with open(self.filename, "w") as f:
            r["reports"].append(report)
            json.dump(r, f)

    def take(self, stats_off=False):
        with open(self.filename, "r") as f:
            reports = json.load(f)["reports"]

        if stats_off:
            for i in reports:
                del i["statistics"]

        return reports

    def burn(self, **kwargs):
        pass
