import discord
from responses import get_response
from printing_utils import print_message


def setup_discord_bot_events(client: discord.Client) -> None:
    def process_message(message_string: str) -> tuple[int, str] | tuple[None, None]:
        message_string_len = len(message_string)

        if message_string_len >= 2:

            if message_string[0] == '!':
                return 1, message_string[1:].lower()

            if message_string_len >= 3 and message_string[:2] == r'?!':
                return 2, message_string[2:].lower()

        return None, None

    client_user = client.user

    @client.event
    async def on_ready() -> None:
        nonlocal client_user
        client_user = client.user

        print_message(1, message=f"{client_user} is now running!")
        print("\nLog:\n")

    @client.event
    async def on_message(message: discord.Message) -> None:
        if message.author == client_user:
            return

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f"{username} said in {channel}: \"{user_message}\"")

        response_mode, command = process_message(user_message)

        if not response_mode or not command:
            return

        response: str | None = get_response(message, command)

        if not response:
            return

        if isinstance(response, str):

            print(f"\nResponding with:\n{' '.join(response.splitlines())}\n")

            if response_mode == 1:
                await message.channel.send(response)
            elif response_mode == 2:
                await message.author.send(response)
