"""
Prompting Guide Updater Agent

An autonomous agent that keeps AI provider prompting documentation up to date.
Uses Claude Agent SDK with Firecrawl for web scraping.
"""
from .agent import run_updater, run_single_provider
from .config import PROVIDER_CONFIGS

__all__ = ["run_updater", "run_single_provider", "PROVIDER_CONFIGS"]

