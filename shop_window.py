from datetime import datetime
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QMessageBox, QComboBox, QSpinBox, QCheckBox, QMenu
)

from dota_items import Component, BasicItem, CombinedItem, NeutralItem
from shop_storage import SecretShop


class DotaShopWindow(QWidget):
    TITLE = "Справочник предметов и рецептов Dota 2"
    DEFAULT_LOGIN = "koil446"

    CATEGORIES = [
        ("Компонент", "Какой стат дает (+10 к силе)", True,
         lambda t, n, g, e: Component(t, n, g, e or "+статы")),
        ("Базовый", "Описание эффекта", True,
         lambda t, n, g, e: BasicItem(t, n, g, e or "Пассивный эффект")),
        ("Сборный (рецепт)", "Части через запятую: Yasha, Кая", True,
         lambda t, n, g, e: CombinedItem(t, n, g, e or "Основа, Рецепт")),
        ("Нейтралка", "Тир от 1 до 5 (например: 2)", False,
         lambda t, n, g, e: NeutralItem(t, n, int(e or 1))),
    ]

    def __init__(self, shop: SecretShop, login: str = DEFAULT_LOGIN):
        super().__init__()
        self._shop = shop
        self._login = login
        self._time_in = datetime.now()
        self._sort_asc = True
        self.resize(780, 480)
        self.setWindowTitle(self.TITLE)
        self.init_ui()

    @property
    def shop(self):
        return self._shop

    @shop.setter
    def shop(self, val):
        self._shop = val

    @property
    def login(self):
        return self._login

    @login.setter
    def login(self, val):
        self._login = str(val).strip() or self.DEFAULT_LOGIN

    @property
    def time_in(self):
        return self._time_in

    @time_in.setter
    def time_in(self, val):
        self._time_in = val

    @property
    def sort_asc(self):
        return self._sort_asc

    @sort_asc.setter
    def sort_asc(self, val):
        self._sort_asc = bool(val)

    @staticmethod
    def make_button(text: str, handler) -> QPushButton:
        btn = QPushButton(text)
        btn.clicked.connect(handler)
        return btn

    def init_ui(self):
        root = QVBoxLayout(self)

        top_bar = QHBoxLayout()
        lbl_header = QLabel("Потайная лавка Dota 2 — База рецептов")
        lbl_header.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.inp_login = QLineEdit(self._login)
        self.inp_login.setFixedWidth(120)
        top_bar.addWidget(lbl_header)
        top_bar.addStretch()
        top_bar.addWidget(QLabel("Игрок (login):"))
        top_bar.addWidget(self.inp_login)
        root.addLayout(top_bar)

        middle = QHBoxLayout()

        grp_form = QGroupBox("Новый предмет лавки")
        form = QFormLayout(grp_form)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.cb_category = QComboBox()
        self.cb_category.addItems([c[0] for c in self.CATEGORIES])
        self.cb_category.currentIndexChanged.connect(self.on_category_changed)
        self.inp_tag = QLineEdit()
        self.inp_tag.setPlaceholderText("например: desolator")
        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText("Название предмета")
        self.spin_gold = QSpinBox()
        self.spin_gold.setRange(0, 15000)
        self.spin_gold.setSingleStep(50)
        self.spin_gold.setValue(1000)
        self.inp_param = QLineEdit()

        form.addRow("Категория:", self.cb_category)
        form.addRow("Короткий тег:", self.inp_tag)
        form.addRow("Название:", self.inp_name)
        form.addRow("Стоимость (золото):", self.spin_gold)
        form.addRow("Бонус / Рецепт:", self.inp_param)
        form.addRow(self.make_button("Добавить в каталог", self.add_new_item))
        grp_form.setFixedWidth(310)
        middle.addWidget(grp_form)
        self.on_category_changed()

        grp_list = QGroupBox("Список артефактов")
        right = QVBoxLayout(grp_list)

        filter_row = QHBoxLayout()
        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("Поиск по названию или части рецепта...")
        self.inp_search.textChanged.connect(self.reload_list)
        self.chk_only_recipes = QCheckBox("Только сборные")
        self.chk_only_recipes.stateChanged.connect(self.reload_list)
        filter_row.addWidget(self.inp_search)
        filter_row.addWidget(self.chk_only_recipes)
        right.addLayout(filter_row)

        self.list_widget = QListWidget()
        right.addWidget(self.list_widget)

        btn_row = QHBoxLayout()
        btn_row.addWidget(self.make_button("Сортировать по цене", self.sort_catalog))
        btn_row.addWidget(self.make_button("Сумма золота", self.show_total_gold))
        btn_row.addWidget(self.make_button("Удалить", self.delete_selected))
        right.addLayout(btn_row)
        middle.addWidget(grp_list)
        root.addLayout(middle)

        status_row = QHBoxLayout()
        self.lbl_status = QLabel("Готово к работе")
        self.lbl_hint = QLabel("")
        self.lbl_hint.setAlignment(Qt.AlignmentFlag.AlignRight)
        for lbl in (self.lbl_status, self.lbl_hint):
            lbl.setStyleSheet("color: gray; font-size: 11px;")
        status_row.addWidget(self.lbl_status, 1)
        status_row.addWidget(self.lbl_hint)
        root.addLayout(status_row)

        self.reload_list()

    def on_category_changed(self):
        _, hint, paid, _ = self.CATEGORIES[self.cb_category.currentIndex()]
        if not paid: 
            self.spin_gold.setValue(0)
        self.spin_gold.setEnabled(paid)
        self.inp_param.setPlaceholderText(hint)

    def visible_items(self) -> list:
        query = self.inp_search.text().strip()
        items = self._shop.get_items(only_combined=self.chk_only_recipes.isChecked())
        return [it for it in items if not query or query in it]

    def fill_list(self, items: list):
        self.list_widget.clear()
        for it in items:
            row = QListWidgetItem(str(it))
            row.setData(Qt.ItemDataRole.UserRole, it.tag) 
            self.list_widget.addItem(row)

    def reload_list(self, *_):
        self.fill_list(self.visible_items())
        self.lbl_status.setText(
            f"Отображено предметов: {self.list_widget.count()} | Всего в базе: {len(self._shop.storage)}")

    def clear_form(self):
        for field in (self.inp_tag, self.inp_name, self.inp_param):
            field.clear()

    def add_new_item(self):
        tag, name = self.inp_tag.text().strip(), self.inp_name.text().strip()
        if not tag or not name:
            QMessageBox.warning(self, "Ошибка", "Укажите тег и название предмета")
            return
        create = self.CATEGORIES[self.cb_category.currentIndex()][3]
        try:
            item = create(tag, name, self.spin_gold.value(), self.inp_param.text().strip())
        except ValueError as e:
            QMessageBox.critical(self, "Ошибка ввода", f"Проверьте введённые данные: {e}")
            return
        self._shop.add_artifact(item)
        self.clear_form()
        self.reload_list()

    def delete_selected(self):
        current = self.list_widget.currentItem()
        if current is None:
            QMessageBox.information(self, "Удаление", "Сначала выделите предмет в списке")
            return
        self._shop.remove_artifact(current.data(Qt.ItemDataRole.UserRole))
        self.reload_list()

    def sort_catalog(self):
        self.fill_list(sorted(self.visible_items(), reverse=not self._sort_asc))
        direction = "по возрастанию" if self._sort_asc else "по убыванию"
        self.sort_asc = not self._sort_asc
        self.lbl_status.setText(f"Список отсортирован по золоту ({direction})")

    def show_total_gold(self):
        QMessageBox.information(
            self, "Стоимость каталога",
            f"Суммарная стоимость всех предметов в лавке: {self._shop.calc_total_gold()} золота")

    def save_report_on_exit(self):
        self.login = self.inp_login.text()
        fmt = "%d.%m.%Y %H:%M:%S"
        w = max(len(self._login), 10)
        widths = (w + 2, 21, 21)
        border = "+" + "+".join("-" * n for n in widths) + "+"
        sep = "|" + "|".join("-" * n for n in widths) + "|"
        header = f"| {'login':<{w}} |{'time_in':^21}|{'time_out':^21}|"
        row = f"| {self._login:<{w}} | {self._time_in.strftime(fmt)} | {datetime.now().strftime(fmt)} |"
        with open("report.txt", "w", encoding="utf-8") as f:
            f.write("\n".join([border, header, sep, row, border]) + "\n")

    def closeEvent(self, event):
        self.save_report_on_exit()
        event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            self.delete_selected()
        elif event.key() == Qt.Key.Key_Escape:
            self.clear_form()
            self.inp_search.clear()
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_F1:
            QMessageBox.information(
                self, "Справка",
                "Del - удалить предмет\nEsc - очистить поля\nCtrl+колесо - шаг цены\n"
                "Двойной клик - сбросить поиск\nПКМ - быстрое меню")
        super().keyReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.inp_search.clear()
        self.list_widget.clearSelection()
        super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            step = 100 if event.angleDelta().y() > 0 else -100
            self.spin_gold.setValue(self.spin_gold.value() + step)
        super().wheelEvent(event)

    def resizeEvent(self, event):
        size = event.size()
        self.setWindowTitle(f"{self.TITLE} ({size.width()}x{size.height()})")
        super().resizeEvent(event)

    def enterEvent(self, event):
        self.lbl_hint.setText("F1 — справка по клавишам")
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.lbl_hint.clear()
        super().leaveEvent(event)

    def showEvent(self, event):
        self.inp_tag.setFocus()
        super().showEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.addAction("Сортировать по золоту", self.sort_catalog)
        menu.addAction("Посчитать общую стоимость", self.show_total_gold)
        menu.addAction("Удалить выбранный предмет", self.delete_selected)
        menu.exec(event.globalPos())