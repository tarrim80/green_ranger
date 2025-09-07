from geoalchemy2.elements import WKBElement, WKTElement
from shapely.geometry import mapping
from shapely.wkb import loads as wkb_loads
from shapely.wkt import loads as wkt_loads


def geometry_to_dict(element: WKTElement | WKBElement | dict) -> dict:
    """Преобразует WKTElement или WKBElement из БД в GeoJSON-совместимый словарь."""
    if isinstance(element, WKTElement):
        return mapping(wkt_loads(element.data))
    if isinstance(element, WKBElement):
        return mapping(wkb_loads(element.data))
    return element
