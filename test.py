class _wrapper:
    def __init__(self, func):
        print("1")
        func()

    def __call__(self):
        print("2")

@_wrapper
def aFunction():
    return 1


aFunction()