import csv
import json
import pytz
from datetime import datetime

"""
Парсит доску в Trello в CSV-файл. Принимает файл trello.json, который должен лежать на одном уровне со скриптом.
Этот файл скачивается путем добавления .json к краткому адресу доски в Trello, например: 
https://trello.com/b/{board_code} -> https://trello.com/b/{board_code}.json
"""


def get_creation_date_from_id(id: str):
    creation_time = datetime.fromtimestamp(int(id[0:8], 16))
    return pytz.utc.localize(creation_time)


if __name__ == '__main__':
    # Создание словарей для дальнейшего поиска по айдишникам
    with open('trello.json', 'r') as f:
        data = json.load(f)
        json_cards = data['cards']

        lists = {list["id"]: list["name"] for list in data["lists"]}
        labels = {label["id"]: label["name"] for label in data["labels"]}
        members = {member["id"]: member["fullName"] for member in data["members"]}

    csv_cards = []

    # Преобразование данных
    for json_card in json_cards:
        csv_card = {}
        csv_card['Название задачи'] = json_card['name']
        csv_card['Дата создания'] = get_creation_date_from_id(json_card['id'])
        csv_card['Дата последнего изменения'] = json_card['dateLastActivity'].replace("T", " ")
        csv_card['Столбец'] = lists[json_card['idList']]
        csv_card["Ссылка"] = json_card["shortUrl"]

        csv_card['Исполнитель'] = ''
        members_count = len(json_card['idMembers'])
        if members_count == 1:
            csv_card['Исполнитель'] = members[json_card['idMembers'][0]]
        elif members_count > 1:
            str_members = ''
            for member in json_card['idMembers']:
                str_members += members[member] + ', '
            csv_card['Исполнитель'] = str_members

        csv_card['Лейбл'] = ''
        labels_count = len(json_card['labels'])
        if labels_count == 1:
            csv_card['Лейбл'] = labels[json_card['labels'][0]['id']]
        elif labels_count > 1:
            str_labels = ''
            for label in json_card['labels']:
                str_labels += labels[label['id']] + ', '
            csv_card['Лейбл'] = str_labels

        csv_cards.append(csv_card)

    # Записывание в CSV
    with open('trello.csv', 'w', newline='') as csvfile:
        fieldnames = [
            'Название задачи',
            'Исполнитель',
            'Дата создания',
            'Дата последнего изменения',
            'Столбец',
            'Лейбл',
            'Ссылка'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for csv_card in csv_cards:
            writer.writerow(csv_card)
