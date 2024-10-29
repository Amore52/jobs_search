import requests


url = 'https://api.superjob.ru/2.20/vacancies/'
headers = {
    'X-Api-App-Id': 'v3.r.138674171.3724eabd2c37d9127fcf0d22d71c372a26d3cf0d.7b3064ca31314bcc431d009af8ee62516ec909f5',
}

lang_list = {
    'Python', 'JavaScript', 'Java', 'C#', 'PHP', 'C++', 'Golang', 'Ruby', 'SQL', 'Visual Basic'
}

def get_vacancies():
    town = 'Москва'
    for lang in lang_list:

        params = {
            'keyword': f'программист {lang}',
            'town': town
        }
        response = requests.get(url, headers=headers, params=params)
        data_vacancies = response.json()
        for vacancy in data_vacancies['objects']:
            name_vacancy = vacancy['profession']
            print(lang, name_vacancy, town, sep=', ')




get_vacancies()






