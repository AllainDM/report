import time
from datetime import datetime, timedelta
import json
import shutil
import os

from aiogram import Bot, Dispatcher, types, executor
import xlwt

import config
import parser


bot = Bot(token=config.BOT_API_TOKEN)
dp = Dispatcher(bot)

if not os.path.exists(f"files"):
    os.makedirs(f"files")
if not os.path.exists(f"files/ТО Запад"):
    os.makedirs(f"files/ТО Запад")
if not os.path.exists(f"files/ТО Север"):
    os.makedirs(f"files/ТО Север")


# Тестовая функция для проверки даты
@dp.message_handler(commands=['del'])
async def echo_mess(message: types.Message):
    # Получим ид пользователя и сравним со списком разрешенных в файле конфига
    user_id = message.from_user.id
    print(f"user_id {user_id}")
    t_o = ""
    if user_id in config.users:
        # Определим ТО по ид юзера в телеграм
        if user_id == 976374565 or user_id == 1240018773:
            t_o = "ТО Запад"
        elif user_id == 652928171:
            t_o = "ТО Север"
        command = message.get_full_command()[1]  # [1].split('.')
        print(command)
        if len(command) == 10:
            await bot.send_message(message.chat.id, f"Хотим удалить папку /{t_o}/{command}")
            try:
                shutil.rmtree(f"files/{t_o}/{command}")
                print(f"/{t_o}/{command} удален")
                await bot.send_message(message.chat.id, f"Папка /{t_o}/{command} удалена")
            except OSError as error:
                print("Возникла ошибка.")
                await bot.send_message(message.chat.id, f"Папка /{t_o}/{command} не найдена!!!")
        else:
            await bot.send_message(message.chat.id, f"Дата не указана или указана не верно")

    else:
        await bot.send_message(message.chat.id, "Неа")
    # else:
    #     await bot.send_message(message.chat.id, f"Дата введена некорректно")
    #
    # await bot.send_message(message.chat.id, f"test")


