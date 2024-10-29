import requests


url = 'https://api.hh.ru/vacancies'
lang_list = {
    'Python', 'JavaScript', 'Java', 'C#', 'PHP', 'C++', 'Golang', 'Ruby', 'SQL', 'Visual Basic'
}
vacancies_count = {}


def get_response(params):
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def get_vacancies_count():
    for lang in lang_list:
        params = {
            'text': f'программист {lang}',
            'area': 1,
            'period': 30
        }
        count_vacancies = get_response(params)['found']
        if count_vacancies > 100:
            vacancies_count[lang] = count_vacancies
    return vacancies_count


def predict_rub_salary(vacancy):
    params = {
        'text': f'программист {vacancy}',
        'area': 1,
        'period': 30,
        'only_with_salary': True
    }
    data_vacancies = get_response(params)
    salaries = []
    for salary in data_vacancies['items']:
        if salary['salary'].get('currency') !='RUR':
            average_salary = 'None'
            salaries.append(average_salary)
        if salary['salary'].get('from') is not None:
            average_salary = int((salary['salary'].get('from')*1.2))
        elif salary['salary'].get('to') is not None:
            average_salary = int((salary['salary'].get('to') * 0.8))
        else:
            average_salary = int((salary['salary'].get('from')*salary['salary'].get('to'))/2)
        salaries.append(average_salary)

    return salaries



print(predict_rub_salary('Python'))
for salary in predict_rub_salary('Python'):
    i = salary
    average_salary = int((i + salary)/salary)
    print (average_salary)