from dota_items import DotaItem, Component, BasicItem, CombinedItem, NeutralItem


class CustomMap:
    def __init__(self):
        self._pairs = []

    @property
    def pairs(self):
        return self._pairs

    @pairs.setter
    def pairs(self, val):
        self._pairs = [list(p) for p in val]

    def _index(self, key: str) -> int:
        for i, pair in enumerate(self._pairs):
            if pair[0] == key:
                return i
        return -1

    def put(self, key: str, item: DotaItem):
        i = self._index(key)
        if i >= 0:
            self._pairs[i][1] = item
        else:
            self._pairs.append([key, item])

    def get(self, key: str) -> DotaItem:
        i = self._index(key)
        if i < 0:
            raise KeyError(f"Предмет с тегом {key} не найден")
        return self._pairs[i][1]

    def delete(self, key: str):
        i = self._index(key)
        if i < 0:
            raise KeyError(f"Нечего удалять по ключу {key}")
        del self._pairs[i]

    def values_list(self) -> list:
        return [pair[1] for pair in self._pairs]

    def __len__(self) -> int:
        return len(self._pairs)

    def __contains__(self, key: str) -> bool:
        return self._index(key) >= 0

    def __str__(self) -> str:
        return f"CustomMap(count={len(self._pairs)})"

    __repr__ = __str__

    def __eq__(self, other) -> bool:
        return isinstance(other, CustomMap) and self._pairs == other.pairs


class SecretShop:
    def __init__(self):
        self._storage = CustomMap()

    @property
    def storage(self):
        return self._storage

    @storage.setter
    def storage(self, val: CustomMap):
        self._storage = val

    def add_artifact(self, item: DotaItem):
        self._storage.put(item.tag, item)

    def remove_artifact(self, tag: str):
        self._storage.delete(tag)

    def get_items(self, only_combined: bool = False) -> list:
        items = self._storage.values_list()
        if only_combined:
            return [it for it in items if isinstance(it, CombinedItem)]
        return items

    def calc_total_gold(self) -> int:
        return sum(self._storage.values_list())

    def __str__(self) -> str:
        return f"SecretShop(предметов: {len(self._storage)}, золота: {self.calc_total_gold()})"

    __repr__ = __str__

    def __eq__(self, other) -> bool:
        return isinstance(other, SecretShop) and self._storage == other.storage

    @staticmethod
    def create_default_shop():
        shop = SecretShop()
        starter_pack = [
            Component("branch", "Iron Branch (Веточка)", 50, "+1 ко всем статам"),
            Component("ogre_axe", "Ogre Axe", 1000, "+10 к силе"),
            Component("alacrity", "Blade of Alacrity", 1000, "+10 к ловкости"),
            Component("reaver", "Reaver", 2800, "+25 к силе"),
            BasicItem("boots", "Boots of Speed", 500, "+45 к скорости бега"),
            BasicItem("blink", "Blink Dagger", 2250, "Прыжок на 1200 ед."),
            BasicItem("wand", "Magic Wand (Стики)", 450, "Восстановление ХП/Маны"),
            CombinedItem("bkb", "Black King Bar", 4050, ("Ogre Axe", "Mithril Hammer", "Рецепт")),
            CombinedItem("manta", "Manta Style", 4600, ("Yasha", "Ultimate Orb", "Рецепт")),
            CombinedItem("pt", "Power Treads (ПТ)", 1400, ("Boots of Speed", "Gloves of Haste", "Belt of Strength")),
            NeutralItem("pig_pole", "Pig Pole", 1),
            NeutralItem("paladin", "Paladin Sword", 3),
        ]
        for it in starter_pack:
            shop.add_artifact(it)
        return shop
