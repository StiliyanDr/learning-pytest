"""
https://docs.python.org/dev/library/unittest.mock.html
https://docs.python.org/3.8/library/unittest.mock-examples.html
"""
#
# What are stubs and mocks?
# Mock objects "expect" certain methods to be called on them, and
# typically cause a unit test to fail if their expectations aren't met.
# Stub objects provide canned responses but typically do not directly
# cause the unit test to fail. They are typically just used so that the
# object we're testing gets the data it needs to do its work
#

from unittest.mock import (
    Mock,
    MagicMock,
    patch,
    create_autospec,
    call,
)

import pytest

import mypkg
from mypkg import (
    constants as const,
    utils,
)


#
# Mock and MagicMock objects create attributes and methods as we access
# them and store details of how they have been used. We can configure
# them, to specify return values or limit what attributes are available,
# and then make assertions about how they have been used
# (We should use MagicMock by default, the difference with Mock is
# discussed later)
#
class MyClass:
    def calculate(self, n, is_something, key):
        return n + int(is_something) + len(key)


#
# Mocking a method
#
def my_function(obj):
    v = obj.calculate(0, True, key="value")

    return v ** 2


def test_my_function_returns_square_of_return_value():
    obj = MyClass()
    obj.calculate = MagicMock(return_value=3)

    result = my_function(obj)

    assert result == 9
    assert obj.calculate.called
    obj.calculate.assert_called_with(0, True, key="value")


#
# Mocking an attribute
#
def my_func(obj):
    return obj.value ** 2


def test_my_func_squares_value():
    obj = MyClass()
    obj.value = 3

    result = my_func(obj)

    assert result == 9
    assert obj.value == 3


#
# Mocking a callable
#
def my_func_callable(c, x):
    return c(x) + 10


def test_my_func_passes_x_and_adds_10():
    c = MagicMock(return_value=5)
    x = 10

    result = my_func_callable(c, x)

    assert result == 15
    c.assert_called_once_with(x)


#
# Throwing an exception
#
def test_an_exception_is_thrown():
    obj = MagicMock(side_effect=ValueError("Error!"))

    with pytest.raises(ValueError):
        obj()


def test_method_raises_an_exception():
    obj = MagicMock()
    obj.method.side_effect = ValueError("Error!")

    with pytest.raises(ValueError):
        obj.method()


#
# Mocking behaviour with specific method
#
def test_behaviour_is_copied():
    obj = MagicMock(side_effect=lambda x: x + 1)

    assert obj(0) == 1
    assert obj(1) == 2


#
# Providing sequence of return values
#
def test_sequenced_results():
    obj = MagicMock(side_effect=[3, 1])

    assert obj() == 3
    assert obj() == 1


#
# Remember that attributes are created on access
#
class Closer:
    def close(self, obj):
        obj.close()


def test_close_is_called():
    closer = Closer()
    obj = MagicMock()

    closer.close(obj)

    obj.close.assert_called_once()


#
# Patching classes
#


def my_f():
    c = mypkg.Foo()

    return c.method()


@patch("mypkg.Foo")
def test_patching_a_class(foo_mock):
    instance = foo_mock.return_value
    instance.method.return_value = "bar"

    result = my_f()

    assert result == "bar"


def test_patching_a_class_cm():
    with patch("mypkg.Foo") as foo_mock:
        instance = foo_mock.return_value
        instance.method.return_value = "baz"

        result = my_f()

        assert result == "baz"


#
# Mocking magic methods
#
def test_mocking_str():
    mock = MagicMock()
    mock.__str__.return_value = "value"

    result = str(mock)

    assert result == "value"
    mock.__str__.assert_called_once()


# The difference between Mock and MagicMock - special/magic methods
# are mocks for MagicMock; created explicitly for Mock
def test_mocking_str_without_magic():
    mock = Mock()
    mock.__str__ = Mock(return_value="val")

    result = str(mock)

    assert result == "val"
    mock.__str__.assert_called_once()


#
# Mocking but keeping a certain specification
# Useful as not to couple tests to client code:
#  when the class changes, the mock should adapt so as not to keep
#  the tests passing
#
class C:
    def __init__(self):
        self.x = 10

    def method(self):
        return self.x + 12


def test_attribute_error_is_raised_for_missing_attributes():
    mock = MagicMock(spec=C)

    with pytest.raises(AttributeError):
        mock.missing_method()


def test_simple_speccing_does_not_go_beyond_attribute_names():
    mock = MagicMock(spec=C)

    mock.method(123)

    mock.method.assert_called_once_with(123)
    # typo, no such method on a mock!
    mock.method.asrrrrrrrt_called_once()


#
# Autospeccing is done recursively - including specs of attributes too
#

# Mocking function specifications
def sum_of(a, b):
    return a + b


def test_function_spec():
    mock = create_autospec(sum_of, return_value=None)

    assert mock(0, 1) is None

    with pytest.raises(TypeError):
        mock("hi")


# Mocking ctor spec
class A:
    def __init__(self, x):
        self.x = x

    def method(self, y):
        return self.x + y


def test_mocking_ctor_spec():
    class_mock = create_autospec(A)

    with pytest.raises(TypeError):
        class_mock(1, 2)


# Mocking a callable specification
class Callable:
    def __call__(self, x):
        return x

    def method(self, y):
        return y ** 2


