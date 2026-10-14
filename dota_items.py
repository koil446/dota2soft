from abc import ABC, abstractmethod


class DotaItem(ABC):
    def __init__(self, tag: str, name: str, gold: int):
        self.tag = tag
        self.name = name
        self.gold = gold

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, val):
        self._tag = str(val).strip()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        self._name = str(val).strip()

    @property
    def gold(self):
        return self._gold

    @gold.setter
    def gold(self, val):
        if int(val) < 0:
            raise ValueError("Золото не может быть отрицательным")
        self._gold = int(val)

    @staticmethod
    def format_gold(amount: int) -> str:
        return f"{amount} золота"

    @abstractmethod
    def get_description(self) -> str:
        pass

    def __str__(self) -> str:
        return self.get_description()

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._tag!r}, {self._name!r}, {self._gold})"

    def __eq__(self, other) -> bool:
        return isinstance(other, DotaItem) and self._tag == other.tag and self._gold == other.gold

    def __lt__(self, other) -> bool:
        return self._gold < other.gold

    def __gt__(self, other) -> bool:
        return self._gold > other.gold

    def __add__(self, other) -> int:
        return self._gold + (other if isinstance(other, int) else other.gold)

    __radd__ = __add__

    def __len__(self) -> int:
        return 1

    def __contains__(self, text: str) -> bool:
        return text.lower() in self._name.lower()


class SimpleItem(DotaItem):
    LABEL = ""

    def __init__(self, tag: str, name: str, gold: int, note: str):
        super().__init__(tag, name, gold)
        self.note = note

    @property
    def note(self):
        return self._note

    @note.setter
    def note(self, val):
        self._note = str(val)

    def get_description(self) -> str:
        return f"[{self.LABEL}] {self._name} ({self._note}) — {self.format_gold(self._gold)}"


class Component(SimpleItem):
    LABEL = "Компонент"


class BasicItem(SimpleItem):
    LABEL = "Базовый"


class CombinedItem(DotaItem):
    def __init__(self, tag: str, name: str, gold: int, recipe_parts):
        super().__init__(tag, name, gold)
        self.recipe_parts = recipe_parts

    @property
    def recipe_parts(self):
        return self._recipe_parts

    @recipe_parts.setter
    def recipe_parts(self, val):
        if isinstance(val, str):
            val = val.split(",")
        self._recipe_parts = tuple(p.strip() for p in val if p.strip())

    def __len__(self) -> int:
        return len(self._recipe_parts)

    def __contains__(self, text: str) -> bool:
        in_parts = any(text.lower() in p.lower() for p in self._recipe_parts)
        return in_parts or super().__contains__(text)

    def get_description(self) -> str:
        parts = " + ".join(self._recipe_parts)
        return f"[Сборный | частей: {len(self)}] {self._name} ({parts}) — {self.format_gold(self._gold)}"


class NeutralItem(DotaItem):
    def __init__(self, tag: str, name: str, tier: int):
        super().__init__(tag, name, 0)
        self.tier = tier

    @property
    def tier(self):
        return self._tier

    @tier.setter
    def tier(self, val):
        if not 1 <= int(val) <= 5:
            raise ValueError("Тир должен быть от 1 до 5")
        self._tier = int(val)

    def get_description(self) -> str:
        return f"[Нейтралка T{self._tier}] {self._name} — Бесплатно (Тир {self._tier})"