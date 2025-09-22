from typing import Optional, Dict
import json
import logging
import os
import os.path
import shutil

import numpy as np
import requests

from observer.player import BotPlayer, BotJsonMeta


logger = logging.getLogger(__name__)

class BotStorage:
    def find_bot(self, name: str) -> Optional[BotPlayer]:
        raise NotImplemented


class LocalBotStorage(BotStorage):
    def __init__(self, bot_dir: str) -> None:
        self.bot_dir = bot_dir

    def find_bot(self, name: str) -> Optional[BotPlayer]:
        f_name = f"{self.bot_dir}/{name}"
        logger.debug(f"checking bot in {f_name}")
        if not os.path.exists(f_name):
            return None

        logger.debug(f"found bot in {f_name}")
        bot = BotPlayer(f_name)

        return bot
