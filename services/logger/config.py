fmt = "{time:YY-MM-D@HH:mm:ss zz} | {module}.{function} | {level} | {message}"

config = {
    "handlers": [
        {"sink": "jacob.log", "format": fmt, "rotation": "00:00", "enqueue": True,},
    ]
}
