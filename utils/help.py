import re
from utils import xml_help as xml


def filter_text(text):
    letters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' \
              'абвгдеёжзийклмнопрстуфхцчшщьъыэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЪЫЭЮЯ' \
              ' !"#$%№&\'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r'
    text = [c for c in text if c in letters]
    return ''.join(text)


def rep_month(text):
    rep = {"января": "Jan", "февраля": "Feb", "марта": "Mar", "апреля": "Apr", "мая": "May", "июня": "Jun",
           "июля": "Jul", "августа": "Aug", "сентября": "Sep", "октября": "Oct", "ноября": "Nov", "декабря": "Dec"}
    rep = dict((re.escape(k), v) for k, v in rep.items())
    pattern = re.compile("|".join(rep.keys()))
    return pattern.sub(lambda m: rep[re.escape(m.group(0))], text)


users = [
    {'id': '1111', 'name': 'kate', 'reses': [{'res': '1'}, {'res': '2'}]},
    {'id': '2222', 'name': 'olia', 'reses': [{'res': '3'}, {'res': '4'}]},
]


def write_file(file_name, mass, items):
    file = open(file_name, 'w', encoding='cp1251')  # encoding='cp1251'

    def get_el(dict, str, n):
        for el in dict:
            if isinstance(dict[el], type({})):
                str += xml.toxml(get_el(dict[el], '', n + 1), xml.tag(el))
                str += '\n' if n == 0 else ''
            elif isinstance(dict[el], list):
                mss = '\n'
                for l in dict[el]:
                    mss += get_el(l, '', n + 1) + '\n'
                str += xml.toxml(mss, xml.tag(el))
            else:
                str += xml.toxml(dict[el], xml.tag(el))
        return str

    text = 'Файл для хранения: ' + items + '\n'
    for el in mass:
        text += xml.toxml(get_el(el, '', 0), xml.tag(items)) + '\n\n'
    filter_text(text)
    file.write(text)
    file.close()


pattern1 = [['<id>', 1, None], ['<name>', 1, None], ['<reses>', 1, ['<res>', 2, None]]]


def read_file(file_name, pattern, item_name):
    file = open(file_name, 'r', encoding='cp1251')
    data = file.read()
    file.close()

    items = []
    texts = xml.unxml_list(data, item_name)
    for _ in texts:
        items.append({})

    def get_atr(patt, item, text):
        for trpl in patt:
            if not isinstance(trpl[0], list) and trpl[1] == 1 and trpl[2] == None:
                item[xml.detag(trpl[0])] = xml.unxml(text, trpl[0])
            if not isinstance(trpl[0], list) and trpl[1] == 1 and isinstance(trpl[2], list):
                item[xml.detag(trpl[0])] = []
                get_atr([trpl[2]], item[xml.detag(trpl[0])], xml.unxml(text, trpl[0]))
            if not isinstance(trpl[0], list) and trpl[1] >= 2 and isinstance(trpl[2], list):
                mass = xml.unxml_list(text, trpl[0])
                for m in mass:
                    item.append({xml.detag(trpl[0]): {}})
                    get_atr(trpl[2], item[-1][xml.detag(trpl[0])], m)

    for i, t in zip(items, texts):
        get_atr(pattern, i, t)
    return items


# write_file('test_arr.txt', users, 'user')
# items = read_file('test_arr.txt', pattern1, 'user')
# print(items)


def write_file_key(file_name, mass, items, key):
    file = open(file_name, 'w', encoding='cp1251')  # encoding='cp1251'

    def get_el(dict, str, n):
        for el in dict:
            if isinstance(dict[el], type({})):
                str += xml.toxml(get_el(dict[el], '', n + 1), xml.tag(el))
                str += '\n' if n == 0 else ''
            elif isinstance(dict[el], list):
                mss = '\n'
                for l in dict[el]:
                    mss += get_el(l, '', n + 1) + '\n'
                str += xml.toxml(mss, xml.tag(el))
            else:
                str += xml.toxml(dict[el], xml.tag(el))
        return str

    text = 'Файл для хранения: ' + items + '\n'
    for item in mass:
        text += xml.toxml(get_el(mass[item], xml.toxml(item, key), 0), xml.tag(items)) + '\n\n'
    letters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' \
              'абвгдеёжзийклмнопрстуфхцчшщьъыэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЪЫЭЮЯ' \
              ' !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r'
    text = [c for c in text if c in letters]
    text = ''.join(text)
    file.write(text)
    file.close()


def read_file_key(file_name, pattern, item_name, key):
    file = open(file_name, 'r', encoding='cp1251')
    data = file.read()
    file.close()

    items = []
    return_items = {}
    texts = xml.unxml_list(data, item_name)
    for _ in texts:
        items.append({})

    def get_atr(patt, item, text):
        for trpl in patt:
            if not isinstance(trpl[0], list) and trpl[1] == 1 and trpl[2] == None:
                item[xml.detag(trpl[0])] = xml.unxml(text, trpl[0])
            if not isinstance(trpl[0], list) and trpl[1] == 1 and isinstance(trpl[2], list):
                item[xml.detag(trpl[0])] = []
                get_atr([trpl[2]], item[xml.detag(trpl[0])], xml.unxml(text, trpl[0]))
            if not isinstance(trpl[0], list) and trpl[1] >= 2:
                mass = xml.unxml_list(text, trpl[0])
                for m in mass:
                    if trpl[2] == None:
                        ntrpl = [[trpl[0], 1, trpl[2]]]
                        item.append({})
                        get_atr(ntrpl, item[-1], xml.toxml(m, trpl[0]))
                    else:
                        item.append({xml.detag(trpl[0]): {}})
                        get_atr(trpl[2], item[-1][xml.detag(trpl[0])], m)

    for i, t in zip(items, texts):
        get_atr(pattern, i, t)
    for it in items:
        return_items[it[xml.detag(key)]] = it
        return_items[it[xml.detag(key)]].pop(xml.detag(key))
    return return_items


# write_file('test_arr.txt', users, 'user')
# items = read_file_key('test_arr.txt', pattern1, '<user>', '<id>')
# print(items)
# write_file_key('test_arr.txt', items, 'user', '<id>')
