"""
https://pytest.org/en/7.4.x/how-to/fixtures.html
"""


import pytest

# A fixture provides context for tests
# It could include some data set or a DB initialised with known
# parameters
# Fixtures define the steps and data that constitute the arrange phase
# of a test
# In pytest, they are functions we define. They can also be used to
# define a test’s act phase; this is a powerful technique for designing
# more complex tests
# The services, state, or other operating environments set up by
# fixtures are accessed by test functions through arguments. For each
# fixture used by a test function there is typically a parameter
# (named after the fixture) in the test function’s definition


class Fruit:
    def __init__(self, name):
        self.name = name
        self.cubed = False

    def cube(self):
        self.cubed = True

    def __eq__(self, other):
        return (self.name == other.name and
                self.cubed == other.cubed)


@pytest.fixture
def my_fruit():
    return Fruit("apple")


@pytest.fixture
def fruit_basket(my_fruit):
    return [Fruit("banana"), my_fruit]


def test_my_fruit_in_basket(my_fruit, fruit_basket):
    assert my_fruit in fruit_basket

# This example also shows us how fixtures can be used in pytest
# to extract set up code (as alternative to jUnit style setUp and
# tearDown functions). Fixtures can be used at test level, class level
# (test case level) and even module level
#
# When pytest goes to run a test, it looks at the parameters in that
# test function’s signature, and then searches for fixtures that have
# the same names as those parameters. Once pytest finds them, it runs
# those fixtures, captures what they returned (if anything), and passes
# those objects into the test function as arguments
# Note that this is also true for fixtures, that is, they can "request"
# other fixtures just like test methods


class FruitSalad:
    def __init__(self, fruit_bowl):
        self.fruit = tuple(fruit_bowl)
        self._cube_fruit()

    def _cube_fruit(self):
        for f in self.fruit:
            f.cube()


# Arrange
@pytest.fixture
def fruit_bowl():
    return [Fruit("apple"), Fruit("banana")]


def test_fruit_salad_consists_of_cubed_fruit(fruit_bowl):
    # Act
    fruit_salad = FruitSalad(fruit_bowl)

    # Assert
    assert all(f.cubed for f in fruit_salad.fruit)


# Two different tests can request the same fixture and have pytest give
# each test their own result from that fixture. This means set up code
# can be easily achieved by reusing the same fixture in different tests.
# Note also that multiple fixtures can be requested at the same time


@pytest.fixture
def first_entry():
    return [0]


@pytest.fixture
def second_entry():
    return [1]


@pytest.fixture
def aggregate(first_entry, second_entry):
    return (first_entry, second_entry)


@pytest.fixture
def expected_aggregate():
    return ([0], [1])


def test_aggregate_is_sequential(aggregate, expected_aggregate):
    assert list(aggregate) == list(expected_aggregate)


# Fixtures can be requested more than once per test (even implicitly)
# and return values are cached


@pytest.fixture
def order():
    return []


@pytest.fixture
def append_first(order, first_entry):
    order.append(first_entry)


def test_fixtures_are_evaluated_once_per_test(
    append_first,
    order,
    first_entry
):
    assert order == [first_entry]


# We can make a fixture an autouse fixture (always used, even when not
# requested explicitly) by passing in autouse=True to the fixture’s
# decorator
@pytest.fixture(autouse=True)
def append_first(order, first_entry):
    order.append(first_entry)


def test_append_first_is_autoused(order, first_entry):
    assert order == [first_entry]


# Fixtures have a default "function" scope, that is, they are evaluated
# for each test that requests them. This can be changed via the `scope`
# keyword argument of the fixture decorator. The scope can be:
#  - function
#  - class (one per class)
#  - module (one per module)
#  - package (one per package)
# We can define a fixture in a separate module with "module" scope
# and use it in (some of) the tests in various modules. The fixture will
# then be evaluated once for every module that uses it

import smtplib


@pytest.fixture(scope="module")
def smtp_connection():
    return smtplib.SMTP("smtp.gmail.com", 587, timeout=5)


# Fixture finalisation
# Fixtures in pytest offer a very useful teardown system, which allows
# us to define the specific steps necessary for each fixture to clean up
# after itself
# The straightforward and recommended way to use finalisation is via
# yielding fixtures. The idea is similar to that of contextmanagers -
# the fixture does the set up, it yields the value instead of returning
# it and the tear down code follows the yield statement. This way pytest
# can use the value in tests and then run the clean up code after the
# tests
# Once pytest figures out a linear order for the fixtures, it retrieves
# the yielded values. Once the test is finished, pytest will go back
# down the list of fixtures, but in the reverse order, doing the clean
# up
class MailUser:
    def __init__(self):
        self.inbox = []

    def send_email(self, email, other):
        other.inbox.append(email)

    def clear_mailbox(self):
        self.inbox.clear()


