# ============================================================
#  Сборка APK в Google Colab (для Basketball Click)
# ============================================================
#  Как пользоваться:
#   1. Открой https://colab.research.google.com  -> New Notebook
#   2. Меню Runtime -> Change runtime type -> GPU (ускоряет тему, не критично)
#   3. Вставь ВЕСЬ этот код в ОДНУ ячейку и нажми Shift+Enter (или выполни по блокам)
#   4. Когда появится файл APK - слева появится панель "Files", скачай его
#
#  Нужен файл:  basketballclick_ready.zip
#  Он лежит в папке проекта:
#    version1_1/aaaaa_clicker_apk(Seryozha's).pygame/basketballclick_ready.zip
# ============================================================

import os, sys, zipfile, glob, shutil, time

# ---------- 1. Установка зависимостей для сборки ----------
print("Устанавливаю system-пакеты...")
os.system("apt-get update -qq > /dev/null 2>&1")
os.system("apt-get install -y -qq python3-pip git zip unzip openjdk-17-jdk \
          build-essential pkg-config autoconf libtool libffi-dev libssl-dev \
          libncurses-dev ccache > /dev/null 2>&1")

print("Ставлю buildozer и cython...")
os.system("pip install -q buildozer cython pygments > /dev/null 2>&1")

# ---------- 2. Загрузка проекта (перетащи zip в Files или запусти ниже) ----------
# Проще всего перетащить basketballclick_ready.zip в панель Files,
# тогда он окажется в /content/

PROJECT_ROOT = "/content"

# Если архива ещё нет — подсказка
found = glob.glob("/content/basketballclick_ready.zip")
if not found:
    print("=" * 60)
    print("НЕ НАЙДЕН файл basketballclick_ready.zip в /content/")
    print("Перетащи файл из папки проекта в панель Files (слева)")
    print("Или выполни код ниже отдельно.")
    print("=" * 60)
    raise SystemExit(1)

zip_path = found[0]
print("Найден архив:", zip_path)

# ---------- 3. Распаковка ----------
# ВНИМАНИЕ: в /content/ могут быть и другие файлы/папки Colab.
# Вычищаем только те, что перезапишем.
with zipfile.ZipFile(zip_path, "r") as z:
    z.extractall(PROJECT_ROOT)
print("Распаковано в", PROJECT_ROOT)
print("Содержимое:", sorted(os.listdir(PROJECT_ROOT))[:20])

# ---------- 4. Сборка ----------
os.chdir(PROJECT_ROOT)
print("Запускаю buildozer android debug (впервые ~30-60 мин)...")
start = time.time()
ret = os.system("yes | buildozer -v android debug")
print("Сборка завершена за %.1f мин, код возврата=%d" % ((time.time()-start)/60, ret))

# ---------- 5. Показ APK ----------
apks = sorted(glob.glob(PROJECT_ROOT + "/bin/*.apk"))
if apks:
    for a in apks:
        print("APK:", a, "%.2f MB" % (os.path.getsize(a)/1024/1024))
    # Colab: скачать показываем ссылку
    from google.colab import files
    files.download(apks[-1])
else:
    print("APK не найден — смотри логи выше на предмет ошибок.")
