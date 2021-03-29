import re
import typing as t

from loguru import logger
from vkwave.api import APIOptionsRequestContext
from vkwave.bots import PhotoUploader
from vkwave.bots import VoiceUploader
from vkwave.types.objects import MessagesMessageAttachment

from jacob.services.exceptions import AttachmentLimitExceeded


async def load_attachments(
    api: APIOptionsRequestContext,
    attachments: t.List["MessagesMessageAttachment"],
    from_id: int,
) -> str:
    """
    Загружает вложения на сервера ВК.

    Args:
        api: Объект API ВКонтакте
        attachments: Вложения
        from_id: Отправитель сообщения с вложениями

    Raises:
        AttachmentLimitExceeded: Если количество вложений больше 10

    Returns:
        str: Список идентификаторов вложений, готовых к отправке
    """
    atchs = []
    photo_uploader = PhotoUploader(api)
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
            atch = await photo_uploader.get_attachment_from_link(
                from_id,
                max_url,
            )
            atchs.append(atch)
        if attach.doc:
            return ",".join(atchs)
        if attach.audio_message:
            atch = await am_uploader.get_attachment_from_link(
                from_id,
                attach.audio_message.link_ogg,
            )
            atchs.append(atch)
    return ",".join(atchs)


def translate_string(s: str) -> str:
    """
    Переводит строку с английской раскладки на русскую и обратно.

    Args:
        s: Исходная строка

    Returns:
        str: Переведенная строка
    """
    layout = dict(
        zip(
            map(
                ord,
                "qwertyuiop[]asdfghjkl;'zxcvbnm,./`"
                'QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~',
            ),
            "йцукенгшщзхъфывапролджэячсмитьбю.ё" "ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё",
        ),
    )
    en_layout = dict(
        zip(
            map(
                ord,
                "йцукенгшщзхъфывапролджэячсмитьбю.ё"
                "ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё",
            ),
            "qwertyuiop[]asdfghjkl;'zxcvbnm,./`" 'QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~',
        ),
    )
    tr = s.translate(layout)
    if tr == s:
        tr = s.translate(en_layout)
    return tr


def get_university_abbreviation(uni: str):
    letters = []
    for word in uni.split():
        index = 2 if re.match(r"(владимир.*)", word, re.IGNORECASE) else 1
        letters.append(word[0:index].capitalize())
        logger.warning(index)
    logger.warning(letters)
    return "".join(letters)
