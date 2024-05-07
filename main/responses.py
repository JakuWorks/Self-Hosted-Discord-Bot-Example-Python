from math import floor
from operator import itemgetter
from random import randint
import discord
from typing import Callable
from helper_functions import remove_non_letters_in_string, find_ints_in_string, get_list_element_at_index


def get_response(message: discord.Message, user_command: str) -> str | None:
    # I am reading this in 2024 and decided to leave this note.
    # Nested functions are an incredibly bad practice. Never do it.
    # Unfortunately that's how I coded it back then so I will leave it like this

    commands = {}

    def set_command(my_function: Callable) -> None:
        commands_prefix: str = "cmd_"
        commands_prefix_length: int = len(commands_prefix)
        commands[my_function.__name__[commands_prefix_length:]] = my_function

    @set_command
    def cmd_help() -> str:
        return "TODO"

    @set_command
    def cmd_hello() -> str:
        return "Hey there!"

    @set_command
    def cmd_roll() -> str:
        # Supports multiple rolls in one command if the pattern is: min max min max

        numbers: list = find_ints_in_string(user_command)
        numbers_len: int = len(numbers)

        default_first: int = 1
        default_second: int = 20

        def get_roll_results_message(minimum: int, maximum: int) -> str:
            return f"A random number from {minimum} to {maximum} is {randint(minimum, maximum)}"

        responses: list = []

        for n in range(floor(numbers_len / 2 + 0.5)):
            i: int = n * 2

            minimum: int = numbers[i] or default_first
            maximum: int = get_list_element_at_index(lst=numbers, index=i+1) or default_second

            response: str = get_roll_results_message(minimum=minimum, maximum=maximum)
            responses.append(response)

        response_full: str = '\n'.join(responses)

        return response_full

    @set_command
    def cmd_account_ages_leaderboard() -> str:
        all_members: list = [[member.id, member.created_at.timestamp()] for member in message.guild.members]

        all_members.sort(key=itemgetter(1))

        lines: list = []

        for i, member in enumerate(all_members):
            timestamp: int = floor(member[1] + 0.5)
            lines.append(f"{i}. Member: <@{member[-1]}>, "
                         f"Relative Time: <t:{timestamp}:R>, "
                         f"Long Date: <t:{timestamp}:F>, "
                         f"Raw Timestamp: {timestamp}")

        head: str = "A list of all members sorted by their account creation timestamp:"

        return '\n'.join([head, *lines])

    for command_name, action in commands:
        command_name_len: int = len(command_name)
        user_command_slice: str = user_command[:command_name_len]

        if command_name == user_command_slice or command_name == remove_non_letters_in_string(user_command_slice):
            return action()
