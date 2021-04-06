import os
import re
from typing import List

from vkwave.api import APIOptionsRequestContext
from vkwave.bots import DocUploader, PhotoUploader, VoiceUploader
from vkwave.types.objects import (
    DocsDoc,
    MessagesAudioMessage,
    MessagesMessageAttachment,
    PhotosPhoto,
)

from jacob.services.exceptions import AttachmentLimitExceeded


async def _load_image(
    api: APIOptionsRequestContext,
    from_id: int,
    photo: PhotosPhoto,
) -> str:
    photo_uploader = PhotoUploader(api)
    return await photo_uploader.get_attachment_from_link(
        from_id,
        photo.sizes[-1].url,
    )


async def _load_doc(
    api: APIOptionsRequestContext,
    from_id: int,
    doc: DocsDoc,
) -> str:
    doc_uploader = DocUploader(api)
    return await doc_uploader.get_attachment_from_link(
        from_id,
        doc.url,
        file_extension=doc.ext,
        file_name=os.path.splitext(doc.title)[0],
    )


async def _load_audio(
    api: APIOptionsRequestContext,
    from_id: int,
    audio: MessagesAudioMessage,
) -> str:
    am_uploader = VoiceUploader(api)
    return await am_uploader.get_attachment_from_link(
        from_id,
        audio.link_ogg,
    )


async def load_attachments(
    api: APIOptionsRequestContext,
    attachments: List[MessagesMessageAttachment],
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
    attaches = []

    if len(attachments) > 10:
        raise AttachmentLimitExceeded("Количество вложений не может быть больше 10")
    for attach in attachments:
        if attach.photo:
            attaches.append(
                await _load_image(
                    api,
                    from_id,
                    attach.photo,
                ),
            )
        if attach.doc:
            attaches.append(
                await _load_doc(
                    api,
                    from_id,
                    attach.doc,
                ),
            )
        if attach.audio_message:
            attaches.append(
                await _load_audio(
                    api,
                    from_id,
                    attach.audio_message,
                ),
            )

    return ",".join(attaches)


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
    return "".join(letters)
