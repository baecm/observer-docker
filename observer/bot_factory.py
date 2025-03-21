from typing import List, Iterable

from observer.bot_storage import BotStorage
from observer.player import BotPlayer, PlayerRace



def retrieve_bots(
    bot_specs: Iterable[str],
    bot_storages: Iterable[BotStorage]
) -> List[BotPlayer]:
    bots = []
    for bot_spec in bot_specs:
        parts = bot_spec.split(":")
        bot_name = parts[0]

        bot = None
        for bot_storage in bot_storages:
            maybe_bot = bot_storage.find_bot(bot_name)
            if maybe_bot:
                bot = maybe_bot
                break

        if bot is None:
            raise Exception(f"Could not find bot {bot_name}")

        if len(parts) == 2:
            bot.race = PlayerRace(parts[1])

        bots.append(bot)

    return bots
