"""
https://pytest.org/en/7.4.x/how-to/skipping.html#skip
"""
import sys

import pytest


# A skip means that you expect your test to pass only if some
# conditions are met. Common examples are skipping windows-only tests
# on non-windows platforms

# Unconditional skip of an entire test module
pytestmark = pytest.mark.skip("All tests still WIP")


# Conditionally skip an entire test module
pytestmark = pytest.mark.skipif(
    sys.platform == "win32",
    reason="Tests for linux only"
)


# Conditionally skip an entire test module, imperative way
if not sys.platform.startswith("win"):
    pytest.skip("Skipping windows-only tests", allow_module_level=True)


# Unconditional skip, `reason` is optional
@pytest.mark.skip(reason="No way of currently testing this")
def test_something_unconditional():
    pass


# Conditional skip, evaluated when collecting tests (import time)
@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason="Requires Python 3.10 or higher"
)
def test_something_conditional():
    pass


# Conditional skip evaluating the condition dynamically
def test_function():
    condition = False

    if not condition:
        pytest.skip("Condition was not met")


# We can share skipif markers between modules
minversion = pytest.mark.skipif(
    pytest.__versioninfo__ < (7, 4),
    reason="At least pytest-7.4 required"
)


@minversion
def test_function():
    pass


# Skip all the methods of a test case
@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Does not run on Windows"
)
class TestPosixCalls:
    def test_function(self):
        pass


#
# An xfail means that we expect a test to fail for some reason. A
# common example is a test for a feature not yet implemented, or a bug
# not yet fixed. When a test passes despite being expected to fail
# (marked with pytest.mark.xfail), it’s an xpass and will be reported
# in the test summary
#

# This test will run but no traceback will be reported if it fails.
# Instead, reporting will list it in the “expected to fail” (XFAIL) or
# “unexpectedly passing” (XPASS) sections
# `reason` is optional
@pytest.mark.xfail(reason="This is why this should fail")
def test_function():
    pass


# Conditionally mark as xfail
@pytest.mark.xfail(sys.platform == "win32",
                   reason="Bug in a 3rd party library on Windows")
def test_function():
    pass


# Conditional and imperative XFAIL
def test_function():
    condition = False

    if not condition:
        pytest.xfail("Failing (but should work)")


# Report but don't even run
# Useful when the test is causing issues
@pytest.mark.xfail(run=False)
def test_function():
    pass