class MailAdminClient:
    def create_user(self):
        return MailUser()

    def delete_user(self, user):
        # do some cleanup
        pass


class Email:
    def __init__(self, subject, body):
        self.subject = subject
        self.body = body


@pytest.fixture
def mail_admin():
    return MailAdminClient()


@pytest.fixture
def sending_user(mail_admin):
    user = mail_admin.create_user()
    yield user
    mail_admin.delete_user(user)


@pytest.fixture
def receiving_user(mail_admin):
    user = mail_admin.create_user()
    yield user
    user.clear_mailbox()
    mail_admin.delete_user(user)


@pytest.fixture
def email():
    return Email(subject="Hey!", body="How's it going?")


def test_email_is_received(sending_user, receiving_user, email):
    sending_user.send_email(email, receiving_user)
    assert email in receiving_user.inbox


# There's also a more verbose way to do finalisation
# It requires defining clean up code as functions and requesting the
# test's request-context to register the functions with it
# https://pytest.org/en/7.4.x/how-to/fixtures.html#adding-finalizers-directly

#
# The safest and simplest fixture structure requires limiting fixtures
# to only making one state-changing action each, and then bundling them
# together with their teardown code
# So if we make sure that any successful state-changing action gets torn
# down by moving it to a separate fixture function and separating it from
# other, potentially failing state-changing actions, then our tests will
# stand the best chance at leaving the test environment the way they
# found it
#


#
# Setting up context and running multiple tests on it
#
# Sometimes we may want to run multiple tests after doing all the setup.
# With jUnit style frameworks we typically set up the context with
# functions like setUpClass and setUpTest. The clean up is then provided
# via functions like tearDownClass and tearDownTest. Multiple tests
# can use this mechanism to run on the same context
#
# Now that we know about fixture scope and finalisation, we can see
# how this can be achieved with pytest.
# All that’s needed is stepping up to a larger scope (like class scope),
# then having the ACT step defined as an autouse fixture, and finally,
# making sure all the fixtures are targeting that higher level scope.
#
# In the following example we have fixtures for our various set up
# values which are defined at class scope. We will set up the values
# for a test case (class scope), add an autouse fixture to the class
# so that the ACT step is run once and reused for all the tests. Finally
# we will have a test method for each thing we want to test
#

# base_url and admin_credentials are some fixtures
#@pytest.fixture(scope="class")
#def admin_client(base_url, admin_credentials):
#    return AdminApiClient(base_url, admin_credentials)


#@pytest.fixture(scope="class")
#def user(admin_client):
#    _user = User(name="Susan",
#                 username=f"testuser-{uuid4()}",
#                 password="P4$$word")
#    admin_client.create_user(_user)
#    yield _user
#    admin_client.delete_user(_user)


#@pytest.fixture(scope="class")
#def driver():
#    _driver = Chrome()
#    yield _driver
#    _driver.quit()


#@pytest.fixture(scope="class")
#def landing_page(driver, login):
#    return LandingPage(driver)


#class TestLandingPageSuccess:
#    @pytest.fixture(scope="class", autouse=True)
#    def login(self, driver, base_url, user):
#        driver.get(urljoin(base_url, "/login"))
#        page = LoginPage(driver)
#        page.login(user)
#
#    def test_name_in_header(self, landing_page, user):
#        assert landing_page.header == f"Welcome, {user.name}!"
#
#    def test_sign_out_button(self, landing_page):
#        assert landing_page.sign_out_button.is_displayed()
#
#    def test_profile_link(self, landing_page, user):
#        profile_href = urljoin(base_url, f"/profile?id={user.profile_id}")
#        assert landing_page.profile_link.get_attribute("href") == profile_href


# Notice that the methods are only referencing self in the signature as
# a formality. No state is tied to the actual test class as it might be
# in the unittest framework. Everything is managed by the pytest
# fixture system
# Each method only has to request the fixtures that it actually needs
# without worrying about order. This is because the act fixture is an
# autouse fixture, and it made sure all the other fixtures executed
# before it. There’s no more changes of state that need to take place,
# so the tests are free to make as many non-state-changing queries as
# they want without risking stepping on the toes of the other tests
#
# The login fixture is defined inside the class as well, because not
# every one of the other tests in the module will be expecting a
# successful login, and the act may need to be handled a little
# differently for another test case
# For example, if we wanted to write another test scenario around
# submitting bad credentials, we could handle it by adding something
# like this to the test file:
#
# class TestLandingPageBadCredentials:
#     @pytest.fixture(scope="class")
#     def faux_user(self, user):
#         _user = deepcopy(user)
#         _user.password = "badpass"
#         return _user
#
#     def test_raises_bad_credentials_exception(self,
#                                               login_page,
#                                               faux_user):
#         with pytest.raises(BadCredentialsException):
#             login_page.login(faux_user)
#


