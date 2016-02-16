__author__ = 'Alexander'

import random
import gc
import time


class Singleton:
    def __init__(self, decorated):
        self._decorated = decorated

    def Instance(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)


@Singleton
class SetupKeeper:
    def __init__(self):
        self.setup_method = None

    def set_setup_method(self, setup_method, params):
        self.setup_method = setup_method
        self.params = params

    def do_setup(self):
        self.setup_method(self.params)
        gc.disable()
        gc.collect()


class WorkCycleBenchmark:
    def __init__(self, warmup_iterations, count_iterations, class_name):
        self.warmup_iterations = warmup_iterations
        self.count_iteration = count_iterations
        self.class_name = class_name
        self.start_time = None
        self.finish_time = None

    def setup(self):
        SetupKeeper.Instance().do_setup()

    def warm_up(self, function, params):
        for count in range(0, self.warmup_iterations):
            self.setup()
            self.exec_work_cycle(function, params)

    def run_work_cycle(self, function, params):
        self.print_head()
        for count in range(0, self.count_iteration):
            self.setup()
            self.start_time = float("%.9f" % time.time())
            self.exec_work_cycle(function, params)
            self.finish_time = float("%.9f" % time.time())
            self.print_result()

    def print_head(self):
        print "================================================================="
        print "Results for {0}".format(self.class_name)
        print "warmup_iterations {0} count_iterations {0}".format(self.warmup_iterations, self.count_iteration)
        print "-----------------------------------------------------------------"

    def print_result(self):
        print "results: "

    def exec_work_cycle(self, function, params):
        function(params)

    def lets_do_it(self, function, params):
        self.warm_up(function, params)
        self.run_work_cycle(function, params)


class FixedWorkIteration(WorkCycleBenchmark):
    def __init__(self, cycle_iteration, warmup_iterations, count_iterations, class_name):
        WorkCycleBenchmark.__init__(self, warmup_iterations, count_iterations, class_name)
        self.cycle_iteration = cycle_iteration

    def print_result(self):
        print "FixedWorkIteration results for {0} iterations".format(self.cycle_iteration)
        print "measurementTime(sec): ", self.finish_time - self.start_time

    def exec_work_cycle(self, function, params):
        for i in range(0, self.cycle_iteration):
            function(params)


class FixedTimeIteration(WorkCycleBenchmark):
    def __init__(self, cycle_time_in_sec, warmup_iterations, count_iterations, class_name):
        WorkCycleBenchmark.__init__(self, warmup_iterations, count_iterations, class_name)
        self.cycle_time_in_sec = cycle_time_in_sec

    def print_result(self):
        print "FixedTimeIteration results "

    def exec_work_cycle(self, function, params):
        #TODO need implementation for fixed Time
        function(params)


class GenerateBenchmark(object):
    def __init__(self, work_cycle):
        print "inside GenerateBenchmark.__init__()"
        self.workCycle = work_cycle

    def __call__(self, function):
        print "inside GenerateBenchmark.__call__()"
        self.workCycle.lets_do_it(function)


def Setup():
    def decorator(func):
        def func_wrapper(self):
            return SetupKeeper.Instance().set_setup_method(func, self)

        return func_wrapper

    return decorator


def FixedWorkBenchmark(cycle_iteration=100, warmup_iterations=5, count_iterations=5, class_name="ClassNameTest"):
    def decorator(func):
        def func_wrapper(self):
            bm = FixedWorkIteration(cycle_iteration, warmup_iterations, count_iterations, class_name)
            return bm.lets_do_it(func, self)

        return func_wrapper

    return decorator


def FixedTimeBenchmark(cycle_time_in_sec=10, warmup_iterations=5, count_iterations=5, class_name="ClassNameTest"):
    def decorator(func):
        def func_wrapper(self):
            bm = FixedTimeIteration(cycle_time_in_sec, warmup_iterations, count_iterations, class_name)
            return bm.lets_do_it(func, self)

        return func_wrapper

    return decorator


class TupleIterationBenchmarkTest:
    def __init__(self):
        self.tuple = ()

    @Setup()
    def full_random(self):
        del self.tuple
        self.tuple = ()
        for i in range(0, 10000):
            self.tuple += (random.uniform(1, 1000),)

    @FixedWorkBenchmark(cycle_iteration=10000, class_name="TupleIterationBenchmarkTest")
    def iteration(self):
        for i in self.tuple:
            pass


