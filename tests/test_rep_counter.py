from rep_counter import RepCounter


def test_rep_counter_counts_single_rep():
    counter = RepCounter()
    sequence = [
        0.10, 0.11, 0.11, 0.10, 0.10,
        0.12, 0.15, 0.18, 0.22, 0.25, 0.28, 0.30,
        0.28, 0.24, 0.18, 0.13, 0.10, 0.10,
    ]
    for value in sequence:
        counter.add_sample(value)

    assert counter.rep_count == 1


def test_rep_counter_ignores_noise():
    counter = RepCounter()
    sequence = [
        0.10, 0.11, 0.10, 0.12, 0.11, 0.10, 0.11, 0.10,
        0.10, 0.11, 0.10, 0.09, 0.10,
    ]
    for value in sequence:
        counter.add_sample(value)

    assert counter.rep_count == 0
