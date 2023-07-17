"""
https://pytest.org/en/7.4.x/getting-started.html
"""

import pytest

from mypkg import utils


# Stand-alone test
def test_basic_test():
    zero = 0

    assert zero == 0


# test case
# each test has its own instance
# class variables are shared
class TestVerifyIsOdd:
    # test
    def test_verify_is_odd_raises_exception_for_even_numbers(self):
        with pytest.raises(ValueError):
            utils.verify_is_odd(2)

    # test
    def test_verify_is_odd_does_nothing_for_odd_numbers(self):
        assert utils.verify_is_odd(1) is None
