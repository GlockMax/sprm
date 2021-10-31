import json, os.path
from prettytable import PrettyTable


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


def new_report(iwp):
    """Создаёт новый отчёт для нового учителя"""
    teacher = input("Ваши ФИО: ")
    iwp["teacher"] = teacher

    iwp["courses"] = []
    course = input("Ваш предмет: ")
    iwp["courses"].append({"course": course})

    n_class = input("Класс: ")
    iwp["courses"][-1]["classes"] = {n_class: {}}

    humans = int(input("Сколько человек в классе: "))
    iwp["courses"][-1]["classes"][n_class]["humans"] = humans

    report_type = input("За контрольную или четверть (к/Ч)? ")
    if report_type == "к":
        iwp["courses"][-1]["classes"][n_class]["tests"] = [{"day": None}]

        day = input("Дата проведения: ")
        iwp["courses"][-1]["classes"][n_class]["tests"][-1]["day"] = day

        common_c_class = int(input("Сколько человек было на контрольной работе? "))
        iwp["courses"][-1]["classes"][n_class]["tests"][-1]["curr_humans"] = common_c_class

        e = dict(zip([2, 3, 4, 5], [int(input(f"Количество {i + 2}: ")) for i in range(4)]))
        iwp["courses"][-1]["classes"][n_class]["tests"][-1]["eva"] = e
        iwp["courses"][-1]["classes"][n_class]["tests"][-1]["statistics"] = {
            "Успеваемость": str(a_performance(e, humans)) + "%",
            "Качество": str(quality(e, humans)) + "%",
            "Средний балл": average_score(e, humans),
            "СОК": str(sok(e, humans)) + "%"
        }

    else:
        iwp["courses"][-1]["classes"][n_class]["quarters"] = [{"num_quarter": None}]

        n_quarter = int(input("Номер четверти (1, 2, 3, 4): "))
        iwp["courses"][-1]["classes"][n_class]["quarters"][-1]["num_quarter"] = n_quarter

        e = dict(zip([2, 3, 4, 5], [int(input(f"Количество {i + 2}: ")) for i in range(4)]))
        iwp["courses"][-1]["classes"][n_class]["quarters"][-1]["eva"] = e
        iwp["courses"][-1]["classes"][n_class]["quarters"][-1]["statistics"] = {
            "Успеваемость": str(a_performance(e, humans)) + "%",
            "Качество": str(quality(e, humans)) + "%",
            "Средний балл": average_score(e, humans),
            "СОК": str(sok(e, humans)) + "%"
        }

    print("\n\n\n")

    print("ФИО:", teacher)
    print("Предмет:", course)
    if report_type == "к":
        print(f"Контрольная работа за {day}, {common_c_class} человек присутствовали")
    else:
        print("Четверть:", n_quarter)

    report = PrettyTable()

    report.field_names = ["Класс", "Двоек", "Троек", "Четвёрок", "Пятёрок", "Успеваемость", "Качество", "Средний балл",
                          "СОК"]

    report.add_row(
        [
            n_class, e[2], e[3], e[4], e[5],
            str(a_performance(e, humans)) + "%",
            str(quality(e, humans)) + "%",
            average_score(e, humans),
            str(sok(e, humans)) + "%"
        ])
    print(report)

    with open("teacher.json", "w") as f:
        json.dump(iwp, f)


def find(a, x, w=""):
    """При w="" возвращает True, если найден x в итерируемом объекте a; при w, равной некому строковому значению,
    производится поиск среди словарей списка a на ключ, равный w"""
    if a == []: return False # FIXME
    if w == "":
        for i in a:
            if i == x:
                return True
            return False
    for i in range(len(a)):
        if a[i][w] == x: return i
    return -1


