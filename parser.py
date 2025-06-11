import time
import re
from importlib.metadata import files

import requests
from bs4 import BeautifulSoup
import lxml

import config

url_login_get = "https://us.gblnet.net/"
url_login = "https://us.gblnet.net/body/login"
url = "https://us.gblnet.net/dashboard"


HEADERS = {
    "main": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0"
}

data_users = {
    "_csrf": '',
    "return_page": "",
    "username": config.loginUS,
    "password": config.pswUS
}

session_users = requests.Session()
# session_users.headers.update(HEADERS)

req = session_users.get(url_login_get)
# req = requests.get(url_login)

csrf = None

def get_token():
    global csrf
    soup = BeautifulSoup(req.content, 'html.parser')
    # print(soup)
    print("###################")
    scripts = soup.find_all('script')

    for script in scripts:
        if script.string is not None:
            # print(script.string)
            script_lst = script.string.split(" ")
            # print(script_lst)
            for num, val in enumerate(script_lst):
                if val == "_csrf:":
                    csrf = script_lst[num+1]
    print(f"csrf {csrf}")



def create_users_sessions():
    global csrf
    while True:
        try:
            get_token()
            data_users["_csrf"] = csrf[1:-3]
            print(data_users)
            response_users2 = session_users.post(url_login, data=data_users, headers=HEADERS).text
            print("Сессия Юзера создана 2")
            # print(response_users2)
            return response_users2
        except ConnectionError:
            print("Ошибка создания сессии")
            # TODO функция отправки тут отсутствует
            # send_telegram("Ошибка создания сессии UserSide, повтор запроса через 5 минут")
            # time.sleep(300)


response_users = create_users_sessions()


