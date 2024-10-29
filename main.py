import requests

url = 'https://api.hh.ru/vacancies'
lang_list = {
    'Python', 'JavaScript', 'Java', 'C#', 'PHP', 'C++', 'Golang', 'Ruby', 'SQL', 'Visual Basic'
}
vacancies_count = {}

def get_vacancies(lang):
    all_vacancies = []
    page = 0
    while True:
        params = {
            'text': f'программист {lang}',
            'area': 1,
            'period': 5,
            'page': page,
            'per_page': 100
        }
        print(f"Загрузка {lang} - страница {page + 1}...")
        response = requests.get(url, params=params)
        response.raise_for_status()
        data_vacancies = response.json()
        all_vacancies.extend(data_vacancies['items'])
        if page >= data_vacancies['pages'] - 1:
            break
        page += 1

    return all_vacancies


def calculate_average_salary(salary_info):
    if salary_info.get('currency') != 'RUR':
        return None

    if salary_info.get('from') is not None and salary_info.get('to') is not None:
        return int((salary_info['from'] + salary_info['to']) / 2)
    elif salary_info.get('from') is not None:
        return int(salary_info['from'] * 1.2)
    elif salary_info.get('to') is not None:
        return int(salary_info['to'] * 0.8)

    return None

def get_vacancies_count():
    for lang in lang_list:
        all_vacancies  = get_vacancies(lang)
        count_vacancies = len(all_vacancies)
        if count_vacancies > 100:
            vacancies_count[lang] = count_vacancies
    return vacancies_count

def predict_rub_salary():
    salary_data = {}
    vacancies_count_result = get_vacancies_count()

    for lang in lang_list:
        total_vacancies = vacancies_count_result.get(lang)
        if total_vacancies is None:
            continue

        all_vacancies = get_vacancies(lang)
        salaries = []
        processed_count = 0

        for vacancy in all_vacancies:
            processed_count += 1
            salary_info = vacancy.get('salary')
            if salary_info is None:
                continue

            average_salary = calculate_average_salary(salary_info)
            if average_salary is not None:
                salaries.append(average_salary)

        if salaries:
            average_salary = sum(salaries) // len(salaries)
            salary_data[lang] = {
                "vacancies_found": total_vacancies,
                "vacancies_processed": processed_count,
                "average_salary": average_salary
            }

    return salary_data

print(predict_rub_salary())