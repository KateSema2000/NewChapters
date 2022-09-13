from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import DesiredCapabilities
from telegram import Update, ReplyKeyboardMarkup
from datetime import datetime, timedelta
from selenium import webdriver
from bs4 import BeautifulSoup
import cloudinary.uploader

import bot_token
from utils.xml_help import *
import requests
from utils import help
import time
import os

chrome_options = webdriver.chrome.options.Options()
chrome_options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("start-maximized")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36")
caps = DesiredCapabilities().CHROME
caps["pageLoadStrategy"] = "none"

wait_to_load = 10

_local = "local"
_heroku = "heroku"

_now = _heroku


def get_driver():
    if _now == _local:
        driver = webdriver.Chrome(desired_capabilities=caps)
        return driver
    else:
        return webdriver.Chrome(executable_path=os.environ.get('CHROMEDRIVER_PATH'), options=chrome_options,
                                desired_capabilities=caps)


# То как создавать потоки !! в хероку не работает !!
# import threading

# def tread_f(args):
#     url = args[0]
#     print(url)
#     driver = get_driver()
#     driver.get(url)
#     print(url, str(len(driver.page_source)))
#     driver.quit()
#
#
# threats = []
# for url in ['https://ficbook.net/readfic/6511856',
#             'https://readmanga.io/19_dnei___odnajdy',
#             'https://mintmanga.live/tiran__kotoryi_vliubilsia__A5327',
#             'https://mintmanga.live/slovno_dikii_zver__A533b',
#             'https://mangalib.me/after-the-curtain-call?section=chapters']:
#     x = threading.Thread(target=tread_f, args=[[url]])
#     x.start()
#     time.sleep(2)
#     threats.append(x)
# for i in threats:
#     i.join()
# print('end')

_url = 'url'
_name = 'name'
_fic = 'fic'
_source = 'source'
_chapter = 'chapter'
_chapters = 'chapters'
_num = 'num'
_time = 'time'
_date = 'date'
_user = 'user'
_user_name = 'user_name'
_user_id = 'user_id'
_resource = 'resource'
_resources = 'resources'
_last_count = 'last_count'
_ficbook = 'ficbook'
_mintmanga = 'mintmanga'
_mangalib = 'mangalib'
_readmanga = 'readmanga'

url_data_fic = 'https://res.cloudinary.com/dnmx4vd6f/raw/upload/ficbook.txt'
url_users = 'https://res.cloudinary.com/dnmx4vd6f/raw/upload/fic_users.txt'

cloudinary.config(
    cloud_name=bot_token.cloud_name,
    api_key=bot_token.api_key,
    api_secret=bot_token.api_secret
)
file_users = 'users_data.txt'
file_fanfictions = 'fanfiction_data.txt'

parts = (' частей', ' части', ' часть')
admin = bot_token.admin
name_fic = 'moye'

new_fanfiction_data = {}
main_fic = tag(_url)
users = {}
main_user = tag(_user_id)


#
# FICBOOK
#

# вынуть данные из списка частей фанфика
def get_ff_chapters(name, url, text, resource):
    fic = {}
    rows = str(text).split('\n')
    fic[detag(tag(_name))] = name
    fic[_url] = url
    fic[detag(tag(_source))] = resource
    fic[detag(tag(_chapters))] = []
    for i in range(len(rows) - 1):
        if i % 2 == 0:
            num = rows[i]
            date = rows[i + 1]
            # date = datetime.strptime(rep_month(date), '%d %b %Y, %H:%M')
            fic[detag(tag(_chapters))].append(
                {detag(tag(_chapter)): {detag(tag(_date)): date, detag(tag(_num)): num}})
    return fic


