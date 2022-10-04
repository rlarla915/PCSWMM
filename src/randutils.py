# -*- coding: utf-8 -*-
import random


def choices(sequence, weights=None):
    if weights is None:
        return sequence[random.randrange(len(sequence))]
    return sequence[_choices_index(weights)]


def randpop(sequence, weights=None):
    if weights is None:
        return sequence.pop(random.randrange(len(sequence)))
    return sequence.pop(_choices_index(weights))


def _choices_index(weights):
    weights = [0. if weight < 0 else float(weight) for weight in weights]

    if sum(weights) <= 0:
        return random.randrange(len(weights))

    normalized_weights = [weight / sum(weights) for weight in weights]
    accumulated_weights = [sum(normalized_weights[:i + 1]) for i in range(len(weights))]
    offset = random.random()
    for i, weight in enumerate(accumulated_weights):
        if offset <= weight:
            return i
    raise RuntimeError("unreachable code!")


def main():
    seq = [1, 2, 3, 4]
    print(seq)
    print(choices(seq))
    print(seq)
    print(randpop(seq))
    print(seq)
    print(choices(seq, [0, 1, 0]))
    print(seq)
    print(randpop(seq, [0, 1, 0]))
    print(seq)


if __name__ == "__main__":
    main()