@dp.message_handler()
async def echo_mess(message: types.Message):
    # Получим ид пользователя и сравним со списком разрешенных в файле конфига
    user_id = message.from_user.id
    group_id = message.chat.id
    group_id *= -1
    print(f"chat_id {group_id}")
    print(f"user_id {user_id}")
    t_o = ""
    if user_id in config.users or group_id in config.groups:
        # Определим ТО по ид юзера в телеграм 1240018773
        if user_id == 976374565 or user_id == 1240018773:
            t_o = "ТО Запад"
        elif user_id == 652928171:
            t_o = "ТО Север"
        elif group_id == 4066612012:
            t_o = "ТО Запад"
        elif group_id == 1001534981751:
            t_o = "ТО Север"

        # answer = []
        date_now = datetime.now()
        print(f"Текущая дата: {date_now}")
        date_ago = date_now - timedelta(hours=15)  # - hours  # здесь мы выставляем минус 15 часов
        print(f"Новая дата: {date_ago}")
        # date_ago = date_now - timedelta(1)  # здесь мы выставляем минус день
        print(date_ago)
        date_now_year = date_ago.strftime("%d.%m.%Y")
        date_now_no_year = date_ago.strftime("%d.%m")
        # Функция отправки отчета в телеграм по уже собранным данным
        if message.text == "1" or message.text == "отчет" or message.text == "отчёт":
            # Для получения отчета только авторизованный админ
            if user_id in config.users:
                await bot.send_message(message.chat.id, f"Готовим отчет")
                if os.path.exists(f"files/{t_o}/{date_now_year}"):
                    files = os.listdir(f"files/{t_o}/{date_now_year}")
                    await bot.send_message(message.chat.id, f"Найдено {len(files)} файл(ов)")
                    rep_a, num_rep = report(files, date_now_year, t_o)
                    await bot.send_message(message.chat.id, f"Посчитано {num_rep[0]} файл(ов)")

                    # Выведем имена мастеров для сверки
                    rep_masters = ""
                    for i in range(1, len(num_rep)):
                        rep_masters += f'{num_rep[i]} \n'
                    await bot.send_message(message.chat.id, rep_masters)

                    print(files)
                    at_int = rep_a["at_int"]
                    at_int_pri = rep_a["at_int_pri"]
                    at_serv = rep_a["at_serv"]

                    ti_int = rep_a["ti_int"]
                    ti_int_pri = rep_a["ti_int_pri"]
                    ti_serv = rep_a["ti_serv"]

                    et_int = rep_a["et_int"]
                    et_int_pri = rep_a["et_int_pri"]
                    et_tv = rep_a["et_tv"]
                    et_tv_pri = rep_a["et_tv_pri"]
                    et_dom = rep_a["et_dom"]
                    et_dom_pri = rep_a["et_dom_pri"]
                    et_serv = rep_a["et_serv"]
                    et_serv_tv = rep_a["et_serv_tv"]

                    answer = (f"{t_o} {date_now_no_year} \n\n"
                              f"ЭХ: интернет {at_int}({at_int_pri} прив), сервис {at_serv} \n"
                              f"Тиера: интернет {ti_int}({ti_int_pri} прив), сервис {ti_serv} \n"
                              f"ЕТ: интернет {et_int}({et_int_pri} прив), "
                              f"ТВ {et_tv}({et_tv_pri} прив), \n"
                              f"домофон {et_dom}({et_dom_pri} прив), "
                              f"сервис интернет {et_serv}, "
                              f"сервис ТВ {et_serv_tv} \n\n"
                              f"Итого: интернет {at_int + ti_int + et_int}({(at_int_pri + ti_int_pri + et_int_pri)}), "
                              f"ТВ {et_tv}({et_tv_pri}), "
                              f"домофон {et_dom}({et_dom_pri}), "
                              f"сервис {at_serv + ti_serv + et_serv}, "
                              f"сервис ТВ {et_serv_tv}")
                    await bot.send_message(message.chat.id, answer)

                    await bot.send_message(message.chat.id, "Идет подготовка адресов, ожидайте файл.")

                    parser_answer = parser.get_address(rep_a)
                    print(f"parser_answer {parser_answer}")

                    # Сохраним ексель файл с номерами ремонтов
                    # save_to_exel(rep_a, t_o, date_now_year)
                    save_to_exel(parser_answer, t_o, date_now_year)
                    # Попробуем отправить файл
                    exel = open(f"files/{t_o}/{date_now_year}/{date_now_year}.xls", "rb")
                    await bot.send_document(message.chat.id, exel)

                else:
                    await bot.send_message(message.chat.id, f"Папка /{t_o}/{date_now_year} не найдена!!!")

        elif message.text[0].lower() == "у" or message.text[0].lower() == "y":  # Английская y
            # Для получения удаления только авторизованный админ
            if user_id in config.users:
                search_date = message.text.split(" ")
                if len(search_date) > 1:
                    await bot.send_message(message.chat.id, f"Хотим удалить папку /{t_o}/{search_date[1]}")
                    try:
                        shutil.rmtree(f"files/{t_o}/{search_date[1]}")
                        print(f"/{t_o}/{search_date[1]} удален")
                        await bot.send_message(message.chat.id, f"Папка /{t_o}/{search_date[1]} удалена")
                    except OSError as error:
                        print("Возникла ошибка.")
                        await bot.send_message(message.chat.id, f"Папка /{t_o}/{search_date[1]} не найдена!!!")
                else:
                    await bot.send_message(message.chat.id, f"Дата не указана или указана не верно")
        elif message.text[0].lower() == "ф":  # or message.text[0].lower() == "y":  # Английская y
            # Для получения удаления только авторизованный админ
            if user_id in config.users:
                search_master = message.text.split(" ")
                if len(search_master) > 1:
                    await bot.send_message(message.chat.id, f"Хотим удалить файл /{t_o}/{date_now_year}/{search_master[1]}")
                    try:
                        os.remove(f"files/{t_o}/{date_now_year}/{search_master[1]}.json")
                        print(f"/{t_o}/{date_now_year}/{search_master[1]} удален")
                        await bot.send_message(message.chat.id, f"Файл /{t_o}/{date_now_year}/{search_master[1]} удален")
                    except OSError as error:
                        print("Возникла ошибка.")
                        await bot.send_message(message.chat.id, f"Файл /{t_o}/{date_now_year}/{search_master[1]} не найден!!!")
                else:
                    await bot.send_message(message.chat.id, f"Файл не указан или указан не верно")
        # Парсер сообщений и сохранение в файл
        else:
            try:
                # Создадим папку за текущий день если не существует
                if not os.path.exists(f"files/{t_o}/{date_now_year}"):
                    os.makedirs(f"files/{t_o}/{date_now_year}")

                at_int = 0
                at_int_pri = 0
                at_serv = 0

                ti_int = 0
                ti_int_pri = 0
                ti_serv = 0

                et_int = 0
                et_int_pri = 0
                et_tv = 0
                et_tv_pri = 0
                et_dom = 0
                et_dom_pri = 0
                et_serv = 0
                et_serv_tv = 0

                # Создадим флаги для поиска ошибок
                at_int_flag = 0
                at_int_pri_flag = 0
                at_serv_flag = 0

                ti_int_flag = 0
                ti_int_pri_flag = 0
                ti_serv_flag = 0

                et_int_flag = 0
                et_int_pri_flag = 0
                et_tv_flag = 0
                et_tv_pri_flag = 0
                et_dom_flag = 0
                et_dom_pri_flag = 0
                et_serv_flag = 0
                et_serv_tv_flag = 0

                # Разбиваем по ":", так мы определим провайдер
                pre_txt_lower = message.text.lower()
                print(f"pre_txt_lower {pre_txt_lower}")
                pre_txt = (pre_txt_lower.replace("тв:", "тв").
                           replace("ис:", "ис").
                           replace("нет:", "нет").
                           replace("он:", "он"))
                print(f"pre_txt {pre_txt}")
                # txt = message.text.split(":")
                txt = pre_txt.split(":")
                print(f"txt {txt}")

                # Строчка ЭтХоум
                # print(f"тут1 {txt[1]}")
                # Заменим скобки и перенос строки пробелами и разобьем на список
                new_txt_at = (txt[1].replace("(", " ").
                              replace(")", " ").
                              replace("\n", " ").
                              replace(",", " ").
                              replace(":", "").
                              replace("\xa0", " ").
                              replace(".", " "))
                new_txt_at_list = new_txt_at.split(" ")
                print(new_txt_at_list)

                # Сделаем перебор нового списка, где значения будем искать после ключевых слов
                for num, val in enumerate(new_txt_at_list):
                    # print(f"111 {num, val}")
                    if val.lower() == "интернет":
                        try:
                            at_int = int(new_txt_at_list[num + 1])  # Следующее значение после "интернет"
                            at_int_flag = 1  # Флаг для проверки правильности отчета
                        except ValueError:
                            at_int = 0
                    elif val[0:4].lower() == "прив":  # or val[0:5].lower() == "привл"
                        try:
                            at_int_pri = int(new_txt_at_list[num - 1])  # Перед "прив"
                            at_int_pri_flag = 1  # Флаг для проверки правильности отчета
                        except ValueError:
                            at_int_pri = 0
                    elif val.lower() == "сервис":
                        try:
                            at_serv = int(new_txt_at_list[num + 1])  # После "сервис"
                            at_serv_flag = 1  # Флаг для проверки правильности отчета
                        except ValueError:
                            at_serv = 0

                # Строчка Тиера
                new_txt_ti = (txt[2].replace("(", " ").
                              replace(")", " ").
                              replace("\n", " ").
                              replace(",", " ").
                              replace(":", "").
                              replace("\xa0", " ").
                              replace(".", " "))
                new_txt_ti_list = new_txt_ti.split(" ")
                print(new_txt_ti_list)

                # Сделаем перебор нового списка, где значения будем искать после ключевых слов
                for num, val in enumerate(new_txt_ti_list):
                    # print(f"111 {num, val}")
                    if val.lower() == "интернет":
                        try:
                            ti_int = int(new_txt_ti_list[num + 1])  # Следующее значение после "интернет"
                            ti_int_flag = 1  # Флаг для проверки правильности отчета
                        except ValueError:
                            ti_int = 0
                    elif val[0:4].lower() == "прив":
                        try:
                            ti_int_pri = int(new_txt_ti_list[num - 1])  # Перед "прив"
                            ti_int_pri_flag = 1  # Флаг для проверки правильности отчета
                        except ValueError:
                            ti_int_pri = 0
                    elif val.lower() == "сервис":
                        try:
                            ti_serv = int(new_txt_ti_list[num + 1])  # После "сервис"
                            ti_serv_flag = 1  # Флаг для проверки правильности отчета
                        except ValueError:
                            ti_serv = 0

                # Строчка Е-телеком
                new_txt_et = (txt[3].replace("(", " ").
                              replace(")", " ").
                              replace("\n", " ").
                              replace(",", " ").
                              replace(":", "").
                              replace("\xa0", " ").
                              replace(".", " "))
                new_txt_et_list = new_txt_et.split(" ")
                print(new_txt_et_list)

                # Сделаем перебор нового списка, где значения будем искать после ключевых слов
                # Сделаем несколько флагов, для разделения сервисов и привлеченных
                flag_priv_int = 0
                flag_priv_tv = 0
                flag_priv_dom = 0
                # flag_tv = 0
                # flag_serv_int = 0
                # flag_serv_tv = 0

                for num, val in enumerate(new_txt_et_list):
                    # print(f"111 {num, val}")
                    if val.lower() == "интернет" and new_txt_et_list[num - 1].lower() != "сервис":
                        # print(f"тут интернет {new_txt_et_list[num + 1]}")
                        try:
                            et_int = int(new_txt_et_list[num + 1])  # Следующее значение после "интернет"
                            et_int_flag = 1  # Флаг для проверки правильности отчета
                        except ValueError:
                            et_int = 0
                    elif val[0:4].lower() == "прив":
                        print(f" тут какой то val1 {val}")
                        print(f" тут какой то val2 {val[0:4]}")
                        if flag_priv_int == 0:  # Флаг привлеченного интернета
                            # print(f"тут прив интернет {new_txt_et_list[num - 1]}")
                            flag_priv_int += 1
                            try:
                                et_int_pri = int(new_txt_et_list[num - 1])  # Перед "прив"
                                et_int_pri_flag = 1  # Флаг для проверки правильности отчета
                            except ValueError:
                                et_int_pri = 0
                        elif flag_priv_tv == 0:  # Флаг привлеченного тв
                            # print(f"тут прив тв {new_txt_et_list[num - 1]}")
                            flag_priv_tv += 1
                            try:
                                et_tv_pri = int(new_txt_et_list[num - 1])  # Перед "прив"
                                et_tv_pri_flag = 1  # Флаг для проверки правильности отчета
                            except ValueError:
                                et_tv_pri = 0
                        elif flag_priv_dom == 0:  # Флаг привлеченного домофона
                            # print(f"тут прив домофон {new_txt_et_list[num - 1]}")
                            flag_priv_dom += 1
                            try:
                                et_dom_pri = int(new_txt_et_list[num - 1])  # Перед "прив"
                                et_dom_pri_flag = 1  # Флаг для проверки правильности отчета
                            except ValueError:
                                et_dom_pri = 0
                    # Сочетание тв
                    elif val.lower() == "тв":
                        if new_txt_et_list[num - 1].lower() == "сервис":
                            # print("тут сервис тв")
                            try:
                                et_serv_tv = int(new_txt_et_list[num + 1])  # После "тв"
                                et_serv_tv_flag = 1  # Флаг для проверки правильности отчета
                            except ValueError:
                                et_serv_tv = 0
                            except IndexError:  # После сервисов тв часто не ставят значение, а это конец сообщения
                                et_serv_tv = 0
                        else:
                            # print("тут подключение тв")
                            # print(new_txt_et_list[num + 1])
                            try:
                                et_tv = int(new_txt_et_list[num + 1])  # После "тв"
                                et_tv_flag = 1  # Флаг для проверки правильности отчета
                            except ValueError:
                                et_tv = 0
                            except IndexError:  # После сервисов тв часто не ставят значение, а это конец сообщения
                                et_tv = 0
                    elif val.lower() == "домофон":
                        try:
                            et_dom = int(new_txt_et_list[num + 1])  # После "домофон"
                            et_dom_flag = 1  # Флаг для проверки правильности отчета
                        except ValueError:
                            et_dom = 0
                    elif val.lower() == "сервис" and new_txt_et_list[num + 1].lower() == "интернет":
                        try:
                            et_serv = int(new_txt_et_list[num + 2])  # + 2
                            et_serv_flag = 1  # Флаг для проверки правильности отчета
                        except ValueError:
                            et_serv = 0

                to_save = {
                    "at_int": at_int,
                    "at_int_pri": at_int_pri,
                    "at_serv": at_serv,

                    "ti_int": ti_int,
                    "ti_int_pri": ti_int_pri,
                    "ti_serv": ti_serv,

                    "et_int": et_int,
                    "et_int_pri": et_int_pri,
                    "et_tv": et_tv,
                    "et_tv_pri": et_tv_pri,
                    "et_dom": et_dom,
                    "et_dom_pri": et_dom_pri,
                    "et_serv": et_serv,
                    "et_serv_tv": et_serv_tv,
                    'master': "не указан",
                    'msg_err_txt': ""  # Запись текста с возможными ошибками
                }

                print(message)
                # Найдем фамилию мастера
                if message.forward_from is not None:
                    if message.forward_from.last_name:
                        to_save["master"] = message.forward_from.last_name
                    elif message.forward_from.first_name:
                        to_save["master"] = message.forward_from.first_name
                elif message.forward_sender_name is not None:
                    to_save["master"] = message.forward_sender_name
                else:
                    to_save["master"] = "не указан"

                # Выставим мастера вручную
                if to_save["master"] == "Sergey":
                    to_save["master"] = "Дьяков"
                elif to_save["master"] == "Александр ЛюТЫй":
                    to_save["master"] = "Михайлюта"
                elif to_save["master"] == "Vladimir":
                    to_save["master"] = "Рябов"
                elif to_save["master"] == "Сеня":
                    to_save["master"] = "Федоров"
                elif to_save["master"] == "Vitaly":
                    to_save["master"] = "Ким"
                elif to_save["master"] == "Koma":
                    to_save["master"] = "Комаревцев"
                elif to_save["master"] == "Рус":
                    to_save["master"] = "Хуснутдинов"
                elif to_save["master"] == "Тимур":
                    to_save["master"] = "Давлетшин"
                elif to_save["master"] == "Антон Erk0o":
                    to_save["master"] = "Митюхин"
                elif to_save["master"] == "Jack":
                    to_save["master"] = "Янюк"
                elif to_save["master"] == "B":
                    to_save["master"] = "Бондаренко"
                elif to_save["master"] == "mifik":
                    to_save["master"] = "Минаков"
                elif to_save["master"] == "Леонид":
                    to_save["master"] = "Алексеев"

                elif to_save["master"] == "Anatoliy Chernykh":
                    to_save["master"] = "Черных"
                elif to_save["master"] == "Князь Владимир":
                    to_save["master"] = "Гончар"
                elif to_save["master"] == "Бодашков Евгений Борисович":
                    to_save["master"] = "Бодашков"
                elif to_save["master"] == "Nikitin":
                    to_save["master"] = "Никитин"
                elif to_save["master"] == "Ailing":
                    to_save["master"] = "Коряков"
                elif to_save["master"] == "ilya":
                    to_save["master"] = "Никифоров"
                elif to_save["master"] == "Vasilev":
                    to_save["master"] = "Васильев"
                elif to_save["master"] == "Александр":
                    to_save["master"] = "Комиссаров"

                # Но, если в начале сообщения есть фамилия, то возьмем ее.
                txt_soname_pre = txt[0].replace("\n", " ")
                txt_soname = txt_soname_pre.split(" ")
                if txt_soname[0].lower() != 'эх':
                    to_save["master"] = txt_soname[0].title()

                if to_save["master"] == "не указан":
                    await bot.send_message(message.chat.id, "Необходимо указать фамилию мастера, отчет не сохранен.")
                    return

                # Сообщение об ошибке на основе флагов
                msg_err = []
                # msg_err_txt = ""

                if at_int_flag == 0:
                    msg_err.append("ЭтХоум интернет. ")

                if at_int_pri_flag == 0:
                    msg_err.append("ЭтХоум интернет привлеченный. ")
                if at_serv_flag == 0:
                    msg_err.append("ЭтХоум сервис. ")

                if ti_int_flag == 0:
                    msg_err.append("Тиера интернет. ")
                if ti_int_pri_flag == 0:
                    msg_err.append("Тиера интернет привлеченный. ")
                if ti_serv_flag == 0:
                    msg_err.append("Тиера сервис. ")

                if et_int_flag == 0:
                    msg_err.append("ЕТ интернет. ")
                if et_int_pri_flag == 0:
                    msg_err.append("ЕТ интернет привлеченный. ")
                if et_tv_flag == 0:
                    msg_err.append("ЕТ тв. ")
                if et_tv_pri_flag == 0:
                    msg_err.append("ЕТ тв привлеченный. ")
                if et_dom_flag == 0:
                    msg_err.append("ЕТ домофон. ")
                if et_dom_pri_flag == 0:
                    msg_err.append("ЕТ домофон привлеченный. ")
                if et_serv_flag == 0:
                    msg_err.append("ЕТ сервис. ")
                if et_serv_tv_flag == 0:
                    msg_err.append("ЕТ сервис тв. ")

                if len(msg_err) > 0:
                    msg_err_txt = f""
                    for e in msg_err:
                        msg_err_txt += e
                    # Стандартный текст передается тут, а не сохраняется
                    await bot.send_message(message.chat.id,
                                           f"Внимание, возможна ошибка с отчетом мастера "
                                           f"{to_save['master']}: {msg_err_txt} Отчет не сохранен.")
                    return
                    # Неактуально если отчет не сохраняется?
                    # Сохраним имя мастера и ошибки в файл, для доп вывода при запросе общего за 1 день
                    # to_save["msg_err_txt"] = f"{to_save['master']} {msg_err_txt}. "

                # Так же создадим список для сохранения номеров ремонтов
                list_repairs = []

                # После получения мастера соберем список ремонтов
                # Запишем номера ремонтов в ЭтХоум
                # Заменим скобки и перенос строки пробелами и разобьем на список
                repairs_txt_at = (txt[1].replace("(", " ").
                                  replace(")", " ").
                                  replace("\n", " ").
                                  replace("#", " ").
                                  replace("e", " ").        # Английская. Тут мастера могут записать етм
                                  replace("е", " ").        # Русская
                                  replace(",", " ").
                                  replace("\xa0", " ").
                                  replace(".", " "))
                repairs_txt_at_list = repairs_txt_at.split(" ")

                for i in repairs_txt_at_list:
                    if len(i) == 7 and i.isnumeric():
                        print(f"i1 {i}")
                        list_repairs.append(['ЭтХоум', i, to_save["master"]])
                    # else:
                    #     print(f"{i} не подходит")

                # Запишем номера ремонтов в Тиере
                # Заменим скобки и перенос строки пробелами и разобьем на список
                repairs_txt_ti = (txt[2].replace("(", " ").
                                  replace(")", " ").
                                  replace("\n", " ").
                                  replace("#", " ").
                                  replace("e", " ").        # Английская. Тут мастера могут записать етм
                                  replace("е", " ").        # Русская
                                  replace(",", " ").
                                  replace("\xa0", " ").
                                  replace(".", " "))
                repairs_txt_ti_list = repairs_txt_ti.split(" ")

                for i in repairs_txt_ti_list:
                    if len(i) == 7 and i.isnumeric():
                        print(f"i2 {i}")
                        list_repairs.append(['Тиера', i, to_save["master"]])
                    # else:
                    #     print(f"{i} не подходит")

                # Запишем номера ремонтов в ЕТ
                # Заменим скобки и перенос строки пробелами и разобьем на список
                repairs_txt_et = (txt[3].replace("(", " ").
                                  replace(")", " ").
                                  replace("\n", " ").
                                  replace("#", " ").
                                  replace("e", " ").        # Английская. Тут мастера могут записать етм
                                  replace("е", " ").        # Русская
                                  replace(",", " ").
                                  replace("\xa0", " ").
                                  replace(".", " "))
                repairs_txt_et_list = repairs_txt_et.split(" ")
                print(f"repairs_txt_et {repairs_txt_et}")

                for i in repairs_txt_et_list:
                    if len(i) == 7 and i.isnumeric():
                        # print(f"i3 {i}")
                        list_repairs.append(['ЕТ', i, to_save["master"]])
                    # else:
                    #     print(f"{i} не подходит")

                # Добавим к сохраняемым данным список с ремонтами

                to_save["list_repairs"] = list_repairs

                # Сохраним в файл
                with open(f'files/{t_o}/{date_now_year}/{to_save["master"]}.json', 'w') as outfile:
                    json.dump(to_save, outfile, sort_keys=False, ensure_ascii=False, indent=4, separators=(',', ': '))

                answe1 = (f"{t_o} {date_now_no_year}. Мастер {to_save['master']} \n\n"
                          f"ЭХ: интернет {at_int}({at_int_pri} прив), сервис {at_serv} \n" 
                          f"Тиера: интернет {ti_int}({ti_int_pri} прив), сервис {ti_serv} \n" 
                          f"ЕТ: интернет {et_int}({et_int_pri} прив), "
                          f"ТВ {et_tv}({et_tv_pri} прив), \n"
                          f"домофон {et_dom}({et_dom_pri} прив), "
                          f"сервис интернет {et_serv}, "
                          f"сервис ТВ {et_serv_tv} \n\n"
                          f"Итого: интернет {at_int + ti_int + et_int}({(at_int_pri + ti_int_pri + et_int_pri)}), "
                          f"ТВ {et_tv}({et_tv_pri}), "
                          f"домофон {et_dom}({et_dom_pri}), "
                          f"сервис {at_serv + ti_serv + et_serv}, "
                          f"сервис ТВ {et_serv_tv}")

                print(answe1)
                await bot.send_message(message.chat.id, f"{answe1}")
                # Используем функцию подсчета файлов для вывода посчитанных мастеров
                # TODO возможно лучше создать отдельную функцию
                if os.path.exists(f"files/{t_o}/{date_now_year}"):
                    files = os.listdir(f"files/{t_o}/{date_now_year}")
                    rep_a, num_rep = report(files, date_now_year, t_o)

                    # Выведем имена мастеров для сверки
                    rep_masters = "Получены отчеты: \n"
                    for i in range(1, len(num_rep)):
                        rep_masters += f'{num_rep[i]} \n'
                    await bot.send_message(message.chat.id, rep_masters)
            except IndexError:
                print("Тут видимо сообщение не относящееся к отчету.")

    else:
        await bot.send_message(message.chat.id, "Вы не авторизованны")
        await bot.send_message(message.chat.id, f"chat_id {group_id}")
        await bot.send_message(message.chat.id, f"user_id {user_id}")

        print(f"chat_id {group_id}")
        print(f"user_id {user_id}")