# распарсить сайт из фикбука
def get_site_ficbook_data(url):
    driver = get_driver()
    try:
        print("Обновляю", url)
        driver.get(url)
        time.sleep(wait_to_load)
        try:
            driver.find_element_by_id("adultCoverWarningHide").click()  # пропустить 18+
        except:
            pass
        name_fic = driver.find_element_by_tag_name('h1').text
        try:
            text = ''
            element = driver.find_element_by_xpath(
                "//ul[@class='list-unstyled list-of-fanfic-parts clearfix']")  # найти список глав
            names = element.find_elements_by_tag_name('h3')
            times = element.find_elements_by_tag_name('span')
            for n, t in zip(names, times):
                text += n.text + '\n' + t.get_attribute('title') + '\n'
            fic = get_ff_chapters(name_fic, url, text, _ficbook)
        except:
            h2 = driver.find_element_by_tag_name('h2').text  # найти название одной главы
            elem = driver.find_element_by_xpath("//div[@class='part-date']")
            time_ = elem.find_element_by_tag_name('span').get_attribute('title')
            fic = get_ff_chapters(name_fic, url, 'Глава 1 ' + h2 + '\n' + time_, _ficbook)
        driver.quit()  # выйти
        return fic
    except Exception as e:
        print(e)
        driver.quit()
        return False


# распарсить сайт минт манги
def get_site_mintmanga_data(url):
    driver = get_driver()
    try:
        print("Обновляю", url)
        driver.get(url)
        time.sleep(wait_to_load)
        try:
            driver.find_element_by_xpath("//span[@class='js-link']").click()  # развернуть
        except Exception as e:
            pass
        name_fic = driver.find_element_by_tag_name('h1').text.split(' | ')[0]
        text = ''
        element = driver.find_element_by_xpath("//table[@class='table table-hover']")  # найти список глав
        names = element.find_elements_by_tag_name('a').__reversed__()
        times = element.find_elements_by_tag_name('tr').__reversed__()
        for n, t in zip(names, times):
            name = n.text + '\n'
            time_f = t.find_elements_by_tag_name('td')[1].get_attribute('data-date-raw') + '\n'
            text += name + time_f
        fic = get_ff_chapters(name_fic, url, text, _mintmanga)
        driver.quit()
        return fic
    except Exception as e:
        print(e)
        driver.quit()
        return False


# распарсить сайт фанфика
def get_site_readmanga_data(url):
    driver = get_driver()
    try:
        print("Обновляю", url)
        driver.get(url)
        time.sleep(wait_to_load)
        try:
            driver.find_element_by_xpath("//span[@class='js-link']").click()  # развернуть
        except Exception as e:
            pass
        name_fic = driver.find_element_by_tag_name('h1').text.split(' | ')[0]
        text = ''
        element = driver.find_element_by_xpath("//table[@class='table table-hover']")  # найти список глав
        names = element.find_elements_by_tag_name('a').__reversed__()
        times = element.find_elements_by_tag_name('tr').__reversed__()
        for n, t in zip(names, times):
            name = n.text + '\n'
            time_f = t.find_elements_by_tag_name('td')[1].get_attribute('data-date-raw') + '\n'
            text += name + time_f
        fic = get_ff_chapters(name_fic, url, text, _mintmanga)
        driver.quit()
        return fic
    except Exception as e:
        print(e)
        driver.quit()
        return False


