from dutils.obsolete import brawl
from dutils import util
from dataclasses import dataclass
from event import eventmanager
from threading import Thread
import inspect, time

brawl.pre_init()
brawl.init()

def assert_fail():
    assert 3 == 4

@dataclass
class TestInfo:
    number: int
    name: str
    success: bool
    message: str
    timetook: float
class TestClass:
    # Group 1 : pyutils
    def TestAllEqual():
        elems1 = (3, 1, 2)
        elems2 = (3, 3, 3)
        assert util.all_equal(elems2)
        assert not util.all_equal(elems1)
    # Group 2 : event
    def TestEvent():
        evt = eventmanager()
        _gt = 0
        @evt.event
        def test(_1):
            nonlocal _gt
            _gt = 1
        evt.emit("test")
        assert _gt == 1, "_gt did not change"
    # Group 3 : brawl
    def TestBrawlName():
        brawl.change_lang('en')
        f = brawl.brawlers[0]
        assert f.name == 'Shelly', 'Shelly name is ' + f.name
    def TestBrawlLangChange():
        brawl.change_lang('ru')
        f = brawl.brawlers[0]
        assert f.name == 'Шелли', 'Shelly name is ' + f.name + ", not Шелли"
    def TestBrawlRarities():
        brawl.change_lang('en')
        chromas = brawl.search_brawlers(brawl.BrawlerQuery.RARITY, brawl.brawlers, brawl.Rarity.CHROMA)
        assert brawl.__init_data__["season"]  == len(chromas)
        assert chromas[0].name == "Gale", "First chroma is not Gale, but " + chromas[0].name
        assert chromas[-1].rarity == brawl.Rarity.CHROMA_LEGENDARY, "Last chroma is not legendary, but " + chromas[-1].rarity
        assert chromas[-2].rarity == brawl.Rarity.CHROMA_MYTHIC, "Prelast chroma is not mythic, but " + chromas[-2].rarity


testinfo = []

def run_test(func, number):
    global testinfo
    if not inspect.isfunction(func): return
    name = func.__name__.partition("Test")[2]
    if not name: return None
    passed = None
    message = None
    begin = time.time()

    try:
        func()
        message = f"\u001b[32mTest №{number} passed in %ss ({name})"
        passed = True
    except AssertionError as e:
        message = f"\u001b[31mTest №{number} failed in %ss ({name}): Assert failed at line {e.__traceback__.tb_next.tb_lineno}{': ' + str(e) if str(e) else ''}"
        passed = False
    except Exception as e:
        message = f"\u001b[31mTest №{number} failed in %ss ({name}): Exception occured at line {e.__traceback__.tb_next.tb_lineno}: {e.__class__.__name__}: {str(e)}"
        passed = False
    testinfo.append(TestInfo(
        number=number,
        name=name,
        success=passed,
        message=message,
        timetook=time.time() - begin
    ))

def run_tests():
    global testinfo
    threads = []
    number = 1
    for i in dir(TestClass):
        if not i.startswith("Test"): continue
        func = getattr(TestClass, i)
        threads.append(Thread(daemon=True, target=run_test, args=(func, number)))
        number += 1

    start = time.time()
    [t.start() for t in threads]
    [t.join() for t in threads]
    took_time = time.time() - start
    took_time2 = 0

    passed = 0
    total = 0
    for t in testinfo:
        passed += (1 if t.success else 0)
        total += 1
        took_time2 += t.timetook
        print((t.message % round(t.timetook, 3)) + "\u001b[0m")

    print(f"{passed}/{total} tests passed ({passed / (total) * 100:.0f}%)")
    print(f"Total time took: {took_time:.3f}s real, {took_time2:.3f}s sum of threads runtime")

if __name__ == '__main__':
    run_tests()