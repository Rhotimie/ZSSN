import itertools

def sort_tuple_list(tuple_list, pos, slice_from=None):
    """
    Return a List of tuples

    Example usage:
      sort_tuple_list([('a', 1), ('b', 3), ('c', 2)])

    :param status: list of tuples
    :type status: List
    :param list:
    :param int:
    :return: sorted list of tuples e.g [('a', 1), ('c', 2) ('b', 3)] usig element at pos 1 to sort
    """

    if tuple_list and type(tuple_list) == list:
        if pos >= len(tuple_list[0]): return None
        slice_from = len(tuple_list) if not slice_from else slice_from
        return sorted(tuple_list, key = lambda i: i[pos], reverse = True)[:slice_from]

    return []


def grouper(n, iterable, is_fill=False, fillvalue=None):
    """
    split a list into n desired groups
    Example
        list(grouper(3, range(9))) = [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
    :return: list of tuples
    """
    args = [iter(iterable)] * n
    if is_fill:
        return list(itertools.zip_longest(*args, fillvalue=fillvalue))
    else:
        return list([e for e in t if e != None] for t in itertools.zip_longest(*args))


def un_grouper(list_of_lists):
    """
    combines a list of lists into a single list
    Example
        grouper([(0, 1, 2), (3, 4, 5), (6, 7, 8)]) = list(range(9))
    :return: list of tuples
    """
    return list(itertools.chain.from_iterable(list_of_lists))