#
# Inspecting the requesting test context
#   request object
#   https://pytest.org/en/7.4.x/reference/reference.html#pytest.FixtureRequest
# Fixture functions can accept the request object to introspect the
# “requesting” test function, class or module context
#  Further extending the previous smtp_connection fixture example with
#  one connection per test module, let’s read an optional server URL
#  from the test module which uses our fixture:
#
@pytest.fixture(scope="module")
def smtp_connection(request):
    server = getattr(request.module, "SMTP_SERVER", "smtp.gmail.com")
    smtp_connection = smtplib.SMTP(server, 587, timeout=5)
    yield smtp_connection
    smtp_connection.close()

#
# Factories as fixtures
# The “factory as fixture” pattern can help in situations where the
# result of a fixture is needed multiple times in a single test
# (remember that fixtures are evaluated once per test).
#
@pytest.fixture
def make_customer_record():
    def _make_customer_record(name):
        return {"name": name, "orders": []}

    return _make_customer_record


def test_customer_records(make_customer_record):
    customer_1 = make_customer_record("Lisa")
    customer_2 = make_customer_record("Mike")
    customer_3 = make_customer_record("Meredith")

# If the data created by the factory requires managing, the fixture
# can take care of that:
@pytest.fixture
def make_customer_record():
    created_records = []

    def _make_customer_record(name):
        record = dict(name=name, orders=[])
        created_records.append(record)
        return record

    yield _make_customer_record

    for record in created_records:
        pass
        #record.destroy()


# Parameterising fixtures
# https://pytest.org/en/7.4.x/how-to/fixtures.html#parametrizing-fixtures
# Fixture functions can be parametrized in which case they will be
# called multiple times, each time executing the set of dependent tests,
# i.e. the tests that depend on this fixture.
# The fixture function gets access to each parameter through the special
# request object:
@pytest.fixture(scope="module",
                params=["smtp.gmail.com", "mail.python.org"])
def smtp_connection(request):
    smtp_connection = smtplib.SMTP(request.param, 587, timeout=5)
    yield smtp_connection
    smtp_connection.close()

# If we have a parametrised fixture, then all the tests using it will
# first execute with one instance and then finalisers are called before
# the next fixture instance is created
# https://pytest.org/en/7.4.x/how-to/fixtures.html#automatic-grouping-of-tests-by-fixture-instances
# for mod_fixture: for class_fixture: for test_fixture: test

#
# Applying fixtures with `usefixtures`
#
# Sometimes test functions do not directly need access to a fixture
# object (its value). For example, tests may require to operate within
# an empty directory (cwd) but otherwise do not care for the concrete
# directory.
import tempfile, os


@pytest.fixture
def clean_dir():
    with tempfile.TemporaryDirectory() as new_path:
        old_dir = os.getcwd()
        os.chdir(new_path)
        yield
        os.chdir(old_dir)


# Apply the fixture to each test in a test case
# Due to the usefixtures marker, the clean_dir fixture will be required
# for the execution of each test method, just as if we specified a
# “clean_dir” function argument to each of them
# @pytest.mark.usefixtures("clean_dir", "another_fixture", ...)
@pytest.mark.usefixtures("clean_dir")
class TestDirectoryInit:
    def test_cwd_starts_empty(self):
        assert os.listdir(os.getcwd()) == []
        with open("myfile", "w", encoding="utf-8") as f:
            f.write("hello")

    def test_cwd_again_starts_empty(self):
        assert os.listdir(os.getcwd()) == []

# Apply a fixture to every test in the module
# pytestmark = pytest.mark.usefixtures("cleandir")


#
# Defining and overriding fixtures
#
# In relatively large test suite, we most likely need to override a
# global (or root) fixture with a locally defined one, keeping the test
# code readable and maintainable
# https://pytest.org/en/7.4.x/how-to/fixtures.html#overriding-fixtures-on-various-levels
#
# Fixtures can be defined in conftest.py files, e.g. tests/conftest.py
# or tests/subtests/conftest.py, and used in various modules. pytest
# then uses the following precedence (at lookup time):
#  1) module level defined fixtures
#  2) subfolder defined fixtures in conftest.py
#  3) superfolder defined fixtures in conftest.py
#  ...
#