def save_to_exel(list_to_exel, t_o, date):
    print("Запуск функции сохранения в ексель файл.")
    wb = xlwt.Workbook()
    # ws = wb.add_sheet(f'{table_name}')
    ws = wb.add_sheet(date)
    # print(f"list_repairs111 {list_to_exel['list_repairs']}")

    # for n, v in enumerate(list_to_exel["list_repairs"]):
    # for n, v in enumerate(list_to_exel):
    for n, v in enumerate(list_to_exel):
        ws.write(n, 0, v[0])  # Бренд
        ws.write(n, 1, date)  # Дата
        ws.write(n, 3, v[1])  # Номер
        ws.write(n, 7, v[2])  # Мастер
        ws.write(n, 4, v[3][0])  # Улица
        ws.write(n, 5, v[3][1])  # Дом
        ws.write(n, 6, v[3][2])  # Квартира
        ws.write(n, 17, f"=ГИПЕРССЫЛКА(CONCAT($Y$2;D{n+1});D{n+1})")  # Ссылка

    # Гиперссылка
    ws.write(1, 24, "https://us.gblnet.net/oper/?core_section=task&action=show&id=")

    # date_now = datetime.now()
    # ws.write(0, 0, f"Версия 005 Время: {date_now}")

    wb.save(f'files/{t_o}/{date}/{date}.xls')
    print("Документ сохранен")


