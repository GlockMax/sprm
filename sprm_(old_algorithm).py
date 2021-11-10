import json, os.path, glob


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


def new_report(teacher: str, course: str, n_class: str, humans: int, report_type: str, date: str = "00.00.000",
               common_c_class: int = 0, n_quarter: int = 1, e: dict = {}):
    """Создаёт новый отчёт для нового учителя"""
    iwp = {"teacher": teacher, "courses": []}

    iwp["courses"].append({"course": course})

    iwp["courses"][-1]["classes"] = {n_class: {}}

    iwp["courses"][-1]["classes"][n_class]["humans"] = humans

    if report_type == "к":
        iwp["courses"][-1]["classes"][n_class]["tests"] = [{"date": None}]

        iwp["courses"][-1]["classes"][n_class]["tests"][-1]["date"] = date

        iwp["courses"][-1]["classes"][n_class]["tests"][-1]["curr_humans"] = common_c_class

        iwp["courses"][-1]["classes"][n_class]["tests"][-1]["eva"] = e
        iwp["courses"][-1]["classes"][n_class]["tests"][-1]["statistics"] = {
            "Успеваемость": str(a_performance(e, humans)) + "%",
            "Качество": str(quality(e, humans)) + "%",
            "Средний балл": average_score(e, humans),
            "СОК": str(sok(e, humans)) + "%"
        }

    else:
        iwp["courses"][-1]["classes"][n_class]["quarters"] = [{"num_quarter": None}]

        iwp["courses"][-1]["classes"][n_class]["quarters"][-1]["num_quarter"] = n_quarter

        iwp["courses"][-1]["classes"][n_class]["quarters"][-1]["eva"] = e
        iwp["courses"][-1]["classes"][n_class]["quarters"][-1]["statistics"] = {
            "Успеваемость": str(a_performance(e, humans)) + "%",
            "Качество": str(quality(e, humans)) + "%",
            "Средний балл": average_score(e, humans),
            "СОК": str(sok(e, humans)) + "%"
        }

    with open(teacher + ".json", "w") as f:
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


def edit_report(iwp, course: str, n_class: str, humans: int, report_type: str, date: str = "00.00.000",
                common_c_class: int = 0, n_quarter: int = 1, e: dict = {}):
    """Редактирует уже созданный отчёт учителя"""
    find_course = find(iwp["courses"], course, "course")
    if find_course >= 0:
        course_index = find_course
    else:
        iwp["courses"].append({"course": course})
        course_index = -1
        iwp["courses"][course_index]["classes"] = {}

    if find(list(iwp["courses"][course_index]["classes"].keys()), n_class):
        print("ЗДЕСЬ")
        class_index = n_class
    else:
        iwp["courses"][course_index]["classes"][n_class] = {}
        class_index = n_class
        iwp["courses"][course_index]["classes"][n_class]["humans"] = humans

    if report_type == "к":
        try:
            print("----- В TRY -----")
            find_date = find(list(iwp["courses"][course_index]["classes"][n_class]["tests"]), date, "date")
        except:
            print("----- В EXCEPT -----")
            iwp["courses"][course_index]["classes"][n_class]["tests"] = [{"day": None}]
            find_date = find(list(iwp["courses"][course_index]["classes"][n_class]["tests"]), date, "date")

        if find_date >= 0:
            date_index = find_date
            print("Данные о выполнении этой контрольной работы уже есть. Если Вы хотите их отредактировать, то сделайте это чуть позже")
            return
        else:
            # iwp["courses"][course_index]["classes"][n_class]["tests"] = []
            iwp["courses"][course_index]["classes"][n_class]["tests"].append({"date": date})
            date_index = -1
        iwp["courses"][course_index]["classes"][n_class]["tests"][date_index]["curr_humans"] = common_c_class
        humans = iwp["courses"][course_index]["classes"][n_class]["humans"]
        iwp["courses"][course_index]["classes"][n_class]["tests"][date_index]["eva"] = e
        iwp["courses"][course_index]["classes"][n_class]["tests"][date_index]["statistics"] = {
            "Успеваемость": str(a_performance(e, humans)) + "%",
            "Качество": str(quality(e, humans)) + "%",
            "Средний балл": average_score(e, humans),
            "СОК": str(sok(e, humans)) + "%"
        }
    else:
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
        iwp["courses"][course_index]["classes"][n_class]["quarters"][quarter_index]["eva"] = e
        iwp["courses"][course_index]["classes"][n_class]["quarters"][quarter_index]["statistics"] = {
            "Успеваемость": str(a_performance(e, humans)) + "%",
            "Качество": str(quality(e, humans)) + "%",
            "Средний балл": average_score(e, humans),
            "СОК": str(sok(e, humans)) + "%"
        }

    with open(iwp["teacher"] + ".json", "w") as f:
        json.dump(iwp, f)


def console_new_report():
    teacher = input("Ваше имя: ")
    course = input("Ваш предмет: ")
    n_class = input("Класс: ")
    humans = int(input("Сколько человек в классе: "))
    report_type = input("За контрольную или четверть (к/Ч)? ")
    if report_type == "к":
        report_type = "Контрольная работа"
        day = input("Дата проведения: ")
        common_c_class = int(input("Сколько человек было на контрольной работе? "))
        e = dict(zip([2, 3, 4, 5], [int(input(f"Количество {i + 2}: ")) for i in range(4)]))
        new_report(teacher=teacher, course=course, n_class=n_class, humans=humans, report_type=report_type, date=day,
                   common_c_class=common_c_class, e=e)
    else:
        n_quarter = int(input("Номер четверти (1, 2, 3, 4): "))
        e = dict(zip([2, 3, 4, 5], [int(input(f"Количество {i + 2}: ")) for i in range(4)]))
        new_report(teacher=teacher, course=course, n_class=n_class, humans=humans, report_type=report_type,
                   n_quarter=n_quarter, e=e)


def console_edit_report(iwp):
    course = input("Ваш предмет: ")
    n_class = input("Класс: ")
    humans = int(input("Сколько человек в классе: "))
    report_type = input("За контрольную или четверть (к/Ч)? ")
    if report_type == "к":
        report_type = "Контрольная работа"
        day = input("Дата проведения: ")
        common_c_class = int(input("Сколько человек было на контрольной работе? "))
        e = dict(zip([2, 3, 4, 5], [int(input(f"Количество {i + 2}: ")) for i in range(4)]))
        edit_report(iwp=iwp, course=course, n_class=n_class, humans=humans, report_type=report_type, date=day,
                    common_c_class=common_c_class, e=e)
    else:
        n_quarter = int(input("Номер четверти (1, 2, 3, 4): "))
        e = dict(zip([2, 3, 4, 5], [int(input(f"Количество {i + 2}: ")) for i in range(4)]))
        edit_report(iwp=iwp, course=course, n_class=n_class, humans=humans, report_type=report_type,
                    n_quarter=n_quarter, e=e)


def main():
    list_of_files = glob.glob('*.json')

    if list_of_files:
        latest_file = max(list_of_files, key=os.path.getctime)
        with open(latest_file, "r") as f:
            iwp = json.load(f)
            is_new_report = False
    else:
        is_new_report = True

    if is_new_report:
        console_new_report()
    else:
        print("Ваше имя ", iwp["teacher"], ", верно?", sep="")
        print()
        to_continue = input("Хотите продолжить? (д/Н) ")
        if to_continue == "д":
            console_edit_report(iwp)
        else:
            console_new_report()


if __name__ == "__main__":
    main()
