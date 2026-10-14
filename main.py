import sys
from PyQt6.QtWidgets import QApplication

from shop_storage import SecretShop
from shop_window import DotaShopWindow


class AppLauncher:
    @staticmethod
    def start():
        app = QApplication(sys.argv)
        shop = SecretShop.create_default_shop()
        win = DotaShopWindow(shop, login="koil446")
        win.show()
        sys.exit(app.exec())


if __name__ == "__main__":
    AppLauncher.start()