import sys


def main(argv):
    arg1 = argv[1]
    arg2 = argv[2]
    arg3 = argv[3]

    returned_arg1 = arg1.upper()
    returned_arg2 = arg2.lower()
    returned_arg3 = arg3.capitalize()

    print(returned_arg1)
    print(returned_arg2)
    print(returned_arg3)


if __name__ == "__main__":
    main(sys.argv)
