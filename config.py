"""
Configuration module with default settings for the automation script.

This module defines all configuration dataclasses and provides default values
for browser options, stealth settings, timeouts, selectors, and logging options.
"""

from typing import Literal, Tuple, Dict
from dataclasses import dataclass


@dataclass
class ViewportConfig:
    """Viewport configuration for browser window size."""
    width: int
    height: int


@dataclass
class BrowserConfig:
    """Browser initialization configuration."""
    headless: bool
    user_data_dir: str
    viewport: ViewportConfig


@dataclass
class SelectorsConfig:
    """CSS selectors for page elements."""
    signup_button: str
    email_input: str


@dataclass
class TimeoutsConfig:
    """Timeout values in milliseconds for various operations."""
    page_load: int = 30000        # milliseconds
    element_visible: int = 30000  # milliseconds
    new_tab: int = 10000          # milliseconds


@dataclass
class StealthConfig:
    """Stealth mode configuration to avoid automation detection."""
    enabled: bool
    human_like_typing: bool
    typing_delay_range: Tuple[int, int]  # (min_ms, max_ms)


@dataclass
class LoggingConfig:
    """Logging configuration for the automation script."""
    level: Literal['debug', 'info', 'error']
    screenshot_on_error: bool
    screenshot_dir: str


@dataclass
class AutomationConfig:
    """Complete configuration for automation script."""
    target_url: str
    selectors: SelectorsConfig
    timeouts: TimeoutsConfig
    browser: BrowserConfig
    stealth: StealthConfig
    logging: LoggingConfig


# Default configuration instance
DEFAULT_CONFIG = AutomationConfig(
    target_url="https://example.com",  # Replace with actual target URL
    selectors=SelectorsConfig(
        signup_button="button[data-testid='signup-button']",  # Replace with actual selector
        email_input="input[type='email']"  # Replace with actual selector
    ),
    timeouts=TimeoutsConfig(
        page_load=30000,
        element_visible=30000,
        new_tab=10000
    ),
    browser=BrowserConfig(
        headless=False,
        user_data_dir="./browser_data",
        viewport=ViewportConfig(width=1920, height=1080)
    ),
    stealth=StealthConfig(
        enabled=True,
        human_like_typing=True,
        typing_delay_range=(50, 150)  # 50-150ms delays between keystrokes
    ),
    logging=LoggingConfig(
        level='info',
        screenshot_on_error=True,
        screenshot_dir="./screenshots"
    )
)
