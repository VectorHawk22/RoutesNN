import os


def is_android():
    """True when running inside an Android (python-for-android) app."""
    return ("ANDROID_ARGUMENT" in os.environ or
            "ANDROID_PRIVATE" in os.environ or
            "ANDROID_APP_PATH" in os.environ)


def assets_dir():
    """Read-only directory with game images (the bundled .py directory)."""
    return os.path.dirname(os.path.abspath(__file__))


def save_dir():
    """Writable directory for save.json / settings.json.

    On Android the app bundle is read-only, so we save into the app's
    private writable storage. On desktop we keep using the project dir so
    that development/testing keeps working exactly as before.
    """
    try:
        from android.storage import app_storage_path
        d = app_storage_path()
        if d:
            os.makedirs(d, exist_ok=True)
            return d
    except Exception:
        pass

    for var in ("ANDROID_PRIVATE", "ANDROID_ARGUMENT"):
        d = os.environ.get(var)
        if d:
            os.makedirs(d, exist_ok=True)
            return d

    return assets_dir()