# распарсить сайт мангалиб !!! не работает !!!
def get_site_mangalib_data(url):
    driver = get_driver()
    try:
        print("Обновляю", url)
        driver.get(url)
        time.sleep(wait_to_load)
        print(driver.page_source)
        try:
            name_fic = driver.find_element_by_xpath("//div[@class='media-name__main']").text.split(' | ')[0]
            elem = driver.find_elements_by_class_name('team-list')[1]
            transleters = elem.find_elements_by_class_name('team-list-item')
            driver.find_element_by_xpath(
                "//div[@class='button button_sm button_light media-chapters-sort']").click()
            lengthes = []
            for i in range(0, len(transleters)):
                driver.execute_script("window.scrollTo(0, 0);")
                transleters[i].click()

                size = int(driver.find_elements_by_class_name('media-info-list__item')[-2].text.split('\n')[-1])
                names, times = [], []
                try:
                    for i in range(0, size * 40, 40):
                        if (i / 40) % 5 == 0:
                            driver.execute_script("window.scrollTo(0, " + str(i) + ");")
                        element = driver.find_element_by_xpath(
                            "//div[@style='transform: translateY(" + str(i) + "px);']")
                        names.append(element.find_element_by_class_name('media-chapter__name').text)
                        times.append(element.find_element_by_class_name('media-chapter__date').text)
                    lengthes.append(len(names))
                except:
                    lengthes.append(len(names))
            max = 0
            iterabl = 0
            for i in range(0, len(lengthes)):
                if lengthes[i] > max:
                    max = lengthes[i]
                    iterabl = i
            driver.execute_script("window.scrollTo(0, 0);")
            transleters[iterabl].click()
            size = int(driver.find_elements_by_class_name('media-info-list__item')[-2].text.split('\n')[-1])
            names, times = [], []
            text = ''
            try:
                for i in range(0, size * 40, 40):
                    if (i / 40) % 5 == 0:
                        driver.execute_script("window.scrollTo(0, " + str(i) + ");")
                    element = driver.find_element_by_xpath(
                        "//div[@style='transform: translateY(" + str(i) + "px);']")
                    names.append(element.find_element_by_class_name('media-chapter__name').text)
                    times.append(element.find_element_by_class_name('media-chapter__date').text)
                    text += names[-1] + '\n' + times[-1] + '\n'
            except:
                for i in range(max, size, 1):
                    text += 'Новая часть' + '\n' + 'None' + '\n'
                lengthes.append(len(names))
            finally:
                fic = get_ff_chapters(name_fic, url, text, _mangalib)
                driver.quit()
                return fic
        except Exception as e:
            try:
                name_fic = driver.find_element_by_xpath("//div[@class='media-name__main']").text
                size = int(driver.find_elements_by_class_name('media-info-list__item')[-2].text.split('\n')[-1])
                driver.find_element_by_xpath(
                    "//div[@class='button button_sm button_light media-chapters-sort']").click()
                names, times = [], []
                for i in range(0, size * 40, 40):
                    if (i / 40) % 5 == 0:
                        driver.execute_script("window.scrollTo(0, " + str(i) + ");")
                    element = driver.find_element_by_xpath("//div[@style='transform: translateY(" + str(i) + "px);']")
                    names.append(element.find_element_by_class_name('media-chapter__name').text)
                    times.append(element.find_element_by_class_name('media-chapter__date').text)
                text = ''
                for n, t in zip(names, times):
                    text += n + '\n' + t + '\n'
                fic = get_ff_chapters(name_fic, url, text, _mangalib)
                driver.quit()
                return fic
            except Exception as e:
                print(e)
                driver.quit()
                return False
    except Exception as e:
        print(e)
        driver.quit()
        return False


# обновить фанфик внутри программы (не файла)
def apd_fanfiction(url, new_fic):
    for atr in new_fanfiction_data[url]:
        new_fanfiction_data[url][atr] = new_fic[atr]


# получить данные фанфика из инета и добавить его в массив данных фф
def get_new_ff_data(url, update, resource):
    if resource == _ficbook:
        fic = get_site_ficbook_data(url)
    elif resource == _mintmanga:
        fic = get_site_mintmanga_data(url)
    elif resource == _readmanga:
        fic = get_site_readmanga_data(url)
    elif resource == _mangalib:
        return False
    else:
        return False
    if fic:
        new_fanfiction_data[url] = fic
        return True
    else:
        return False


# вызвать нужный метод для выбранного ресурса
def get_new_chapter_data(url, source, update=False):
    if source == 'ficbook':
        return check_fanfiction(url, update)


# обновить в облаке данные фф
def upload_fanfiction_data():
    cloudinary.uploader.upload("ficbook.txt", public_id="ficbook", resource_type="raw", invalidate=True)


# получить данные фф из облака
def download_fanfiction_data():
    html = requests.get(url_data_fic)
    soup = BeautifulSoup(html.content.decode('cp1251', 'ignore'), features="lxml")
    text = unxml(str(soup), '<body>')
    file = open(file_fanfictions, 'w', encoding='cp1251')
    file.write(text.replace('\r', ''))
    file.close()
    read_fanfictions()


# проверить есть ли фф в базе
def check_fanfiction(url, update, resource):
    if not url in new_fanfiction_data or update:
        return get_new_ff_data(url, update, resource)
    return True


# функция-поток для получения отдельного фф из сайта
def thread_function_update_user_chapters(args):
    check_fanfiction(args[0], args[1], args[2])


def get_time(time, resource):
    if resource == _ficbook:
        return datetime.strptime(help.rep_month(time), '%d %b %Y, %H:%M')
    if resource == _mintmanga:
        return datetime.strptime(help.rep_month(time).split('.')[0], '%Y-%m-%d %H:%M:%S')
    if resource == _readmanga:
        return datetime.strptime(help.rep_month(time).split('.')[0], '%Y-%m-%d %H:%M:%S')


