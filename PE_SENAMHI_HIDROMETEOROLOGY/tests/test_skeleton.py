# -*- coding: utf-8 -*-

import pytest
from pe_senamhi_hidrometeorology.skeleton import fib

__author__ = "Cesar Luis Aybar Camacho"
__copyright__ = "Cesar Luis Aybar Camacho"
__license__ = "mit"


def test_fib():
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(7) == 13
    with pytest.raises(AssertionError):
        fib(-10)
