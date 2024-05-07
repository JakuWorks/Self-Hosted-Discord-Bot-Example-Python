from sys import exit as sys_exit
from time import sleep
from printing_utils import ask_input, print_wrong_answer, print_message, get_m_body, ask_bool_input, answers_positive, answers_negative, get_m_boundary
from token_functions import try_get_saved_token, save_token
from config_reads import config_reads
from typing import Union
import subprocess


def setup_token() -> str:
    def user_questionnaire() -> str:

        a1_first_bad: bool = True
        a2_first_bad1: bool = True
        a2_first_bad2: bool = True

        while True:

            m1_1: str = f"No token was found in {config_reads.PathConfig}."
            m1_2: str = f"The token You pass below will be saved to {config_reads.PathConfig}"
            m1_3: str = "Please enter the token of Your Discord bot below."
            answer1 = ask_input(get_m_body(m1_1, m1_2, m1_3))

            if len(answer1) >= 1:
                while True:
                    m2_1: str = f"Your bot will run with the token: {answer1}"
                    m2_2: str = f"Is the above token Correct? Answer below. ({answers_positive[0]}/{answers_negative[0]})"
                    a2_details: tuple[Union[bool, None], str] = ask_bool_input(m2_1, m2_2)
                    a2_is_positive: bool | None = a2_details[0]
                    a2: str = a2_details[1]

                    if a2_is_positive:
                        m3_1: str = "Saving the token and continuing the script..."
                        print_message(1, message=m3_1)
                        return answer1

                    if not a2_is_positive:
                        if a2_first_bad1:
                            m4_wait_seconds: int = 3
                            a2_first_bad1 = False
                            print_message(1, message=f"Repeating the question in {m4_wait_seconds} seconds...")
                            sleep(m4_wait_seconds)
                        else:
                            print_message(1, message="Repeating the question...")
                        break

                    print_wrong_answer(a2, comment="Your answer was not 'Y', nor 'N'", do_wait=a2_first_bad2)
                    a2_first_bad2 = False
            else:
                a1_too_short_comment = "Your token has to be at least 1 character long!"
                print_wrong_answer(answer1, comment=a1_too_short_comment,
                                do_wait=a1_first_bad)
                a1_first_bad = False

    token_file_first_read: str | None = try_get_saved_token()

    if not token_file_first_read:
        token: str = user_questionnaire()
        save_token(token)
        return token

    return token_file_first_read


def handle_bot_login_failure() -> None:
    m_1: str = "Improper token has been passed!"

    if config_reads.ClearTokenIfBad:
        m_2: str = "Cleared the current Discord Bot Token and restarting the script " \
                   "to avoid further errors."

        print_message(1, message=get_m_body(m_1, m_2), new_boundary_character='=',
                      new_lines_before_first_boundary=3)
        subprocess.call(args=[r"python", config_reads.PathResetToken])
    else:
        print_message(1, message=m_1)


def handle_bot_bad_intents(error_message: str, override_retry_exit_code: int) -> None:
    m1_1: str = "Your token is correct, but You haven't enabled the correct " \
                "Intents in the configuration of Your bot. You have to enable them " \
                "before running the bot again."
    m1_2: str = "\nThe Intents that have to be enabled:"
    m1_3: str = " - SERVER MEMBERS INTENT"
    m1_4: str = " - MESSAGE CONTENT INTENT"
    m1_5: str = "\nDiscord's error message:"
    m1_6: str = f"    {error_message}"

    m_body_for_boundary: str = get_m_body(m1_1, m1_2, m1_3, m1_4, m1_5)
    m_boundary: str = get_m_boundary(m_body_for_boundary, '=')

    print_message(1, m_boundary, get_m_body(m_body_for_boundary, m1_6),
                  new_lines_before_first_boundary=3)

    print(f"\nExit Code:\n{override_retry_exit_code} - OverrideRetry")

    sys_exit(override_retry_exit_code)
