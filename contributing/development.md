# Локальная разработка

Скачайте себе на компьютер свой форк:

``` bash
git clone https://github.com/YOUR_USERNAME/jacob
```

Убедитесь, что у вас установлен Python версии не ниже 3.9...

``` bash
python --version
Python 3.9.2
```

и PostgreSQL не ниже 13

``` bash
psql (PostgreSQL) 13.2
```

Установите Poetry, менеджер зависимостей и docker-compose

``` bash
pip install poetry docker-compose
```

Перейдите в директорию проекта

``` bash
cd jacob
```

Используйте файл `.env.example`, чтобы настроить свои переменные окружения
```bash
mv .env.example .env
```

```bash
vim .env
```

Установите зависимости:

``` bash
poetry install
```

Настройте базу данных

``` bash
createdb jacob
PYTHONPATH=. poetry run python jacob/database/models.py
PYTHONPATH=. poetry run python generate_test_data.py
```

Запустите проект

```bash
docker-compose up
```
