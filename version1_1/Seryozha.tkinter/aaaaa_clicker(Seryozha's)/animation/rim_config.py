import os

# Калибровка позиции кольца для каждой картинки корзины.
# Доли от размера ОБРЕЗАННОГО изображения (после удаления прозрачных полей):
#   cx, cy - центр кольца (точка попадания мяча)
#   x0     - передняя кромка кольца (точка удара при промахе)
RIM_CALIBRATION = {
    "basket.png":  {"cx": 0.24, "cy": 0.19, "x0": 0.03},
    "basket2.png": {"cx": 0.11, "cy": 0.20, "x0": 0.01},
    "basket3.png": {"cx": 0.24, "cy": 0.24, "x0": 0.03},
    "basket4.png": {"cx": 0.18, "cy": 0.42, "x0": 0.02},
}

# Запасная калибровка для неизвестных файлов
DEFAULT_RIM = {"cx": 0.22, "cy": 0.20, "x0": 0.04}


def get_rim_calibration(basket_file):
    name = os.path.basename(basket_file)
    return RIM_CALIBRATION.get(name, DEFAULT_RIM)
