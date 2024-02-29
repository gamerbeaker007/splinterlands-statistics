from src.api import spl
from src.static.static_values_enum import Format


def test_add_numbers():
    assert len(Format) == 2


def test_second():
    assert len(spl.get_settings()) == 108
