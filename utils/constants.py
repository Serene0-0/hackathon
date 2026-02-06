""""
Constant Definition
"""
from __future__ import annotations

from enum import Enum

class WarmMessageTags(str, Enum):
    """
    Tags for Warm Messages
    """
    EMPATHY = "empathy"
    ENCOURAGEMENT = "encouragement"
    CALM = "calm"
    PROUD = "proud"
    GROUNDING = "grounding"
    SUPPORT = "support"
    HOPE = "hope"

    @classmethod
    def values(cls) -> list[str]:
        """
        Return all tag values
        :return: list of string
        """""
        return [tag.value for tag in cls]

    @classmethod
    def validate(cls, tag: str) -> bool:
        """
        Validate the validity of tag
        """
        return tag in cls.values()

SUGGESTED_RELATIONSHIPS = [
    "family",
    "friend",
    "roommate",
    "advisor",
    "partner",
    "classmate",
    "other"
]