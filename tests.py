# coding: utf-8

import time
import inspect
from random import randint
from random import uniform
from rpack import Rect
from rpack import pack
from rpack import coverage
from rpack import get_enclosing_rect

def multiple(func, amount_range):
    amount = randint(amount_range[0], amount_range[1])
    return [func(i) for i in range(amount)]

def randrect(from_size, to_size):
    def _(i):
        w = randint(from_size[0], to_size[0])
        h = randint(from_size[1], to_size[1])
        return Rect(w, h, i)
    return _


class Clock(object):
    def __init__(self):
        self.stop()

    def stop(self):
        self._ticks = time.clock()

    def get_ticks(self):
        t = time.clock()
        delta = t - self._ticks
        self._ticks = t
        return delta


class Group(object):
    def __init__(self, a, b):
        self.cases = []
        self.add(a)
        self.add(b)

    def add(self, group):
        if isinstance(group, Case):
            self.cases.append(group)
        elif isinstance(group, Group):
            self.cases.extend(group.cases)
        else: raise ValueError

    def __lshift__(self, group):
        self.add(group)
        return self


class Case(object):
    def __init__(self, from_size, to_size, amount_range):
        self.from_size = from_size
        self.to_size = to_size
        self.amount_range = amount_range

    def __lshift__(self, group):
        return Group(self, group)

    def __str__(self):
        return "<Case (from_size: %s, to_size: %s, amount: %s)>" %\
                (self.from_size, self.to_size, self.amount_range)

    def __repr__(self):
        return str(self)


class Test(object):
    tests = []
    cmps = []

    def __init__(self, name, description, group=None):
        self.name = name
        self.description = description
        self.cases = []
        if group: self <= group
        self.tests.append(self)

    def __le__(self, group):
        if self.cases:
            raise ValueError
        if isinstance(group, Group):
            self.cases = group.cases
        elif isinstance(group, Case):
            self.cases = [group]
        else:
            raise ValueError
        return self

    def __str__(self):
        result = "<Test (name: '%s', description: '%s')>" %\
                (self.name, self.description)
        delim = "\n" + 4 * " "
        result += delim
        result += delim.join(str(case) for case in self.cases)
        return result+"\n\n"

    #def __repr__(self):
    #    return str(self)

    def build(self):
        self.rects = []
        for case in self.cases:
            f = randrect(case.from_size, case.to_size)
            self.rects.extend(multiple(f, case.amount_range))

    @classmethod
    def register_cmp(cls, name, func):
        cls.cmps.append((name, func))

    @classmethod
    def run_once(cls):
        clk = Clock()
        results = []
        for test in cls.tests:
            test.build()
            for cmp in cls.cmps:
                clk.stop()
                done = pack(test.rects, rect_cmp=cmp[1])
                runtime = clk.get_ticks()
                er = get_enclosing_rect(done)
                cv = coverage(done, er)
                results.append(TestResult(test, cmp, runtime, cv, er))
        return results

    @classmethod
    def run(cls, times):
        results = []
        for i in range(times):
            results.append(cls.run_once())
        return results


class TestResult(object):
    def __init__(self, test, cmp, runtime, coverage, enclosing_rect):
        self.test = test
        self.cmp = cmp
        self.runtime = runtime
        self.coverage = coverage
        self.enclosing_rect = enclosing_rect


def pretty_print(results):
    for row in results:
        for result in row:
            print "<test: %s, cmp: %s, runtime: %s, coverage: %s>" %\
                    (result.test.name, result.cmp[0], result.runtime, result.coverage)
        print "\n"

if __name__ == '__main__':
    #from rpack import rect_cmp1
    #from rpack import rect_cmp2
    #from rpack import rect_cmp3

    def rect_cmp1(rect):
        e = rect.width / float(rect.height)
        if rect.width > rect.height:
            e = rect.height / float(rect.width)
        s = 1.0 / (rect.width * rect.height)
        w = 1.0 / rect.width
        return w * e * s

    def rect_cmp2(rect):
        e = (rect.width + rect.height) / float(rect.width * rect.height)
        return rect.width * -1.0 + e

    def rect_cmp3(rect):
        size = float(rect.width * rect.height)
        e = (2 * rect.width + 2 * rect.height) / size
        s = 1 / size
        return -1.0 * (rect.width - e - s)

    def rect_cmp4(rect):
        size = float(rect.width * rect.height)
        e = (rect.width + rect.height) / size
        s = 1.0 / size
        w = 1.0 / rect.width
        return w * e * s

    def rect_cmp5(rect):
        return 1.0 / rect.width

    def rect_cmp6(rect):
        return (1.0 / rect.width) * (1.0 / rect.height)

    def rect_cmp7(rect):
        return 1.0 / (rect.width * rect.height)

    Test.register_cmp("cmp1", rect_cmp1)
    Test.register_cmp("cmp2", rect_cmp2)
    Test.register_cmp("cmp3", rect_cmp3)
    Test.register_cmp("cmp4", rect_cmp4)
    Test.register_cmp("cmp5", rect_cmp5)
    Test.register_cmp("cmp6", rect_cmp6)

    """
    Test('32x32', 'only similar rectangles with differing amount') <=\
            Case((32, 32), (32, 32), (100, 200))

    Test('base2', 'rectangles with base 2 ( 32, 64 and 128 )')\
            <= Case((32, 32), (32, 32), (50, 100))\
            << Case((64, 64), (64, 64), (50, 100))\
            << Case((128, 128), (128, 128), (50, 100))
    """

    Test('high_or_wide', 'high or wide rectangles')\
            <= Case((100, 10), (300, 100), (50, 100))\
            << Case((10, 100), (100, 300), (50, 100))

    Test('32x32+rand', 'mixed tiles with rects of random sizes')\
            <= Case((10, 10), (300, 300), (50, 100))\
            << Case((32, 32), (32, 32), (200, 300))

    Test('high_xor_big', 'rectangles may be big or high')\
            <= Case((200, 200), (300, 300), (50, 100))\
            << Case((200, 10), (400, 50), (50, 100))

    Test('many_small_big', 'a lot of small and a lot of big')\
            <= Case((10, 10), (500, 500), (500, 1000))

    pretty_print(Test.run(5))