# запускает потоки под каждый фф из данных юзера что бы получить обнову из сайтов
def update_user_chapters(user_id, update, user_upd=None):
    if str(user_id) in users:
        user = users[str(user_id)]
        if user_upd is not None and len(user[_resources]) > 0:
            send_sms_to_user(user_id, 'Запускаю поиск обновлений, это займет некоторое время...')
        if len(user[_resources]) > 0:
            news = False
            for resource in user[_resources]:
                url = resource[_resource][_url]
                if url in new_fanfiction_data:
                    check_fanfiction(url, update, new_fanfiction_data[url][_source])
                else:
                    check_fanfiction(url, True, get_resourse(url)[0])
            for resource in user[_resources]:
                url = resource[_resource][_url]
                if url in new_fanfiction_data:
                    count = len(new_fanfiction_data[url][_chapters])
                    last_count = int(resource[_resource][_last_count])
                    if count > last_count:
                        text = url + '\nНазвание: ' + new_fanfiction_data[url][_name]
                        diff = count - last_count
                        if last_count == 0:
                            text += '\n' + 'Количество глав: ' + str(count)
                            text += '\n' + 'Дата выхода последней главы: ' \
                                    + new_fanfiction_data[url][_chapters][-1][_chapter][_date]
                            send_sms_to_user(user_id, text)
                        else:
                            text += '\n' + 'Новые главы:\n'
                            for c in new_fanfiction_data[url][_chapters][-diff:]:
                                date = get_time(c[_chapter][_date], new_fanfiction_data[url][_source])
                                text += c[_chapter][_num] + ' ('
                                text += str(date.strftime("%d.%m.%Y")) + ')\n' if date != None else 'недавно' + ')\n'
                            send_sms_to_user(user_id, text)
                        resource[_resource][_last_count] = count
                        news = True
            return news
    return None


# фунция-возврата для повторения функции обновления юзера спустя н-минут
def alarm(context: CallbackContext) -> None:
    args = str(context.job.name).split('|')
    user_id, interval = args[0], args[1]
    if user_id in users:
        if len(users[user_id][_resources]) > 0:
            update_user_chapters(user_id, True)
            repeate_upd(user_id, interval)


# функция для задания напоминания обновления через н-минут
def repeate_upd(user_id, interval):
    updater.job_queue.run_once(alarm, timedelta(minutes=int(interval)), name=user_id + '|' + interval,
                               context=int(user_id))


# для всех юзеров - получитьт новости и задать повтор напоминания
def update_all_user_chapters(update):
    for user_id in users:
        update_user_chapters(user_id, update)
        repeate_upd(user_id, users[user_id][_time])
    write_users()
    write_fanfictions()


# функция-поток для получения одного фф из сайта
def thread_function_get_all_ficbook_data(args):
    check_fanfiction(args[0], args[1], args[2])


def delete_abandoned_fics():
    read_users()
    read_fanfictions()
    avalable = {}
    for url in new_fanfiction_data:
        avalable[url] = 0
    for id in users:
        for res in users[id][_resources]:
            avalable[res[_resource][_url]] += 1
    for i in avalable:
        if avalable[i] == 0:
            new_fanfiction_data.pop(i)
    write_fanfictions()


# запускает потоки для получения обнов всех фф из базы
def get_all_ficbook_data():
    delete_abandoned_fics()
    for url in new_fanfiction_data:
        check_fanfiction(url, True, new_fanfiction_data[url][_source])
    write_fanfictions()


#
# USER
#

# записать данные юзеров
def write_users():
    help.write_file_key(file_users, users, detag(tag(_user)), main_user)
    unload_users_data()


# прочитать данные юзеров
def read_users():
    global users
    user_pattern = [
        [main_user, 1, None],
        [tag(_user_name), 1, None],
        [tag(_time), 1, None],
        [tag(_resources), 1, [
            tag(_resource), 2, [
                [tag(_url), 1, None], [tag(_last_count), 1, None], [tag(_name), 1, None]]]]
    ]
    users = help.read_file_key(file_users, user_pattern, tag(_user), main_user)


