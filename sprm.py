
from prettytable import PrettyTable


name = input("Ваши ФИО: ")
course = input("Ваш предмет: ")
n_class = int(input("Класс: "))
c_class = int(input("Сколько человек в классе: "))
report_type = input("За контрольную или четверть (к/Ч)? ")
if report_type == "к":
    date_test = input("Дата проведения: ")
    commom_c_class = input("Сколько человек было на контрольной работе? ")
else:
    n_quarter = int(input("Номер четверти (1, 2, 3, 4): "))

e = dict(zip([2, 3, 4, 5], [int(input(f"Количество {i+2}: ")) for i in range(4)]))
print("\n\n\n")

print("ФИО:", name)
print("Предмет:", course)
print("Четверть:", n_quarter)

report = PrettyTable()

report.field_names = ["Класс", "Двоек", "Троек", "Четвёрок", "Пятёрок", "Успеваемость", "Качество", "Средний балл", "СОК"]

report.add_row(
    [
        n_class, e[2], e[3], e[4], e[5],
        str((e[5] + e[4] + e[3]) / c_class * 100) + "%",
        str((e[5] + e[4]) / c_class * 100) + "%",
        (5*e[5] + 4*e[4] + 3*e[3] + 2*e[2]) / c_class,
        str((e[5]*1 + e[4]*0.64 + e[3]*0.36 + e[2]*0.14) / c_class * 100) + "%"
    ])
print(report)

