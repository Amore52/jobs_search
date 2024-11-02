import requests
from terminaltables import AsciiTable
from dotenv import load_dotenv
from os import environ


load_dotenv()
TOWN = 1
DAYS = 20
VACANCY_ON_PAGE = 100
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
            'area': TOWN,
            'period': DAYS,
            'page': page,
            'per_page': VACANCY_ON_PAGE
        }
        print(f"Загрузка HH: {lang} - страница {page + 1}...")

        response = requests.get(HH_URL, params=params)
        response.raise_for_status()
        data = response.json()
        vacancies.extend(data['items'])

        if page == 0:
            total_vacancies = data['found']
        if page >= data['pages'] - 1:
            break
        page += 1

    return vacancies, total_vacancies


def sj_get_vacancies(lang):
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

        response = requests.get(SJ_URL, headers=SJ_HEADERS, params=params)
        response.raise_for_status()
        data = response.json()

        if page == 0:
            total_vacancies = data['total']
        if not data['objects']:
            break
        vacancies.extend(data['objects'])

        if page >= data['total'] // VACANCY_ON_PAGE:
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

    for lang in HH_LANGUAGES:
        all_vacancies, total_vacancies = hh_get_vacancies(lang)
        salaries = []
        processed_count = 0

        for vacancy in all_vacancies:
            processed_count += 1
            vacancy_salary = vacancy.get('salary')
            if vacancy_salary is None:
                continue
            average_salary = calculate_average_salary(
                vacancy_salary.get('from'),
                vacancy_salary.get('to'),
                vacancy_salary.get('currency')
            )
            if average_salary:
                salaries.append(average_salary)

        hh_salary[lang] = {
            "vacancies_found": total_vacancies,
            "vacancies_processed": processed_count,
            "average_salary": sum(salaries) // len(salaries) if salaries else 0
        }

    return hh_salary

def sj_predict_rub_salary():
    salary_data = {}

    for lang in SJ_LANGUAGES:
        all_vacancies, total_vacancies = sj_get_vacancies(lang)
        salaries = []
        processed_count = 0

        for vacancy in all_vacancies:
            processed_count += 1
            average_salary = calculate_average_salary(
                vacancy.get('payment_from'),
                vacancy.get('payment_to'),
                'RUR'
            )
            if average_salary:
                salaries.append(average_salary)

        salary_data[lang] = {
            "vacancies_found": total_vacancies,
            "vacancies_processed": processed_count,
            "average_salary": sum(salaries) // len(salaries) if salaries else 0
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

def main():
    hh_salary = hh_predict_rub_salary()
    sj_salary = sj_predict_rub_salary()

    print_salary_table(hh_salary, "+HeadHunter Moscow")
    print_salary_table(sj_salary, "+SuperJob Moscow")

if __name__ == "__main__":
    main()
