from statistics import stdev

numbers_2d = [[1,2,3,4,5], [2,3,4,5,6], [3,4,5,6,7]]
workflow = dict()
exported_instances = dict()

def wf(graph, *args, **kwargs):
    def inner(func, *args, **kwargs):
        graph[func.__name__] = func
        return func
    return inner


def snippet(func):
    def inner(*args, **kwargs):
        result = func()
        global exported_instances
        exported_instances[func.__name__] = result
        return result
    return inner


@wf(graph=workflow)
def averages(numbers_2d):
    return [sum(numbers)/len(numbers) for numbers in numbers_2d]

@snippet
@wf(graph=workflow)
def standard_deviation(averages):
    return stdev(averages)

