import os

class Config:
    # These will be injected by the builder
    DISCORD_TOKEN = "[[DISCORD_TOKEN_PLACEHOLDER]]"
    GUILD_ID = "[[GUILD_ID_PLACEHOLDER]]"
    COMMAND_PREFIX = "$"

    # Default paths
    OWN_DIR_NAME = ".CaptainHook"
    LOGS_DIR_NAME = "logs"
    VERSION = "3.0.0"
