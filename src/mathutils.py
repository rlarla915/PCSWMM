# -*- coding: utf-8 -*-


def lerp(start, end, size):
    """## Linear Interpolation"""
    gap = float(end - start) / (size - 1)
    for i in range(size - 1):
        yield start + i * gap
    yield end


def main():
    print([x for x in lerp(0, 10, 5)])
    print([x for x in lerp(10, 0, 5)])


if __name__ == "__main__":
    main()