def add_user_resourse(user_id, url):
    if user_id in users:
        name = new_fanfiction_data[url][_name]
        resource = {_resource: {_url: url, _last_count: 0, _name: name}}
        users[user_id][_resources].append(resource)
        write_users()


def add_user_in_data(update):
    user_id = str(update.message.chat_id)
    user_name = str(update.message.from_user.name)
    user = {_user_id: user_id, _user_name: user_name, _time: 30, _resources: []}  # add new user
    users[user_id] = user
    write_users()


def check_user_ff(update, resource):
    user_id = str(update.message.chat_id)
    read_users()
    is_fanfic = False
    is_user = user_id in users
    if not is_user:
        add_user_in_data(update)
    user = users[user_id]
    for res in user[_resources]:  # в его ресурсах
        if res[_resource][_url] == resource:  # этот ресурс
            is_fanfic = True  # он уже есть тут
            break
    return is_fanfic


# выгрузить в облако данные юзеров
def unload_users_data():
    cloudinary.uploader.upload(file_users, public_id="fic_users", resource_type="raw", invalidate=True)


# скачать данные юзеров из облака
def download_users_data():
    html = requests.get(url_users)
    soup = BeautifulSoup(html.content.decode('cp1251', 'ignore'), features="lxml")
    text = unxml(str(soup), '<body>')
    file = open(file_users, 'w', encoding='cp1251')
    file.write(text.replace('\r', ''))
    file.close()
    read_users()
    write_users()


#  записать данные фанфиков в файл
def write_fanfictions():
    help.write_file_key(file_fanfictions, new_fanfiction_data, 'fic', main_fic)
    unload_fics_data()


# прочитать данные фанфиков из файла
def read_fanfictions():
    global new_fanfiction_data
    fanfiction_pattern = [
        [main_fic, 1, None],
        [tag(_name), 1, None],
        [tag(_source), 1, None],
        [tag(_chapters), 1, [tag(_chapter), 2, [[tag(_date), 1, None], [tag(_num), 1, None]]]]
    ]
    new_fanfiction_data = help.read_file_key(file_fanfictions, fanfiction_pattern, tag(_fic), main_fic)


# выгрузить в облако данные фанфиков
def unload_fics_data():
    cloudinary.uploader.upload(file_fanfictions, public_id="ficbook", resource_type="raw", invalidate=True)


# скачать данные фанфиков из облака
def download_fics_data():
    html = requests.get(url_data_fic)
    soup = BeautifulSoup(html.content.decode('cp1251', 'ignore'), features="lxml")
    text = unxml(str(soup), '<body>')
    file = open(file_fanfictions, 'w', encoding='cp1251')
    file.write(text)
    file.close()


# удалить юзера????
def del_user(id):
    # Командой /set юзер задал свои предметы и ф-я записала его в файлик
    f = open(file_users, 'r', encoding='cp1251')
    file = f.read()
    users = unxml_list(file, tag(_user))
    for user in users:
        if user == str(id):
            users.remove(user)
            f.close()
            f = open(file_users, 'w', encoding='cp1251')
            text = '0'
            for len in users:
                text += toxml(len, tag(_user)) + '\n\n'
            f.write(text)
            break
    f.close()
    unload_users_data()


# отправить смс какому то пользователю по айди
def send_sms_to_user(id, text):
    if len(text) > 4096:
        for x in range(0, len(text), 4096):
            updater.bot.sendMessage(chat_id=int(id), text=text[x:x + 4096])
    else:
        updater.bot.sendMessage(chat_id=int(id), text=text)
    file = open('questions.txt', 'a+', encoding='cp1251')
    answer = help.filter_text(text)
    file.write('[' + str(datetime.now().strftime("%d.%m.%Y %H:%M")) + ']' +
               str(id) + ':' + 'sms to user' +
               '\n - ' + answer.replace('\n', '\\n') + '\n\n')
    file.close()
    print(id, 'None')
    print('-', answer, '\n')


