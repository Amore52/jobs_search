import requests
from terminaltables import AsciiTable
from dotenv import load_dotenv
from os import environ


TOWN = 1
DAYS = 1
VACANCY_ON_PAGE = 100
HH_URL = 'https://api.hh.ru/vacancies'
LANGUAGES = {
    'Python', 'JavaScript', 'Java', 'C#', 'PHP', 'C++', 'Golang', 'Ruby', 'SQL', 'Visual Basic'
}
SJ_URL = 'https://api.superjob.ru/2.20/vacancies/'


def hh_get_vacancies(lang):
    vacancies = []
    page = 0

    while True:
        params = {
            'text': f'программист {lang}',
            'area': TOWN,
            'period': DAYS,
            'page': page,
            'per_page': VACANCY_ON_PAGE
        }
        print(f"Загрузка HH: {lang} - страница {page + 1}...")

        response = requests.get(HH_URL, params=params)
        response.raise_for_status()
        json_response = response.json()
        vacancies.extend(json_response['items'])

        if page == 0:
            total_vacancies = json_response['found']
        if page >= json_response['pages'] - 1:
            break
        page += 1

    return vacancies, total_vacancies


def sj_get_vacancies(lang, sj_headers):
    vacancies = []
    page = 0

    while True:
        params = {
            'keyword': f'программист {lang}',
            'town': 'Moscow',
            'page': page,
            'count': VACANCY_ON_PAGE
        }
        print(f"Загрузка SJ: {lang} - страница {page + 1}...")

        response = requests.get(SJ_URL, headers=sj_headers, params=params)
        response.raise_for_status()
        json_response = response.json()

        if page == 0:
            total_vacancies = json_response['total']
        vacancies.extend(json_response['objects'])
        if not json_response.get('more'):
            break
        page += 1

    return vacancies, total_vacancies


def calculate_average_salary(salary_from, salary_to, currency):
    if currency != 'RUR':
        return None

    if salary_from and salary_to:
        return (salary_from + salary_to) // 2
    if salary_from:
        return int(salary_from * 1.2)
    if salary_to:
        return int(salary_to * 0.8)
    return None


def hh_predict_rub_salary():
    hh_salary = {}

    for lang in LANGUAGES:
        all_vacancies, total_vacancies = hh_get_vacancies(lang)
        salaries = []

        for vacancy in all_vacancies:
            vacancy_salary = vacancy.get('salary')
            if vacancy_salary:
                average_salary = calculate_average_salary(
                    vacancy_salary.get('from'),
                    vacancy_salary.get('to'),
                    vacancy_salary.get('currency')
                )
            if average_salary:
                salaries.append(average_salary)

        hh_salary[lang] = {
            "vacancies_found": total_vacancies,
            "vacancies_processed": len(salaries),
            "average_salary": sum(salaries) // len(salaries) if salaries else 0
        }

    return hh_salary


def sj_predict_rub_salary(sj_headers):
    sj_salary = {}

    for lang in LANGUAGES:
        all_vacancies, total_vacancies = sj_get_vacancies(lang, sj_headers)
        salaries = []

        for vacancy in all_vacancies:
            average_salary = calculate_average_salary(
                vacancy.get('payment_from'),
                vacancy.get('payment_to'),
                'RUR'
            )
            if average_salary:
                salaries.append(average_salary)

        sj_salary[lang] = {
            "vacancies_found": total_vacancies,
            "vacancies_processed": len(salaries),
            "average_salary": sum(salaries) // len(salaries) if salaries else 0
        }

    return sj_salary


def print_salary_table(salary, title):
    table = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']
    ]

    for lang, stats in salary.items():
        table.append([
            lang,
            stats['vacancies_found'],
            stats['vacancies_processed'],
            stats['average_salary']
        ])

    table = AsciiTable(table, title)
    print(table.table)


def main():
    load_dotenv()
    sj_token = environ.get('SJ_TOKEN')
    sj_headers = {
        'X-Api-App-Id': sj_token,
    }

    hh_salary = hh_predict_rub_salary()
    sj_salary = sj_predict_rub_salary(sj_headers)

    print_salary_table(hh_salary, "+HeadHunter Moscow")
    print_salary_table(sj_salary, "+SuperJob Moscow")


if __name__ == "__main__":
    main()
