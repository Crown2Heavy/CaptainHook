import os

class Config:
    # --- STUB PLACEHOLDERS ---
    # These strings MUST be exactly these lengths for the binary patcher to work reliably.
    # They are replaced with null-terminated strings during the build process.
    DISCORD_TOKEN = "TOKEN_PLACEHOLDER_64_BYTES____________________________________"
    GUILD_ID = "GUILD_ID_PLACEHOLDER_32_BYTES_______"
    
    COMMAND_PREFIX = "$"
    DEVELOPER_MODE = False

    # Default paths
    OWN_DIR_NAME = ".CaptainHook"
    LOGS_DIR_NAME = "logs"
    VERSION = "0.1.0"
