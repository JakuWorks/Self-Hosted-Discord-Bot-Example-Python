from os import path, getcwd, chdir
import discord
import discord.errors
from setup_module import setup_token, handle_bot_login_failure, handle_bot_bad_intents
from printing_utils import print_message
from bot import setup_discord_bot_events


def main() -> None:
    # Make sure the working directory is correct
    # This is for emergency situations when this file has been launched directly.

    override_retry_exit_code: int = 1001

    if path.basename(getcwd()) == 'Assets':
        chdir(r'.\..')

    token: str = setup_token()

    print_message(1, message=f"TOKEN: '{token}' will be used...",
                  new_boundary_character="=")

    my_intents = discord.Intents.default()
    my_intents.message_content = True
    my_intents.members = True

    client: discord.Client = discord.Client(intents=my_intents)

    setup_discord_bot_events(client)

    try:
        client.run(token)
    except discord.errors.LoginFailure:
        handle_bot_login_failure()
    except discord.errors.PrivilegedIntentsRequired as bad_intents_error:
        handle_bot_bad_intents(str(bad_intents_error), override_retry_exit_code)


if __name__ == "__main__":
    main()