# логирует данные от юзера(ник, веремя, текст)
def loging(update, answer, reply_markup=None):
    # выводит переписку в консоль + отправляет смс юзеру
    file = open('questions.txt', 'a+', encoding='cp1251')
    answer = help.filter_text(answer)
    file.write('[' + str(datetime.now().strftime("%d.%m.%Y %H:%M")) + ']' +
               str(update.message.chat_id) + ':' + update.message.from_user.name +
               '\n - ' + update.message.text.replace('\n', '\\n') +
               '\n - ' + answer.replace('\n', '\\n') + '\n\n')
    file.close()

    update.message.reply_text(answer, reply_markup=reply_markup, parse_mode='markdown')
    print(update.effective_user.mention_markdown_v2(), update.message.from_user.name)
    print('-', update.message.text)
    print('-', answer, '\n')


def start(update: Update, _: CallbackContext) -> None:
    # стартовая команда для юрера
    answer = 'Привет, я - бот'
    loging(update, answer, markup)


def get_resourse(url):
    source = False
    resource = False
    if url.startswith('https://ficbook.net/readfic/'):
        resource = 'https://ficbook.net/readfic/' + url.split('/')[4] if url.split('/')[4] else False
        source = _ficbook
    elif url.startswith('https://mintmanga.live/'):
        resource = 'https://mintmanga.live/' + url.split('/')[3] if url.split('/')[3] else False
        source = _mintmanga
    elif url.startswith('https://readmanga.io/'):
        resource = 'https://readmanga.io/' + url.split('/')[3] if url.split('/')[3] else False
        source = _readmanga
    # elif url.startswith('https://mangalib.me/'):
    #     resource = url.split('?')[0] + '?section=chapters' if url.split('/')[3] else False
    #     source = _mangalib
    return source, resource


# понять что єто фикбук - добавить пользователя и ресурс его отслеживания - добавить в дату данные ресурса
def get_link_from_user(update):
    text = update.message.text
    text_success = 'Вы подписались на этот ресурс'
    text_not_suc = 'Вы уже подписаны на этот ресурс'
    user_id = str(update.message.chat_id)
    source, resource = get_resourse(text)
    if source and resource:
        in_user_res = check_user_ff(update, resource)
        if not in_user_res:
            is_real_fanfic = check_fanfiction(resource, True, source)
            if is_real_fanfic:
                add_user_resourse(user_id, resource)
                update_user_chapters(user_id, False, None)
                write_users()
                write_fanfictions()
                return text_success + ':\n' + str(new_fanfiction_data[resource][_name])
        elif in_user_res:
            return text_not_suc
        else:
            return False


def echo(update: Update, _: CallbackContext) -> None:
    # Основной читалель смс от юзера
    loging(update, 'Обрабатываю ваше сообщение, это может занять от 10 секунд до 10 минут, подождите пожалуйста',
           markup)
    answer = get_link_from_user(update)
    if not answer:
        answer = 'Это не ссылка на ресурс'
    loging(update, answer, markup)


def check(update: Update, _: CallbackContext) -> None:
    user_id = update.message.chat_id
    news = update_user_chapters(user_id, update=True, user_upd=True)
    if news is True:
        pass
    elif news is False:
        loging(update, 'Нет новых глав', markup)
    else:
        loging(update, 'Вы еще ничего не отслеживаете', markup)


def delete_user_resource(update: Update, context: CallbackContext):
    if not context.args:
        loging(update, 'Вы не выбрали что удалить')
    else:
        num = context.args[0]
        if not num.isnumeric():
            loging(update, 'Вы отправили не целое число')
        else:
            n = int(num) - 1
            user = users[str(update.message.chat_id)]
            resources = user[_resources]
            if not (n >= 0 and n < len(resources)):
                loging(update, 'У вас нет такого ресурса')
            else:
                answer = 'Вы отписались от: ' + resources[n][_resource][_name]
                resources.pop(n)
                write_users()
                loging(update, answer, markup)


def select_to_delete_user_resorce(update: Update, _: CallbackContext) -> None:
    user_id = str(update.message.chat_id)
    if not (user_id in users):
        loging(update, 'Вам не от чего отписываться', markup)
    else:
        answer = 'Выберете "/del №" того, что не хотите больше отслеживать'
        reply_keyboard = [[]]
        a = 1
        user = users[user_id]
        sq = int(len(user[_resources])) ** 0.5
        for resource in user[_resources]:
            if a % (1 + sq) == 0:
                reply_keyboard.append([])
            answer += '\n' + str(a) + ' - ' + resource[_resource][_name]
            reply_keyboard[-1].append('/del ' + str(a))
            a += 1
        reply_keyboard.append(['/cancel'])
        if a == 1:
            answer = 'У вас еще нет подписок'
            loging(update, answer, markup)
        else:
            answer += '\n/cancel - что бы ни от чего не отписываться'
            temp_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
            loging(update, answer, temp_markup)


