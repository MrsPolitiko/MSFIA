# MSFIA Chat

MSFIA — это простой корпоративный чат-клиент и сервер на Python с графическим интерфейсом (PyQt5) и поддержкой уведомлений о новых сообщениях.

## Назначение
Позволяет сотрудникам обмениваться сообщениями в локальной сети через удобный интерфейс.

## Состав
- `client/` — клиентское приложение (GUI)
- `server/` — сервер для обработки сообщений

## Запуск
1. Запустите сервер: `python server/server.py`
2. Запустите клиент: `python client/client.py`

## Сборка portable-версии
Для создания переносимой версии используйте PyInstaller.
