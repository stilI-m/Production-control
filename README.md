# 🏭 Manufacturing API

REST API сервис для управления производственными партиями, агрегацией деталей и асинхронной обработкой данных.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-async-4169E1?logo=postgresql&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-tasks-37814A?logo=celery&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

---

## 📋 Содержание

- [О проекте](#-о-проекте)
- [Стек технологий](#-стек-технологий)
- [Архитектура и основные фичи](#-архитектура-и-основные-фичи)
- [Быстрый старт (Docker Compose)](#-быстрый-старт-docker-compose)
- [Локальная разработка без Docker](#-локальная-разработка-без-docker)
- [Документация API](#-документация-api)
- [Структура проекта](#-структура-проекта)

---

## 📖 О проекте

**Manufacturing API** — сервис для учёта и обработки производственных данных: создание и закрытие партий, привязка серийных номеров деталей, фоновая обработка Excel-отчётов и уведомление внешних систем через webhooks.

## 🚀 Стек технологий

| Категория | Технологии |
|---|---|
| **Backend** | FastAPI, Python 3.11+ |
| **База данных** | PostgreSQL, SQLAlchemy (Async), Alembic |
| **Фоновые задачи** | Celery + Redis / RabbitMQ |
| **Хранилище объектов** | MinIO (S3-совместимое) |
| **Интеграции** | Webhook-система с HMAC-подписью |

## 🏗 Архитектура и основные фичи

### 📦 Управление партиями (Batches)
Создание, закрытие партий и получение статистики по ним.

### 🔗 Агрегация деталей
Привязка серийных номеров к производственным партиям.

### 📊 Асинхронный импорт/экспорт
Загрузка и выгрузка Excel-отчётов в фоне с использованием MinIO для хранения файлов и Celery для обработки задач без блокировки основного потока.

### 🔔 Webhooks
Подписка внешних систем на события (`batch_created`, `batch_closed` и др.) с гарантированной доставкой через очереди.

---

## 🛠 Быстрый старт (Docker Compose)

Самый простой способ запустить проект — использовать Docker.

**1. Склонируйте репозиторий:**

```bash
git clone <url_репозитория>
cd <имя_папки>
```

**2. Создайте файл конфигурации:**

```bash
cp .env.example .env
```

При необходимости отредактируйте `.env` под свои нужды.

**3. Запустите инфраструктуру** (БД, MinIO, Redis, воркеры, API):

```bash
docker-compose up -d --build
```

**4. Примените миграции базы данных:**

```bash
docker-compose exec api alembic upgrade head
```

**Готово! 🎉**

| Сервис | Адрес |
|---|---|
| API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |

---

## 📦 Локальная разработка без Docker

Если вы хотите запускать сервис напрямую, без контейнеризации:

**1. Поднимите инфраструктуру**

Понадобятся локально установленные и запущенные:
- PostgreSQL
- MinIO (или совместимое S3-хранилище)
- Redis / RabbitMQ (брокер для Celery)

**2. Создайте виртуальное окружение**

```bash
python3.11 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

**3. Установите зависимости**

```bash
pip install -r requirements.txt
```

**4. Настройте `.env`**

```bash
cp .env.example .env
```

Укажите параметры подключения к вашим локальным БД, MinIO и брокеру задач.

**5. Примените миграции**

```bash
alembic upgrade head
```

**6. Запустите API**

```bash
uvicorn src.main:app --reload
```

**7. Запустите Celery-воркер** (в отдельном терминале)

```bash
celery -A src.celery_app worker --loglevel=info
```

---

## 📚 Документация API

После запуска сервиса интерактивная документация доступна по адресам:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 📁 Структура проекта

```
.
├── src/
│   ├── main.py            # Точка входа FastAPI
│   ├── celery_app.py      # Конфигурация Celery
│   ├── api/                # Роуты и эндпоинты
│   ├── models/             # SQLAlchemy модели
│   ├── schemas/             # Pydantic схемы
│   └── services/           # Бизнес-логика
├── alembic/                # Миграции БД
├── docker-compose.yml
├── .env.example
└── requirements.txt
```

---

<p align="center">Сделано с ❤️ для эффективного управления производством</p>
