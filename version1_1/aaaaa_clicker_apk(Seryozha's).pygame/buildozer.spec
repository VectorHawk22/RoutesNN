[app]

# ===== Пакет =====
title = Basketball Click
package.name = basketballclick
package.domain = org.seryozha
version = 1.0
android.version_code = 1

# ===== Источники =====
# Папка, в которой лежит игра (buildozer запускается из неё)
source.dir = .
source.include_exts = py,png,jpg,jpeg,json,txt,kv,ttf,ttc
source.exclude_exts = pyc,pyo,md,bak,spec

# ===== Ориентация и полноэкранный режим =====
android.orientation = landscape
android.fullscreen = 1

# ===== Версии Android =====
android.min_sdk_version = 21
android.target_sdk_version = 33

# ===== Архитектуры =====
# arm64-v8a - большинство современных телефонов
android.archs = arm64-v8a, armeabi-v7a

# ===== Зависимости =====
# kivy - движок GUI; pillow - работа с картинками (обрезка/поворот)
requirements = python3,kivy,pillow

# ===== Bootstrap (движок окна на Android) =====
# Kivy работает через SDL2
p4a.bootstrap = sdl2

# ===== Прочее =====
android.wakelock = True
android.accept_sdk_license = True
# Цвет пресплэша пока не используем иконки по умолчанию
android.presplash_color = #FFFFFF

[buildozer]
log_level = 2
warn_on_root = 1
