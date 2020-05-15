from pathlib import Path

import requests


async def load_attachments(bot, attachments, from_id):
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
