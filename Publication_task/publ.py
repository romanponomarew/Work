import requests
from bs4 import BeautifulSoup #библиотека для парсинга
import json
from fake_useragent import UserAgent #Для рандомного выбора программы-клиента запросов
from random import choice #рандомный выбор из списка


def author_annotation(author_start, author_end, current_publication):
    # author_start - Номер автора(publications.json) с которого продолжить загрузки
    # author_end - Номер автора(publications.json) на котором омтановить загрузку
    # current_publication - сколько статей загружено на данный момент в файл(data.json)

    # Создание списка с номером автора = ['4', '5', '6', '7']
    global spis
    spis = []
    #Заполнение списка описываемых авторов (по их номерам)
    for i in range(author_start, author_end): #for i in range(1693, 2449):
        spis.append(str(i))

    #Создание промежуточного словаря с id публикаций в соответствии каждому автору:
    global data1
    data1 = {}
    with open("publications.json", "r") as read_file:
        data = json.load(read_file)

        for i in data:
            for n in spis:
                if i == n:
                    data1[i] = data[i]
    # print(data)
    # print(data1)

    # counts = 750 #Начиная с этого номера беру только по 5 публикаций от одного автора
    # counts = 10011
    global counts    #Номер аннотации в существующем файле json, чтобы продолжать с этого места
    counts = current_publication + 1 #counts = 10417


def auth_session(): #Пример авторизованных запросов:
    datas = {
        'login': 'def',
        'password': 'def'
    }

    datas['login'] = 'romanponomarew'
    datas['password'] = 'password'

    url = 'https://www.elibrary.ru/defaultx.asp'

    s = requests.Session() #Создание сессии
    loging = s.post(url, data=datas, headers=headers, proxies = proxy)
    response18 = s.get(url, data=datas, headers=headers, proxies = proxy)

def rand_headers(): # Создание рандомного клиента с помощью fake_useragent
    ua1 = UserAgent()
    headers = {'User-Agent': str(ua1.random)}
    return headers


def my_ip(): #Функция определения своего ip с помощью парсинга сайта http://sitespy.ru/my-ip
    response1 = requests.get("http://sitespy.ru/my-ip", headers=headers, proxies=proxy)
    #print(response1.text)
    print('---------------')
    soup = BeautifulSoup(response1.text, 'lxml')
    ip = soup.find('span', class_ = 'ip').text.strip()
    ua = soup.find('span', class_ = 'ip').find_next_sibling('span').text.strip()
    print(ip)
    print(ua)
    print('-----------')

def proxy_random():
    global rand_proxy, proxy
    rand_proxy = choice(proxy_list)
    proxy = {'https': 'https://' + rand_proxy}
    return rand_proxy, proxy


def parsing(): #Парсинг сайта elibrary.ru
    # и создание словаря slovar1 = {0: {"id_author": [], "id_publication": [], "name_publ": [], "annotation": []}}
    global slovar1, counts

    proxy_random() #Случайный выбор прокси из списка прокси-серверов
    # Ключ - порядковый номер автора:
    for author in data1:
        print("author_num=", author)
        print("publications_num= ", data1[author]["num_publications"])
        count_publ = 0
        # Вытаскиваем id автора:
        for publ in data1[author]["publications"]:
            count_publ += 1
            if count_publ == 4:
                break
            slovar1[counts] = {}
            slovar1[counts]["id_author"] = data1[author]["id_author"]
            slovar1[counts]["id_publication"] = publ
            popitki = 0

            while popitki < 170:
                print(f"Попытка №{popitki} с прокси = {proxy}")
                try:
                    print("try with proxy=", proxy)
                    print("Номер статьи = ", counts)
                    response = requests.get(f"https://elibrary.ru/item.asp?id={publ}", headers=headers,
                                        proxies=proxy, verify=False, timeout=3)
                    print(response.status_code)
                    bs = BeautifulSoup(response.text, 'html.parser')
                    publ_name = bs.find("head").text
                    slovar1[counts]["num_publ"] = list(filter(None, publ_name.splitlines()))
                    publ_text = bs.find("head")
                    slovar2 = slovar1
                    # Парсинг аннотации со страницы
                    count = 0
                    for tag in publ_text.find_all("meta"):
                        count = count + 1
                        if count == 2:
                            slovar1[counts]["annotation"] = list(filter(None, tag.get("content", None).splitlines()))
                    #Запись промежуточных результатов в файл на случай того, что программа недоработает
                    with open("data.json(3)", "w", encoding="utf-8", ) as file:
                        json.dump(slovar2, file, ensure_ascii=False)

                    if True:
                        popitki = 200

                except:
                    print("Не получается получить аннотацию к статье с прокси = ", rand_proxy)
                    print(f"Удаляем прокси {rand_proxy} из списка ")
                    global proxy_list
                    proxy_list.remove(rand_proxy)
                    print("Кол-во прокси серверов в списке=", len(proxy_list))
                    # rand_proxy = choice(proxy_list)
                    # proxy = {'https': 'https://' + rand_proxy}
                    proxy_random() # Замена прокси-сервера
                    popitki = popitki + 1
            counts = counts + 1
    print(slovar1)
    return slovar1

def append_json(): # Дозаписывание полученного словаря в существующий файл json
    with open("data.json", "a", encoding="utf-8", ) as file:
        json.dump(slovar1, file, ensure_ascii=False)


if __name__ == '__main__':

    #Создание списка прокси-серверов из файла:
    # proxy = {'https': 'https://8.9.37.53:8080'}
    # proxy_list = [{'https': 'https://45.77.153.252:8080'}, {'https': 'https://138.197.120.248:3128'}]
    proxy_list = open('proxies(7).txt').read().split('\n')

    #Назначение программы-клиента для запросов:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/78.0.3904.97 Safari/537.36"}

    #Вид финального словаря:
    slovar1 = {0: {"id_author": [], "id_publication": [], "name_publ": [], "annotation": []}}

    #Определение с какой статьи, автора начать заполнение и где закончить
    author_annotation(1693, 2449, 10416) #author_start, author_end, current_publication

    #Первоначальное определение прокси-сервера:
    proxy_random()

    parsing()  # Парсинг сайта elibrary.ru

    append_json() # Дозаписывание полученного словаря в существующий файл json

