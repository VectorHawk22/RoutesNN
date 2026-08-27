[app]
# ===== Общие настройки пакета =====
title = Basketball Click

# Имя пакета (без апострофов и спецсимволов!)
package.name = basketballclick

# Домен-производитель (формат обратного домена, строчными буквами)
package.domain = org.seryozha

# Версия и код версии
version = 1.0
android.version_code = 1

# Минимальная версия Android и таргет
android.min_sdk_version = 21
android.target_sdk_version = 33

# Записи REPL/service не нужны, безусловно отключаем
android.allow_backup = True
android.orientation = landscape
android.fullscreen = 1

# ===== Источники =====
source.dir = .
source.include_exts = py,png,jpg,jpeg,json,txt
source.exclude_exts = pyc,pyo,md
source.exclude_dirs = tests,bin,.buildozer,build,dist

# Запрещаем копировать сам spec и папку логики сборки
source.exclude_patterns = buildozer.spec,*.md

# ===== Точка входа =====
p4a.bootstrap = sdl2
p4a.entry_point = main.py

# ===== Зависимости =====
# pygame тянет SDL2; pillow нужен для работы с картинками (обрезка/поворот)
requirements = python3,pygame,pyjnius,pillow

# Запрещаем символические ссылки внутри APK (мешают некоторым устройствам)
android.private_storage = True

# Окно: скейлим сгенерированную картинку 600x490 на весь экран
android.wakelock = True

# Учётная пара и подпись (сгенерируйте свои ключи для Google Play)
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a

# Иконка и пресплэш (замените на свои файлы)
# android.icon.filename = %(source.dir)s/icon.png
# android.presplash.filename = %(source.dir)s/presplash.png

[buildozer]
log_level = 2
warn_on_root = 1
