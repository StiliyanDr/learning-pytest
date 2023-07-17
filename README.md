# learning-pytest
Examples of unit tests using pytest and mocking.


```bash
# all tests
$ python -m pytest tests/

# tests matching keyword
$ python -m pytest -k filenamekeyword

# single test file
$ python -m pytest tests/utils/test_sample.py

# single test method
$ python -m pytest tests/utils/test_sample.py::test_answer_correct 

# single test method in class (test case)
$ python -m pytest tests/utils/test_mod.py::TestClass::test_method

# log output to file
$ python -m pytest --resultlog=testlog.log tests/ 

# print output to console
$ python -m pytest -s tests/

# succinct output
$ python -m pytest -q tests/

# show extra info on xfailed, xpassed, and skipped tests
$ python -m pytest -rxXs tests/  
```
