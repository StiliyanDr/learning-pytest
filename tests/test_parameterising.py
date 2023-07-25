import pytest


#
# Parameterising test functions
#
# The pytest.mark.parametrize decorator enables parametrisation of
# arguments for a test function
# Note that arguments are evaluated statically so side effects persist
@pytest.mark.parametrize("expr,value", [("1+1", 2), ("2*3", 6)])
def test_evaluation(expr, value):
    assert eval(expr) == value


#
# Parameterising all the tests in a test case
#
@pytest.mark.parametrize("n,expected", [(1, 2), (3, 4)])
class TestClass:
    def test_simple_case(self, n, expected):
        assert n + 1 == expected

    def test_weird_case(self, n, expected):
        assert (n * 1) + 1 == expected


#
# Parameterising all the tests in a module
#
# pytestmark = pytest.mark.parametrize("n,expected", [(1, 2), (3, 4)])


#
# Stacking decorators to produce 'product' of parameterised arguments
# 0-1, 0-1, 0-2, 0-2 (y1-x1, y1-x2, ...)
#
@pytest.mark.parametrize("x", [0, 0])
@pytest.mark.parametrize("y", [1, 2])
def test_function(y, x):
    assert x + y == y
