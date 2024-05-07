from base64 import b64encode, b64decode
from re import findall
from math import ceil


def b64encode_utf8(my_bytes: bytes) -> str:
    return b64encode(my_bytes).decode("utf-8")


def my_b64utf8_decode(my_string: str) -> bytes:
    return b64decode(my_string)


def find_ints_in_string(to_match: str) -> list:
    pattern = r"\d+"

    return [int(match) for match in findall(pattern, to_match)]


def remove_non_letters_in_string(my_string: str) -> str:
    return "".join(findall(r"[\w\s]+", my_string))


def predictable_shuffle_string(my_str: str) -> str:
    my_str_reversed: str = my_str[::-1]

    def recursive_unsort(my_slice: str) -> str:
        my_slice_len: int = len(my_slice)

        if my_slice_len <= 2:
            return my_slice

        new_slice: str = ""

        for i in range(ceil(my_slice_len / 2)):
            new_slice += my_slice[i : i + 1] + my_slice[-i - 1]

        new_slice_len: int = len(new_slice)

        if len(new_slice) > my_slice_len:
            new_slice: str = new_slice[:-1]
            new_slice_len: int = len(new_slice)

        new_slice_half_pos: int = ceil(new_slice_len / 2)

        half1 = recursive_unsort(new_slice[:new_slice_half_pos])
        half2 = recursive_unsort(new_slice[new_slice_half_pos:])

        return half1 + half2

    my_str_unsorted: str = my_str_reversed

    for _ in range(len(my_str_reversed)):
        my_str_unsorted = recursive_unsort(my_str_reversed)

    return recursive_unsort(my_str_unsorted)


def get_list_element_at_index(lst, index: int, default = None):
    if index < 0:
        return default
    if index >= len(lst):
        return default

    return lst[index]
