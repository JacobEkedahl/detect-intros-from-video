import sys

def silly_foo():
    print("more printing...")

if __name__ == "__main__":
    st = sys.argv[1]
    silly_foo()
    print("from python: %s" % st)
    