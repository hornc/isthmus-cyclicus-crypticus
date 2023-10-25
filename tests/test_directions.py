import pytest
from complex import Translator 

direction_tests = [
    ('U', [0.0, 0.0, 1.0]),
    ('D', [0.0, 0.0, -1.0]),
    ('N', [-1.0, 0.0, 0.0]),
    ('S', [1.0, 0.0, 0.0]),
    ('E', [0.0, 1.0, 0.0]),
    ('W', [0.0, -1.0, 0.0]),
    ('Ne', [-1.0, 1.0, 0.0]),
    ('En', [-1.0, 1.0, 0.0]),
    ('Nen', [-1.0, 0.5, 0.0]),
    ('Nee', [-0.5, 1.0, 0.0]),
    ('Nuuu', [-0.3333333333333333, 0.0, 1.0]),
]


@pytest.mark.parametrize('direction,expect', direction_tests)
def test_directions(direction, expect):
    t = Translator('test', '')
    msg, vector =  t.abs_dir(0, direction)
    print('RESULT:', msg, vector)
    assert vector == expect
