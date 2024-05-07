from time import sleep


answers_positive: list = ["Y", "Yes", "Yea"]
answers_negative: list = ["N", "No", "Nah"]

answers_positive_lower: list = [*map(str.lower, answers_positive)]
answers_negative_lower: list = [*map(str.lower, answers_negative)]


def get_m_boundary(message_body: str, character: str = '=') -> str:
    longest_line_length: int = len(max(message_body.splitlines(), key=len))
    boundary_body: str = character * longest_line_length
    return boundary_body


def get_m_body(*lines: str) -> str:
    return '\n'.join(lines)


def print_message(mode: int = 1, boundary_body: str = '', message: str = '',
                  new_boundary_character: str = '-',
                  new_lines_before_first_boundary: int = 1) -> None:
    if not boundary_body:

        if message:
            boundary_body = get_m_boundary(message, new_boundary_character)
        else:
            print()
            return

    new_lines: str = '\n' * new_lines_before_first_boundary
    first_boundary: str = f'{new_lines}{boundary_body}>'
    second_boundary: str = f'<{boundary_body}'

    if mode == 1:

        if message:
            print(f"{first_boundary}\n{message}\n{second_boundary}")
        else:
            print(f"{first_boundary}\n{second_boundary}")

    elif mode == 2:

        if message:
            print(f"{first_boundary}\n{message}")
        else:
            print(f"{first_boundary}")

    elif mode == 3:

        if message:
            print(f"{message}\n{second_boundary}")
        else:
            print(f"{second_boundary}")


def print_wrong_answer(bad_answer: str, comment: str = "None", do_wait: bool = False,
                       wait_seconds: float = 3) -> None:
    message1: str = "Your answer was rejected!"
    message2: str = f"Comment: {comment}"

    if bad_answer:
        message3: str = f"Your answer was: {bad_answer}"
    else:
        message3: str = "Your answer was: You didn't write anything!"

    def shared_print_message() -> None:
        print_message(1, message=get_m_body(message1, message2, message3, message4))

    if do_wait:
        message4: str = f"The question will be repeated in {wait_seconds} seconds..."
        shared_print_message()
        sleep(wait_seconds)
    else:
        message4: str = "The question will be repeated..."
        shared_print_message()


def ask_input(question: str) -> str:
    m_boundary: str = get_m_boundary(question)

    print_message(2, m_boundary, question)
    answer: str = input("\n ")
    print_message(3, m_boundary)

    return answer


def ask_bool_input(*question_lines: str) -> tuple[bool | None, str]:
    answer = ask_input(get_m_body(*question_lines))
    a_lower = answer.lower()

    boolean = True if a_lower in answers_positive_lower \
        else False if a_lower in answers_negative_lower else None
    return (boolean, answer)
