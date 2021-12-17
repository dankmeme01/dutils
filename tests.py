from dutils import internet, math, util
from dutils.obsolete import brawl
import sys

def assert_fail():
    assert 3 == 4

class TestClass:
    # Group 1 : pyutils
    def TestAllEqual():
        elems1 = (3, 1, 2)
        elems2 = (3, 3, 3)
        assert util.all_equal(elems2)
        assert not util.all_equal(elems1)
    # Group 2 : event
    def TestOverload():
        assert_fail()
    # Group 3 : brawl
    # Group 4 : gamelib
    def Test3():
        pass

def run_tests():
    failed = 0
    passed = 0
    count = 1
    for i in dir(TestClass):
        name = i.partition("Test")[2]
        if not name: continue
        try:
            getattr(TestClass, i)()
            message = f"\u001b[32mTest №{count} passed ({name})"
            passed += 1
        except AssertionError as e:
            message = f"\u001b[31mTest №{count} failed ({name}): Assert failed at line {e.__traceback__.tb_next.tb_lineno}"
            failed += 1
        except Exception as e:
            message = f"\u001b[31mTest №{count} failed ({name}): Exception occured at line {e.__traceback__.tb_next.tb_lineno}: {e.__class__.__name__}: {str(e)}"
            failed += 1
        finally:
            print(message + "\u001b[0m")
            count += 1

    perc = (passed/count) * 100
    print(f"{passed}/{count - 1} tests passed ({passed / (count - 1) * 100:.0f}%)")

if __name__ == '__main__':
    run_tests()