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