
def verify_is_odd(x):
    if not is_odd(x):
        raise ValueError(f"{x} is not odd!")


def is_odd(x):
    return not is_even(x)


def is_even(x):
    return divides(2, x)


def divides(a, b):
    return b % a == 0


def factorial(n):
    result = 1

    while n > 0:
        result *= n
        n -= 1

    return result


def sum_from_one_to(n):
    return sum(range(1, n + 1))


def is_balanced(n):
    lhs, rhs = _split_at_middle(str(n))

    return _sum_of_digits(lhs) == _sum_of_digits(rhs)


def _split_at_middle(s):
    mid = len(s) // 2
    rhs_start = mid + int(is_odd(len(s)))

    return s[:mid], s[rhs_start:]


def _sum_of_digits(str_num):
    return sum(int(d) for d in str_num)


def is_palindrome(n):
    lhs, rhs = _split_at_middle(str(n))

    return lhs == rhs
