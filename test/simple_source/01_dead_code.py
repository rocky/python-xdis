def dead_code(a):
    if a:
        return 5
    else:
        return 6
    # Python 2.7 and before adds a "return None" here
    # which can't be reached
