from pathlib import Path

import requests


async def load_attachments(bot, attachments, from_id) -> str:
    """
    Загружает вложения на сервера ВК
    Args:
        bot: Объект бота
        attachments: Вложения
        from_id: Отправитель сообщения с вложениями

    Returns:
        str: Список идентификаторов вложений, готовых к отправке
    """
    atch = []
    for attach in attachments:
        if attach.photo:
            max_size = 0
            max_url = ""
            for size in attach.photo.sizes:
                if size.height > max_size:
                    max_size = size.height
                    max_url = size.url
            response = requests.get(max_url)
            Path(f"{attach.photo.access_key}.jpg").write_bytes(response.content)
            file = open(Path(f"{attach.photo.access_key}.jpg"), "rb")
            server = await bot.api.photos.get_messages_upload_server(peer_id=from_id)
            upload = requests.post(server.upload_url, files={"photo": file},).json()
            save = await bot.api.photos.save_messages_photo(**upload)
            photo = f"photo{save[0].owner_id}_{save[0].id}"
            atch.append(photo)
        if attach.doc:
            server = await bot.api.docs.get_messages_upload_server(peer_id=from_id)
            response = requests.get(attach.doc.url)
            Path(f"{attach.doc.title}").write_bytes(response.content)
            file = open(Path(f"{attach.doc.title}"), "rb")
            upload = requests.post(server.upload_url, files={"file": file},).json()
            save = await bot.api.docs.save(file=upload["file"])
            doc = f"doc{save.doc.owner_id}_{save.doc.id}"
            atch.append(doc)
    return ",".join(atch)


def translate_string(s: str):
    """Переводит строку с английской раскладки на русскую и обратно"""
    en = [
        "q",
        "w",
        "e",
        "r",
        "t",
        "y",
        "u",
        "i",
        "o",
        "p",
        "[",
        "]",
        "a",
        "s",
        "d",
        "f",
        "g",
        "h",
        "j",
        "k",
        "l",
        ";",
        "'",
        "\\",
        "z",
        "x",
        "c",
        "v",
        "b",
        "n",
        "m",
        ",",
        ".",
        "/",
        "Q",
        "W",
        "E",
        "R",
        "T",
        "Y",
        "U",
        "I",
        "O",
        "P",
        "{",
        "}",
        "A",
        "S",
        "D",
        "F",
        "G",
        "H",
        "J",
        "K",
        "L",
        ":",
        '"',
        "|",
        "Z",
        "X",
        "C",
        "V",
        "B",
        "N",
        "M",
        "<",
        ">",
        "?",
    ]
    ru = [
        "й",
        "ц",
        "у",
        "к",
        "е",
        "н",
        "г",
        "ш",
        "щ",
        "з",
        "х",
        "ъ",
        "ф",
        "ы",
        "в",
        "а",
        "п",
        "р",
        "о",
        "л",
        "д",
        "ж",
        "э",
        "\\",
        "я",
        "ч",
        "с",
        "м",
        "и",
        "т",
        "ь",
        "б",
        "ю",
        ".",
        "Й",
        "Ц",
        "У",
        "К",
        "Е",
        "Н",
        "Г",
        "Ш",
        "Щ",
        "З",
        "Х",
        "Ъ",
        "Ф",
        "Ы",
        "В",
        "А",
        "П",
        "Р",
        "О",
        "Л",
        "Д",
        "Ж",
        "Э",
        "/",
        "Я",
        "Ч",
        "С",
        "М",
        "И",
        "Т",
        "Ь",
        "Б",
        "Ю",
        ",",
    ]

    result = ""

    for i in range(len(s)):
        try:
            ind = en.index(s[i])
        except ValueError:
            pass
        else:
            result += ru[ind]
            continue

        try:
            ind = ru.index(s[i])
        except ValueError:
            result += s[i]
        else:
            result += en[ind]

    return result