# задать новый фф для слежки
def new_fic(update: Update, _: CallbackContext) -> None:
    answer = 'Сейчас я умею следить за такими источниками:' \
             '\nhttps://ficbook.net/' \
             '\nhttps://mintmanga.live/' \
             '\nhttps://readmanga.live/' \
             '\nКсожалению, https://mangalib.me/ невозможно отслеживать' \
             '\n\nВсе ваши подписки я буду проверять раз в 30 минут' \
             '\nЧто бы начать следить за обновлениями, отправте мне ссылку на ваш ресурс'
    loging(update, answer, markup)


def set_time(update: Update, _: CallbackContext) -> None:
    answer = 'Вы отписались от проверки обновлений'
    loging(update, answer, markup)


def get_user_resources(update: Update, _: CallbackContext) -> None:
    user_id = str(update.message.chat_id)
    answer = 'Вы еще не подписались ни на что'
    if not user_id in users:
        loging(update, answer, markup)
    else:
        if not len(users[user_id][_resources]) > 0:
            loging(update, answer, markup)
        else:
            resources = users[user_id][_resources]
            answer = 'Вы подписаны на следующие обновления:'
            for i in range(0, len(resources)):
                res = resources[i][_resource]
                answer += '\n' + str(i + 1) + ') [' + res[_name] + '](' + res[_url] + ')'
            loging(update, answer, markup)


def get_last_parts(update: Update, _: CallbackContext) -> None:
    user_id = str(update.message.chat_id)
    answer = 'Вы еще не подписались ни на что'
    if not user_id in users:
        loging(update, answer, markup)
    else:
        if not len(users[user_id][_resources]) > 0:
            loging(update, answer, markup)
        else:
            resources = users[user_id][_resources]
            answer = 'Последние вышедшие части ваших ресурсов:'
            for i in range(0, len(resources)):
                res = resources[i][_resource]
                last_chapter = new_fanfiction_data[res[_url]][_chapters][-1][_chapter]
                resource = new_fanfiction_data[res[_url]][_source]
                answer += '\n' + str(i + 1) + ') [' + res[_name] + '](' + res[_url] + ')\n' + \
                          str(get_time(last_chapter[_date], resource)) + ' - "' + last_chapter[_num] + '"' + '\n'
            loging(update, answer, markup)


def cancel(update: Update, _: CallbackContext) -> None:
    answer = 'Отмена действий'
    loging(update, answer, markup)


# старт приложения, скачать юзеров, скачать фф, задать повторы
def start_work():
    download_users_data()  # скачать последие данные юзеров
    download_fanfiction_data()  # скачать последие данные фанфиков
    get_all_ficbook_data()  # скачать все данные фанфиков
    update_all_user_chapters(update=False)  # пройтись по юзерам, отправить обнову, скачать фанфик если надо
    print('update')


print(datetime.now())
# updater = Updater("1990967552:AAFJ4bYjpdJk21m7bgZlcj6-ztnPD_DmGfw")
updater = Updater(bot_token.token)
dispatcher = updater.dispatcher
reply_keyboard = [['/new_fic', '/check_new'], ['/my_list', '/last_parts'], ['/un_subscribe']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

start_work()

dispatcher.add_handler(CommandHandler("start", new_fic))
dispatcher.add_handler(CommandHandler("help", new_fic))
dispatcher.add_handler(CommandHandler("new_fic", new_fic))
dispatcher.add_handler(CommandHandler("my_list", get_user_resources))
dispatcher.add_handler(CommandHandler("last_parts", get_last_parts))
dispatcher.add_handler(CommandHandler("check_new", check))
dispatcher.add_handler(CommandHandler("un_subscribe", select_to_delete_user_resorce))
dispatcher.add_handler(CommandHandler("del", delete_user_resource))
dispatcher.add_handler(CommandHandler("cancel", cancel))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
updater.start_polling()
updater.idle()

'''
git add .
git commit -am "make it better"
git push heroku master
heroku ps:scale worker=1

heroku logs -n 1500
'''
