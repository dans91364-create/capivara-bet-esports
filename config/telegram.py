"""Telegram configuration and utilities."""
from typing import Optional
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


class TelegramConfig:
    """Telegram configuration class."""

    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID

    def is_enabled(self) -> bool:
        """Check if Telegram is properly configured."""
        return bool(self.bot_token and self.chat_id)

    @property
    def notification_settings(self) -> dict:
        """Get notification settings."""
        return {
            "opportunities": True,
            "results": True,
            "daily_report": True,
            "alerts": True,
        }


# Global instance
telegram_config = TelegramConfig()