# TODO необходимо будет сделать одну функция под множество запросов
def get_address(list_service_masters):
    global response_users
    response_users = create_users_sessions()
    print("Что у нас в аргументе")
    print(list_service_masters)
    print(f'list_service_masters {list_service_masters["list_repairs"]}')
    list_repairs = list_service_masters["list_repairs"]
    id_ls = {"user_id": "", "user_ls": ""}
    for v in list_repairs:
        print(f"v: {v}")
        service = v[1]
        # link = f"https://us.gblnet.net/oper/?core_section=task&action=show&id={service}"
        link = f"https://us.gblnet.net/task/{service}"
        print("link 111")
        print(link)
        time.sleep(config.delay)  # Небольшая задержка
        try:
            HEADERS["_csrf"] = csrf[1:-3]
            print(f"HEADERS: {HEADERS}")
            print("Пытаемся получить страничку")
            print(f"Токен: {csrf}")
            html = session_users.get(link, headers=HEADERS)
            print(html)
            if html.status_code == 200:
                print("Код ответа 200")
                # soup = BeautifulSoup(html.text, 'lxml')
                soup = BeautifulSoup(html.text, 'html.parser')
                # print(f"soup {soup}")
                table = soup.find('table', class_="j_table")
                # print(f"table {table}")
                if table is None:
                    v.append([" ", " ", " ", " "])
                    v.append("!!! Внимание, возможно не верный номер сервиса 1.")
                    v.append(" ")
                    v.append(" ")
                    print("!!! Внимание, возможно не верный номер сервиса 1.")
                else:
                    # Так же сразу найдем тип задания. Главная страница - UserSide
                    table_type_task = soup.find(class_="label_h2")
                    table_type_task_span = table_type_task.find('span')
                    print(f"Тут может быть таск: {table_type_task_span.text}")
                    table_a = table.find_all('a')
                    print("Парсим ссылки")
                    print(table_a)
                    if table_a:
                        answer_parser_address = ""
                        for i in table_a:
                            if 'Россия' in i.text:
                                answer_parser_address = parser_address(i.text)
                                v.append(answer_parser_address)
                                print(f"answer_parser_address: {answer_parser_address}")
                                # Так же в любом случае добавляем полученный тип задания.
                                v.append(table_type_task_span.text)

                        if answer_parser_address == "":
                            print("Адрес не найден")
                            v.append([" ", " ", " ", " "])
                            v.append("!!! Внимание, возможно не верный номер сервиса 2.")
                            v.append(" ")
                            v.append(" ")
                            print("!!! Внимание, возможно не верный номер сервиса 2.")
                        # Еще раз отдельный цикл по ссылкам уже в поиске ид и лс
                        print("Запишем индексы для ИД и ЛС.")
                        # v.append({"id": " "})  # ID
                        # v.append({"ls": " "})  # ЛС
                        user_id = ""
                        user_ls = ""
                        print("Записали индексы для ИД и ЛС.")
                        # check_ls = []
                        for tab_test in table_a:
                            # print(f"тест ссылок: {tab_test}")
                            # print(f"тест ссылок текст: {tab_test.text}")
                            test_a = tab_test.text.split(" ")
                            # print(f"test_a: {test_a}")
                            for num, el in enumerate(test_a):
                                if el == "ID:":
                                    user_id = test_a[num+1]
                                    id_ls["user_id"] = test_a[num+1]
                                    print(f"Найден ид юзера: {id_ls['user_id']}")
                                if el == "договор:":
                                    user_id = test_a[num+1]
                                    id_ls["user_ls"] = test_a[num+1]
                                    print(f"Найден лс юзера: {id_ls['user_ls']}")
                        houm_ls_table = soup.find(class_="taskCustomerFullInfo")
                        houm_ls_table_list = houm_ls_table.text.split(" ")
                        for num, el in enumerate(houm_ls_table_list):
                            if el == "договор:":
                                print(f"el !!!!!!!!! {el}")
                            # user_id = houm_ls_table_list[num+1]
                            # id_ls["user_ls"] = houm_ls_table_list[num+1]
                            # print(f"Найден лс юзера: {id_ls['user_ls']}")


                                # if el == "-":
                                #     # ЛС может быть с _ это ЭтХоумовский логин, он не подходит
                                #     check_ls = test_a[num+1].split()
                                #     # Авансом привяжем как у ЕТ, позже обработаем не в этом цикле
                                #     id_ls["user_ls"] = test_a[num+1]
                                #     user_ls = test_a[num+1]
                                #     print(f"Найден лс юзера: {id_ls['user_ls']}")
                                #     if "_" in check_ls[0]:
                                #         print("Это Этхоумовский логин")
                                #         # В этом случае надо снова пройтись по таблице в поисках нужного класса
                                #         table_for_ls = table.find(class_="taskCustomerFullInfo")
                                #         table_for_ls = table_for_ls.text.split(" ")
                                #         for l in table_for_ls:
                                #             if l[0:3] == "руб":
                                #                 id_ls["user_ls"] = l[4:11]
                                #                 user_ls = l[4:11]
                                #             if l[0:12] == "лицевой счет":
                                #                 id_ls["user_ls"] = l[15:123]
                                #                 user_ls = l[15:23]
                                #     else:
                                #         id_ls["user_ls"] = test_a[num+1]
                                #         user_ls = test_a[num+1]
                                #     print(f"Найден лс юзера: {id_ls['user_ls']}")
                        print("Таблица проверена.")

                        v.append(user_ls)
                        v.append(user_id)

                    else:
                        v.append([" ", " ", " ", " "])
                        v.append("!!! Внимание, возможно не верный номер сервиса 3.")
                        v.append(" ")
                        v.append(" ")
                        print("!!! Внимание, возможно не верный номер сервиса 3.")
                print("###############################################################################################")
                print("###############################################################################################")
            else:
                print("error")
        except requests.exceptions.TooManyRedirects as e:
            print(f'{link} : {e}')
    return list_repairs, id_ls


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
            address[3] == " Новогорелово пос." or \
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
            # print(f"el: {el}")
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