class TupleAppendBenchmarkTest:
    def __init__(self):
        self.tuple = ()

    @Setup()
    def clear_tuple(self):
        del self.tuple
        self.tuple = ()

    @FixedWorkBenchmark(cycle_iteration=10000, class_name="TupleAppendBenchmarkTest")
    def append_tuple(self):
        self.tuple += ("add some string",)


class SearchInTupleBenchmarkTest:
    def __init__(self):
        self.tuple = ()

    @Setup()
    def full_random(self):
        del self.tuple
        self.tuple = ()
        for i in range(0, 10000):
            self.tuple += (random.randint(1, 1000),)

    @FixedWorkBenchmark(cycle_iteration=100000, class_name="SearchInTupleBenchmarkTest")
    def search(self):
        return random.randint(1, 1000) in self.tuple


class TupleGetElementBenchmarkTest:
    def __init__(self):
        self.tuple = ()

    @Setup()
    def full_random(self):
        del self.tuple
        self.tuple = ()
        for i in range(0, 10000):
            self.tuple += (random.randint(1, 1000),)

    @FixedWorkBenchmark(cycle_iteration=1000000, class_name="TupleGetElementBenchmarkTest")
    def get_element(self):
        return self.tuple[random.randint(0, 9999)]


class CreateTuple10ElemBenchmarkTest:
    def __init__(self):
        self.tuple = ()

    @Setup()
    def clear(self):
        del self.tuple
        self.tuple = ()

    @FixedWorkBenchmark(cycle_iteration=10000000, class_name="CreateTuple10ElemBenchmarkTest")
    def create_tuple(self):
        self.tuple = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)


class TupleUnion2x10ElemBenchmarkTest:
    def __init__(self):
        self.tuple1 = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
        self.tuple2 = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

    @Setup()
    def do_nothing(self):
        pass

    @FixedWorkBenchmark(cycle_iteration=10000000, class_name="TupleUnion2x10ElemBenchmarkTest")
    def union(self):
        return self.tuple1 + self.tuple2


class ListIterationBenchmarkTest:
    def __init__(self):
        self.list = []

    @Setup()
    def full_random(self):
        del self.list[:]
        for i in range(0, 10000):
            self.list.append(random.uniform(1, 1000))

    @FixedWorkBenchmark(cycle_iteration=10000, class_name="ListIterationBenchmarkTest")
    def iteration(self):
        for i in self.list:
            pass


class ListAppendBenchmarkTest:
    def __init__(self):
        self.list = []

    @Setup()
    def clear_list(self):
        del self.list[:]

    @FixedWorkBenchmark(cycle_iteration=10000, class_name="ListAppendBenchmarkTest")
    def append_list(self):
        self.list.append("add some string")


class SearchInListBenchmarkTest:
    def __init__(self):
        self.list = []

    @Setup()
    def full_random(self):
        del self.list[:]
        for i in range(0, 10000):
            self.list.append(random.randint(1, 1000))

    @FixedWorkBenchmark(cycle_iteration=100000, class_name="SearchInListBenchmarkTest")
    def search(self):
        return random.randint(1, 1000) in self.list


class ListGetElementBenchmarkTest:
    def __init__(self):
        self.list = []

    @Setup()
    def full_random(self):
        del self.list[:]
        for i in range(0, 10000):
            self.list.append(random.randint(1, 1000))

    @FixedWorkBenchmark(cycle_iteration=1000000, class_name="ListGetElementBenchmarkTest")
    def get_element(self):
        return self.list[random.randint(0, 9999)]


class CreateList10ElemBenchmarkTest:
    def __init__(self):
        self.list = []

    @Setup()
    def clear(self):
        del self.list[:]

    @FixedWorkBenchmark(cycle_iteration=10000000, class_name="CreateList10ElemBenchmarkTest")
    def create_list(self):
        self.list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


class ListUnion2x10ElemBenchmarkTest:
    def __init__(self):
        self.list1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.list2 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    @Setup()
    def do_nothing(self):
        pass

    @FixedWorkBenchmark(cycle_iteration=10000000, class_name="ListUnion2x10ElemBenchmarkTest")
    def union(self):
        return self.list1 + self.list2


if __name__ == '__main__':
    print "start"
    tuple_test = TupleIterationBenchmarkTest()
    tuple_test.full_random()
    tuple_test.iteration()

    list_test = ListIterationBenchmarkTest()
    list_test.full_random()
    list_test.iteration()