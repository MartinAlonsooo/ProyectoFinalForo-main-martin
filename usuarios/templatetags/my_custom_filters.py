from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Permite acceder a un valor de un diccionario por su clave."""
    if key in dictionary:
        return dictionary.get(key)
    return key
    
@register.filter
def add(value, arg):
    """Suma el argumento al valor."""
    try:
        return int(value) + int(arg)
    except (ValueError, TypeError):
        try:
            return value + arg
        except TypeError:
            return value

@register.filter
def split(value, arg):
    """Divide una cadena por el argumento dado."""
    if value is None:
        return []
    return value.split(arg)

@register.filter
def trim(value):
    """Elimina los espacios en blanco iniciales y finales de una cadena."""
    if isinstance(value, str):
        return value.strip()
    return value