def edit_report(iwp):
    """Редактирует уже созданный отчёт учителя"""
    course = input("Ваш предмет: ")
    find_course = find(iwp["courses"], course, "course")
    if find_course >= 0:
        course_index = find_course
    else:
        iwp["courses"].append({"course": course})
        course_index = -1
        iwp["courses"][course_index]["classes"] = {}

    n_class = input("Класс: ")
    if find(list(iwp["courses"][course_index]["classes"].keys()), n_class):
        print("ЗДЕСЬ")
        class_index = n_class
    else:
        iwp["courses"][course_index]["classes"][n_class] = {}
        class_index = n_class
        humans = int(input("Сколько человек в классе: "))
        iwp["courses"][course_index]["classes"][n_class]["humans"] = humans

    report_type = input("За контрольную или четверть (к/Ч)? ")
    
    
    if report_type == "к":
        day = input("Дата проведения: ")
        try:
            print("----- В TRY -----")
            find_day = find(list(iwp["courses"][course_index]["classes"][n_class]["tests"]), day, "day")
        except:
            print("----- В EXCEPT -----")
            iwp["courses"][course_index]["classes"][n_class]["tests"] = [{"day": None}]
            
            find_day = find(list(iwp["courses"][course_index]["classes"][n_class]["tests"]), day, "day")
        if find_day >= 0:
            day_index = find_day
            print("Данные о выполнении этой контрольной работы уже есть. Если Вы хотите их отредактировать, то сделайте это чуть позже")
            return
        else:
            # iwp["courses"][course_index]["classes"][n_class]["tests"] = []
            iwp["courses"][course_index]["classes"][n_class]["tests"].append({"day": day})
            day_index = -1
        common_c_class = int(input("Сколько человек было на контрольной работе? "))
        iwp["courses"][course_index]["classes"][n_class]["tests"][day_index]["curr_humans"] = common_c_class
        humans = iwp["courses"][course_index]["classes"][n_class]["humans"]
        e = dict(zip([2, 3, 4, 5], [int(input(f"Количество {i + 2}: ")) for i in range(4)]))
        iwp["courses"][course_index]["classes"][n_class]["tests"][day_index]["eva"] = e
        iwp["courses"][course_index]["classes"][n_class]["tests"][day_index]["statistics"] = {
            "Успеваемость": str(a_performance(e, humans)) + "%",
            "Качество": str(quality(e, humans)) + "%",
            "Средний балл": average_score(e, humans),
            "СОК": str(sok(e, humans)) + "%"
        }
    else:
        n_quarter = int(input("Номер четверти (1, 2, 3, 4): "))
        try:
            print("----- B TRY -----")
            find_quarter = find(iwp["courses"][course_index]["classes"][n_class]["quarters"], n_quarter, "num_quart")
        except:
            print("----- B EXCEPT -----")
            iwp["courses"][course_index]["classes"][n_class]["quarters"] = [{"num_quart": None}]
            find_quarter = find(iwp["courses"][course_index]["classes"][n_class]["quarters"], n_quarter, "num_quart")
        if find_quarter >= 0:
            quarter_index = find_quarter
            print("Данные о выполнении этой четверти уже есть. Если Вы хотите их отредактировать, то сделайте это чуть позже")
            return
        else:
            # iwp["courses"][course_index]["classes"][n_class]["quarters"] = []
            iwp["courses"][course_index]["classes"][n_class]["quarters"].append({"num_quart": n_quarter})
            quarter_index = -1
        humans = iwp["courses"][course_index]["classes"][n_class]["humans"]
        e = dict(zip([2, 3, 4, 5], [int(input(f"Количество {i + 2}: ")) for i in range(4)]))
        iwp["courses"][course_index]["classes"][n_class]["quarters"][quarter_index]["eva"] = e
        iwp["courses"][course_index]["classes"][n_class]["quarters"][quarter_index]["statistics"] = {
            "Успеваемость": str(a_performance(e, humans)) + "%",
            "Качество": str(quality(e, humans)) + "%",
            "Средний балл": average_score(e, humans),
            "СОК": str(sok(e, humans)) + "%"
        }

    print("\n\n\n")

    print("ФИО:", iwp["teacher"])
    print("Предмет:", iwp["courses"][course_index]["course"])
    if report_type == "к":
        print(f"Контрольная работа за {day}, {common_c_class} человек присутствовали")
    else:
        print("Четверть:", n_quarter)

    report = PrettyTable()

    report.field_names = ["Класс", "Двоек", "Троек", "Четвёрок", "Пятёрок", "Успеваемость", "Качество", "Средний балл",
                          "СОК"]

    report.add_row(
        [
            n_class, e[2], e[3], e[4], e[5],
            str(a_performance(e, humans)) + "%",
            str(quality(e, humans)) + "%",
            average_score(e, humans),
            str(sok(e, humans)) + "%"
        ])
    print(report)

    with open("teacher.json", "w") as f:
        json.dump(iwp, f)


def main():
    if os.path.exists("./teacher.json"):
        with open("teacher.json", "r") as f:
            iwp = json.load(f)
            is_new_report = False
    else:
        iwp = {
            "teacher": None,
            "courses": None
        }
        is_new_report = True
    if is_new_report:
        new_report(iwp)
    else:
        print("Ваше имя ", iwp["teacher"], ", верно?", sep="")
        print()
        to_continue = input("Хотите продолжить? (д/Н) ")
        if to_continue == "д":
            edit_report(iwp)
        else:
            new_report(iwp)


if __name__ == "__main__":
    main()