def test_mocking_callable_spec():
    c = Callable()
    mock = create_autospec(c)

    mock(12)

    mock.assert_called_once_with(12)

    with pytest.raises(TypeError):
        mock(1, 2)


# Mocking spec of object
def test_mocking_object_spec():
    c = Callable()
    mock = create_autospec(c)

    mock.method(3)

    mock.method.assert_called_once_with(3)

    with pytest.raises(TypeError):
        mock.method()


#
# Listing calls to mocks (including child mocks)
#
def test_checking_all_calls():
    mock = MagicMock()
    expected_calls = [call.method(), call.attribute.method(10, x=53)]

    mock.method()
    mock.attribute.method(10, x=53)

    assert mock.mock_calls == expected_calls


# Arguments of nested calls are not tracked!
def test_arguments_of_nested_calls_are_not_tracked():
    mock = MagicMock()

    mock.method(key="value").f()

    assert mock.mock_calls[-1] == call.method(key="v").f()


# Listing nested calls
def test_listing_nested_calls():
    mock = Mock()

    # mock.connection.cursor()
    # obtain the resulting mock
    cursor = mock.connection.cursor.return_value
    # cursor.execute()
    cursor.execute.return_value = ["foo"]
    expected = call.connection.cursor().execute("SELECT 1").call_list()

    mock.connection.cursor().execute("SELECT 1")

    assert mock.mock_calls == expected


# Listing calls to the mock as a callable
def test_listing_callable_calls():
    mock = MagicMock()
    expected = [call(1, 2), call("str"), call(False, 3.14)]

    mock(1, 2)
    mock.method(1, 2)
    mock("str")
    mock(False, 3.14)

    assert mock.call_args_list == expected


# Checking that certain calls were made
#  any_order=True if order doesnt matter
def test_checking_certain_calls_were_made():
    mock = MagicMock()

    mock.f()
    mock.item.g()
    mock.h().f()

    mock.assert_has_calls(
        call.h().f().call_list()
    )


#
# Patching
# https://docs.python.org/3.8/library/unittest.mock-examples.html#patch-decorators
# https://docs.python.org/3.8/library/unittest.mock.html#where-to-patch
#

# Patching a class within a module
# When the module is imported
#  Note: imagine mypkg.Foo is used in the module we are testing
@patch("mypkg.Foo")
def test_patching_imported_module_class(foo_mock):
    assert mypkg.Foo is foo_mock


# Patching a class within a module
# When the class is imported
#  Note: imagine this import is done in the module we are testing;
#  we'd patch moduleundertest.Foo
from mypkg import Foo


def test_patching_imported_class():
    with patch("tests.mocking.Foo") as foo_mock:
        assert Foo is foo_mock


class SomeClass:
    C = 10

    def __init__(self, x):
        self.x = x

    def get(self):
        return self.x


# Patching a class attribute
@patch.object(SomeClass, "get")
def test_patching_class_method(get_mock):
    instance = SomeClass(0)
    get_mock.return_value = 100

    assert instance.get() == 100


# Patching with specific value
def test_patching_with_specific_value():
    new_value = 1234

    with patch.object(SomeClass, "C", new_value):
        assert SomeClass.C == new_value


# Patching a module variable (Similar to classes, really)
@patch("mypkg.constants.FIVE", 10)
def test_patching_a_module_variable():
    assert const.FIVE == 10


def test_patching_a_module_var():
    new_value = 21

    with patch.object(const, "FIVE", new_value):
        assert const.FIVE == new_value


# Patching built-ins
def test_patching_built_ins():
    made_up_handle = 1000
    open_mock = MagicMock(return_value=made_up_handle)

    with patch("builtins.open", open_mock):
        handle = open("filename", "rb")

    assert handle == made_up_handle
    open_mock.assert_called_once_with("filename", "rb")


# Patching every test in a test case
@patch.object(const, "FIVE", 3)
class TestPatchingCase:
    def test_sum_one_to_five(self):
        assert utils.sum_from_one_to(const.FIVE) == 6

    def test_five_is_three(self):
        assert const.FIVE == 3


# NOTE: stacking decorators passes them from bottom up
# def test_func(dec_one, dec_two)


# Patching dictionaries
def test_patching_dict_adding_values():
    d = {"a": 1, "b": 2}

    with patch.dict(d, {"c": 3}):
        assert d == {"a": 1, "b": 2, "c": 3}


def test_patching_dict_entire_value():
    d = {"a": 1, "b": 2}

    with patch.dict(d, {"c": 3}, clear=True):
        assert d == {"c": 3}


# Patching multiple tests in a test case
@patch("mypkg.Foo")
class TestPatchingManyMethods:
    def test_one(self, FooMock):
        assert mypkg.Foo is FooMock

    def test_two(self, FooMock):
        assert mypkg.Foo is FooMock

    def not_a_test(self):
        return None


#
# Mocking a dictionary
#
my_dict = {'a': 1, 'b': 2, 'c': 3}
def getitem(name):
    return my_dict[name]

def setitem(name, val):
    my_dict[name] = val


def test_mocking_a_dictionary():
    mock = MagicMock()
    mock.__getitem__.side_effect = getitem
    mock.__setitem__.side_effect = setitem

    mock["x"] = 10
    mock["y"] = 20

    assert mock["a"] == 1
    assert mock["c"] == 3

    assert mock.__getitem__.call_args_list == [
        call("a"),
        call("c")
    ]
    assert mock.__setitem__.call_args_list == [
        call("x", 10),
        call("y", 20)
    ]
