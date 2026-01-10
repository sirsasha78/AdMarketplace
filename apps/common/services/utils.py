def set_dict_attr(obj, data: dict):
    """Устанавливает атрибуты объекта из словаря."""

    for attr, value in data.items():
        setattr(obj, attr, value)
    return obj
