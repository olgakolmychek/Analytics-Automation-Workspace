def print_report(report_data):
    """
    Выводит итоговый отчет по странам.
    """

    print("\nОбщий отчет:")

    for country, data in report_data.items():

        print("\n" + country)

        print(data)