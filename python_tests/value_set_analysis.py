from typing import Set

from evm_cfg_builder.value_analysis.value_set_analysis import (
    merge_stack,
    Stack,
    AbsStackElem,
)


def test_merge_stack_1() -> None:
    authorized_values = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}
    st1 = Stack(authorized_values)

    st1.push(1)
    st1.push(2)
    st1.push(10)
    st1.push(3)

    st2 = Stack(authorized_values)

    st2.push(1)
    st2.push(3)
    st2.push(5)

    st_merged = merge_stack([st1, st2], authorized_values)

    st_real = Stack(authorized_values)
    st_real.push(1)
    st_real.push(AbsStackElem(authorized_values, {1, 2}))
    st_real.push(AbsStackElem(authorized_values, {3, 10}))
    st_real.push(AbsStackElem(authorized_values, {3, 5}))

    print(st1)
    print(st2)
    print(st_merged)
    print(st_real)
    assert st_real.equals(st_merged)


def test_merge_stack_2() -> None:
    authorized_values = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}
    st1 = Stack(authorized_values)

    st1.push(1)
    st1.push(AbsStackElem(authorized_values, {2, 4}))
    st1.push(10)
    st1.push(3)

    st2 = Stack(authorized_values)

    st2.push(1)
    st2.push(3)
    st2.push(5)

    st_merged = merge_stack([st1, st2], authorized_values)

    st_real = Stack(authorized_values)
    st_real.push(1)
    st_real.push(AbsStackElem(authorized_values, {1, 2, 4}))
    st_real.push(AbsStackElem(authorized_values, {3, 10}))
    st_real.push(AbsStackElem(authorized_values, {3, 5}))

    print(st1)
    print(st2)
    print(st_merged)
    print(st_real)
    assert st_real.equals(st_merged)


def test_merge_stack_no_authorized_value() -> None:
    authorized_values: Set[int] = set()
    st1 = Stack(authorized_values)

    st1.push(1)
    st1.push(2)
    st1.push(3)
    st1.push(4)
    st1.push(5)

    st2 = Stack(authorized_values)

    st2.push(3)
    st2.push(4)
    st2.push(5)

    st_merged = merge_stack([st1, st2], authorized_values)

    st_real = Stack(authorized_values)
    st_real.push(1)
    st_real.push(2)
    st_real.push(3)
    st_real.push(4)
    st_real.push(5)

    print(st1)
    print(st2)
    print(st_merged)
    print(st_real)
    assert st_real.equals(st_merged)


def test_pop_push() -> None:
    authorized_values: Set[int] = set()
    st1 = Stack(authorized_values)
    st1.push(1)
    st1.push(2)
    assert st1.top().equals(AbsStackElem(authorized_values, {2}))


def test_merge_stack_diff_size() -> None:
    authorized_values: Set[int] = set()
    st1 = Stack(authorized_values)
    st2 = Stack(authorized_values)

    st1.push(1)
    st1.push(2)

    st2.push(2)

    st_merged = merge_stack([st1, st2], authorized_values)

    st_real = Stack(authorized_values)
    st_real.push(1)
    st_real.push(2)

    print(st1)
    print(st2)
    print(st_merged)
    print(st_real)
    assert st_real.equals(st_merged)


if __name__ == "__main__":
    test_pop_push()
    test_merge_stack_diff_size()
    test_merge_stack_1()
    test_merge_stack_2()
    test_merge_stack_no_authorized_value()
