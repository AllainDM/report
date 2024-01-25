import time

import requests
from bs4 import BeautifulSoup

import config

url_login = "http://us.gblnet.net/oper/"

HEADERS = {
    "main": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0"
}

data_users = {
    "action": "login",
    "username": config.loginUS,
    "password": config.pswUS
}

session_users = requests.Session()


def create_users_sessions():
    while True:
        try:
            response_users2 = session_users.post(url_login, data=data_users, headers=HEADERS).text
            # session_users.post(url_login, data=data_users, headers=HEADERS)
            print("Сессия Юзера создана 2")
            return response_users2
        except ConnectionError:
            print("Ошибка создания сессии")
            # TODO функция отправки тут отсутствует
            # send_telegram("Ошибка создания сессии UserSide, повтор запроса через 5 минут")
            # time.sleep(300)


response_users = create_users_sessions()


# TODO необходимо будет сделать одну функция под множество запросов
def get_address(list_service_masters):
    print(f'list_service_masters {list_service_masters["list_repairs"]}')
    list_repairs = list_service_masters["list_repairs"]
    for v in list_repairs:
        print(f"v: {v}")
        service = v[1]
        link = f"https://us.gblnet.net/oper/?core_section=task&action=show&id={service}"
        print("link 111")
        print(link)
        time.sleep(config.delay)  # Небольшая задержка
        try:
            print("Пытаемся получить страничку")
            html = session_users.get(link)
            if html.status_code == 200:
                print("Код ответа 200")
                # soup = BeautifulSoup(html.text, 'lxml')
                soup = BeautifulSoup(html.text, 'html.parser')
            #     # # print(f"soup {soup}")
                table = soup.find('table', class_="j_table")
                if table is None:
                    v.append([" ", " ", " ", "!!! Внимание, возможно не верный номер сервиса."])
                    print("!!! Внимание, возможно не верный номер сервиса.")
                else:
                    table_a = table.find_all('a')
                    print("Парсим ссылки")
                    print(table_a)
                    if table_a:
                        for i in table_a:
                            # print(i.text)
                            # print(type(i))
                            if 'Россия' in i.text:
                                answer_parser_address = parser_address(i.text)
                                v.append(answer_parser_address)
                                print(answer_parser_address)
                    else:
                        v.append([" ", " ", " ", "!!! Внимание, возможно не верный номер сервиса."])
                        print("!!! Внимание, возможно не верный номер сервиса.")
                print("###############################################################################################")
                print("###############################################################################################")
            else:
                print("error")
        except requests.exceptions.TooManyRedirects as e:
            print(f'{link} : {e}')
    return list_repairs


def parser_address(start_address):
    print("Запускаем парсер адреса")
    full_address = start_address  # Полный адрес для сверки
    print(f"full_address {full_address}")
    address = start_address.split(",")
    print(f"address {address}")
    district = address[2][1:-4].strip()
    # Исключения
    if district == "Кол":
        district = "Колпино"
    elif district == "Пу":
        district = "Пушкин"
    elif district == "Ломон":
        district = "Ломоносов"

    # Разберем улицу, для определения поселков.
    if address[3] == " Парголово" or \
            address[3] == " Шушары" or \
            address[3] == " Новое Девяткино дер." or \
            address[3] == " пос. Шушары" or \
            address[3] == " Кудрово" or \
            address[3] == " Мурино" or \
            address[3] == " Бугры пос." or \
            address[3] == " Репино" or \
            address[3] == " Сестрорецк" or \
            address[3] == " Песочный" or \
            address[3] == " Лисий" or \
            address[3] == " Горелово" or \
            address[3] == " Коммунар" or \
            address[3] == " Колпино" or \
            address[3] == " Горская" or \
            address[3] == " Понтонный" or \
            address[3] == " Тельмана" or \
            address[3] == " Тельмана пос." or \
            address[3] == " Стрельна" or \
            address[3] == " пос. Стрельна" or \
            address[3] == " Новогорелово":
        street = address[4][1:-4]
        if address[4][-2] == 'ш':
            street = address[4][1:-3]
    else:
        # Обычно в конце строки "ул." или "б-р", тоесть 3 символа, но есть варианты с "ш."
        street = address[3][1:-4]
        if address[3][-2] == 'ш':
            street = address[3][1:-3]

    # Отдельно для Кудрово у ЕТ пропишем район как Кудрово
    if address[3] == " Кудрово":
        district = "Кудрово"

    # TODO на будущее под все ТО надо будет доделать.
    # if t_o == "TOEast" and district == "Всеволожский":
    #     print(f"ТОВосток и Всеволожский район: {district}")
    #     continue
    # elif t_o == "TONorth" and district == "Кудрово":
    #     print(f"ТОСевер и Кудрово: {district}")
    #     continue

    # Дальше отфильтруем улицу на лишние слова общим фильтром
    street = street.strip()
    street = cut_street(street)

    # Ищем номер дома, при двойном адресе берем номер дома перед "вторым" адресом
    russia = start_address.replace(",", " ")
    russia = russia.split(" ")
    print(f"russia {russia}")
    russia_count = russia.count("Россия")
    print(f"russia_count {russia_count}")

    address_dom = ""

    if russia_count > 1:
        count_r = 0
        for num, el in enumerate(russia):
            print(f"el: {el}")
            if el == "Россия" and count_r == 1:
                print(f"Найдено второе совпадение, номер элемента: {num}")
                address_dom = russia[num - 2]
                break
            elif el == "Россия":
                count_r += 1
    else:
        address_dom = address[-1].split()
        print(f"address_dom {address_dom}")
        address_dom = address_dom[0]
        print(f"address_dom {address_dom}")

    # Отдельно надо разделить номер дома и корпус
    if address_dom[-1].isdigit():
        address_dom = address_dom.replace("/", "к")
    else:
        address_dom = address_dom.replace("/", "")

    address_kv = address[-1].split()

    return [street, address_dom, address_kv[-1], full_address]


def cut_street(street):
    new_street = ""
    if street == "реки Смоленки":
        new_street = "Смоленки"
    elif street == "Набережная Фонтанки":
        new_street = "Фонтанки"
    elif street == "Канонерский остров":
        new_street = "Канонерский"
    elif street == "Воскресенская (Робеспьера)":
        new_street = "Воскресенская"
    elif street == "Петровская":
        new_street = "Петровская коса"
    elif street == "Октябрьская":
        new_street = "Октябрьская наб."
    elif street == "Волковский пр.":
        new_street = "Волковский"

    else:
        new_street = street

    return new_street