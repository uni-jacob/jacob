from vkwave.bots import DocUploader
from vkwave.bots import PhotoUploader
from vkwave.bots import VoiceUploader

from services.exceptions import AttachmentLimitExceeded


async def load_attachments(api, attachments, from_id) -> str:
    """
    Загружает вложения на сервера ВК
    Args:
        api: Объект API ВКонтакте
        attachments: Вложения
        from_id: Отправитель сообщения с вложениями

    Returns:
        str: Список идентификаторов вложений, готовых к отправке
    """
    atchs = []
    photo_uploader = PhotoUploader(api)
    doc_uploader = DocUploader(api)
    am_uploader = VoiceUploader(api)
    if len(attachments) > 10:
        raise AttachmentLimitExceeded("Количество вложений не может быть больше 10")
    for attach in attachments:
        if attach.photo:
            max_url = ""
            max_size = 0
            for size in attach.photo.sizes:
                if size.height > max_size:
                    max_size = size.height
                    max_url = size.url
            atch = await photo_uploader.get_attachment_from_link(from_id, max_url)
            atchs += atch.split(",")
        if attach.doc:
            atch = await doc_uploader.get_attachment_from_link(from_id, attach.doc.url)
            atchs += atch.split(",")
        if attach.audio_message:
            # TODO: не работает!
            atch = await am_uploader.get_attachment_from_link(
                from_id, attach.audio_message.link_mp3
            )
            atchs += atch.split(",")

    return ",".join(atchs)


def translate_string(s: str):
    """Переводит строку с английской раскладки на русскую и обратно"""
    # TODO: ГОВНОКОД!
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
