import requests

from terminaltables import AsciiTable
from dotenv import load_dotenv
from os import environ


load_dotenv()
sj_token = environ.get('SJ_TOKEN')
HH_URL = 'https://api.hh.ru/vacancies'
HH_LANGUAGES = {
    'Python', 'JavaScript', 'Java', 'C#', 'PHP', 'C++', 'Golang', 'Ruby', 'SQL', 'Visual Basic'
}

SJ_URL = 'https://api.superjob.ru/2.20/vacancies/'
SJ_HEADERS = {
    'X-Api-App-Id': sj_token,
}
SJ_LANGUAGES = {
    'Python', 'JavaScript', 'Java', 'C#', 'PHP', 'C++', 'Golang', 'Ruby', 'SQL', 'Visual Basic'
}


def hh_get_vacancies(lang):
    vacancies = []
    page = 0

    while True:
        params = {
            'text': f'программист {lang}',
            'area': 1,
            'period': 30,
            'page': page,
            'per_page': 100
        }
        print(f"Загрузка HH: {lang} - страница {page + 1}...")

        response = requests.get(HH_URL, params=params)
        response.raise_for_status()
        data = response.json()
        vacancies.extend(data['items'])

        if page >= data['pages'] - 1:
            break
        page += 1

    return vacancies


def hh_calculate_average_salary(salary_info):
    if salary_info.get('currency') != 'RUR':
        return None

    salary_from = salary_info.get('from')
    salary_to = salary_info.get('to')

    if salary_from is not None and salary_to is not None:
        return int((salary_from + salary_to) / 2)
    if salary_from is not None:
        return int(salary_from * 1.2)
    if salary_to is not None:
        return int(salary_to * 0.8)

    return None


def hh_predict_rub_salary():
    salary_data = {}

    for lang in HH_LANGUAGES:
        all_vacancies = hh_get_vacancies(lang)
        salaries = []
        processed_count = 0

        for vacancy in all_vacancies:
            processed_count += 1
            salary_info = vacancy.get('salary')
            if salary_info is None:
                continue
            average_salary = hh_calculate_average_salary(salary_info)
            if average_salary is not None:
                salaries.append(average_salary)

        if salaries:
            average_salary = sum(salaries) // len(salaries)
            salary_data[lang] = {
                "vacancies_found": len(all_vacancies),
                "vacancies_processed": processed_count,
                "average_salary": average_salary
            }

    return salary_data


def sj_get_vacancies(lang):
    vacancies = []
    page = 0

    while True:
        params = {
            'keyword': f'программист {lang}',
            'town': 4,
            'page': page,
            'count': 100
        }
        print(f"Загрузка SJ: {lang} - страница {page + 1}...")

        response = requests.get(SJ_URL, headers=SJ_HEADERS, params=params)
        response.raise_for_status()
        data = response.json()

        if not data['objects']:
            break
        vacancies.extend(data['objects'])

        if page >= data['total'] // 100:
            break
        page += 1

    return vacancies


def sj_predict_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_from + salary_to) // 2
    if salary_from:
        return int(salary_from * 1.2)
    if salary_to:
        return int(salary_to * 0.8)
    return None


def sj_predict_rub_salary():
    salary_data = {}

    for lang in SJ_LANGUAGES:
        all_vacancies = sj_get_vacancies(lang)
        salaries = []
        processed_count = 0

        for vacancy in all_vacancies:
            processed_count += 1
            average_salary = sj_predict_salary(
                vacancy.get('payment_from'),
                vacancy.get('payment_to')
            )
            if average_salary is not None:
                salaries.append(average_salary)

        if salaries:
            average_salary = sum(salaries) // len(salaries)
            salary_data[lang] = {
                "vacancies_found": len(all_vacancies),
                "vacancies_processed": processed_count,
                "average_salary": average_salary
            }

    return salary_data


def print_salary_table(salary_data, title):
    table_data = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']
    ]

    for lang, stats in salary_data.items():
        table_data.append([
            lang,
            stats['vacancies_found'],
            stats['vacancies_processed'],
            stats['average_salary']
        ])

    table = AsciiTable(table_data, title)
    print(table.table)


hh_salary_data = hh_predict_rub_salary()
sj_salary_data = sj_predict_rub_salary()

print_salary_table(hh_salary_data, "+HeadHunter Moscow")
print_salary_table(sj_salary_data, "+SuperJob Moscow")
