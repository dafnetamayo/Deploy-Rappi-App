from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Filtro personalizado para obtener un valor de un diccionario usando una clave.
    Uso en plantilla: {{ my_dict|get_item:key }}
    """
    return dictionary.get(key, '')
