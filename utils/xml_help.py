def unxml_list(text, tag):
    # развертывает множество фраз одного тега в список
    detag = tag[0] + '/' + tag[1:]
    tag_list = []
    while text.find(tag) != -1 and text.find(detag) != -1:
        tag_list.append(text[text.find(tag) + len(tag):text.find(detag)])
        text = text[text.find(detag) + len(detag):]
    return tag_list


def unxml(text, tag):
    # Развертывает фразу из тега
    detag = tag[0] + '/' + tag[1:]
    if text.find(tag) != -1 and text.find(detag) != -1:
        return text[text.find(tag) + len(tag):text.find(detag)]


def toxml(text, tag):
    # Оборачивает фразу в тег
    return str(tag) + str(text) + str(tag)[0] + '/' + str(tag)[1:]


def replacexml(text, replacement, tag):
    # хмл - меняет содержимое в text на replacement в теге tag
    detag = tag[0] + '/' + tag[1:]
    data = text[text.find(tag):text.find(detag) + len(detag)]
    return text.replace(data, toxml(replacement, tag))


def tag(text):
    # оборачивает слово в скобочки
    return '<' + text + '>'


def detag(text):
    # разварачивает слово из скобочик
    return text[1:-1]