def report(files, date, t_o):
    to_save = {
        "at_int": 0,
        "at_int_pri": 0,
        "at_serv": 0,

        "ti_int": 0,
        "ti_int_pri": 0,
        "ti_serv": 0,

        "et_int": 0,
        "et_int_pri": 0,
        "et_tv": 0,
        "et_tv_pri": 0,
        "et_dom": 0,
        "et_dom_pri": 0,
        "et_serv": 0,
        "et_serv_tv": 0,
        "list_repairs": [],
        "msg_err_txt": []
    }
    # Возвращаем количество отчетов для сверки. Первый индекс количество, остальные фамилии мастеров
    rep = [0]
    # masters = []
    for file in files:
        print(f"Попробуем наладить фильтр по названию файла {file}")
        print(f"Попробуем наладить фильтр по названию файла {file[-4:]}")
        if file[-4:] == "json":
            with open(f'files/{t_o}/{date}/{file}', 'r', encoding='utf-8') as outfile:
                # , errors='ignore'
                # data = json.load(outfile)
                print(f"будем искать такой файл: {file}")
                data = json.loads(outfile.read())
                print(data)
                to_save["at_int"] += data["at_int"]
                to_save["at_int_pri"] += data["at_int_pri"]
                to_save["at_serv"] += data["at_serv"]

                to_save["ti_int"] += data["ti_int"]
                to_save["ti_int_pri"] += data["ti_int_pri"]
                to_save["ti_serv"] += data["ti_serv"]

                to_save["et_int"] += data["et_int"]
                to_save["et_int_pri"] += data["et_int_pri"]
                to_save["et_tv"] += data["et_tv"]
                to_save["et_tv_pri"] += data["et_tv_pri"]
                to_save["et_dom"] += data["et_dom"]
                to_save["et_dom_pri"] += data["et_dom_pri"]
                to_save["et_serv"] += data["et_serv"]
                to_save["et_serv_tv"] += data["et_serv_tv"]
                rep[0] += 1  # Добавим счетчик количества посчитанных
                rep.append(data["master"])  # Добавим фамилию мастера
                # Сложим так же все номера ремонтов
                to_save["list_repairs"] += data["list_repairs"]

    # Сохраним в файл
    # Хотя необходимости нет?
    with open(f'files/{t_o}/{date}.json', 'w') as outfile:
        json.dump(to_save, outfile, sort_keys=False, ensure_ascii=False, indent=4, separators=(',', ': '))

    return to_save, rep


# def search_reports():
#     ...


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
