import sqlite3

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QTableWidgetItem


# Диалог изменения пользователей
class UsersChangeDialog(QDialog):
    def __init__(self):
        super(UsersChangeDialog, self).__init__()
        uic.loadUi('UsersChangeDialogWindow.ui', self)

        # Подключение базы данных
        self.con = sqlite3.connect('library.db')
        self.cur = self.con.cursor()

        # Подключение сигналов к функциям
        self.search_id_box.valueChanged.connect(self.search_users)
        self.reload_users.clicked.connect(self.reload_users_table)
        self.update_role_btn.clicked.connect(self.update_role)
        self.del_user_btn.clicked.connect(self.delete_user)

        self.show_users()

        # Список всех пользователей
        self.all_users = self.cur.execute("""SELECT username FROM users""").fetchall()
        self.all_users = list(map(lambda x: x[0], self.all_users))

        # Список всех ролей
        self.roles = self.cur.execute("""SELECT Role FROM roles""").fetchall()
        self.roles = list(map(lambda x: x[0], self.roles))

        # Заполнение выпадающего списка ролями
        self.new_role_box.addItems(self.roles)

    # Функция обновления роли
    def update_role(self):
        # Список всех ID
        self.all_ids = self.cur.execute("""SELECT id FROM users""").fetchall()
        self.all_ids = list(map(lambda x: x[0], self.all_ids))

        # Проверка на существование ID и обновление роли
        if self.new_role_id.value() not in self.all_ids:
            self.upd_status.setText('<html><head/><body>'
                                    '<p>Пользователя с таким ID не существует!'
                                    '<br/>Сверьтесь с таблицей слева.'
                                    '</p></body></html>')
        else:
            if self.new_role_box.currentText() == 'ADMIN':
                self.cur.execute(f"""UPDATE permissions SET RoleID = 1 
                WHERE UserID = {self.new_role_id.value()} """)
            if self.new_role_box.currentText() == 'LIBRARIAN':
                self.cur.execute(f"""UPDATE permissions SET RoleID = 2
                WHERE UserID = {self.new_role_id.value()} """)
            if self.new_role_box.currentText() == 'USER':
                self.cur.execute(f"""UPDATE permissions SET RoleID = 3 
                WHERE UserID = {self.new_role_id.value()} """)
            self.upd_status.setText('<html><head/><body>'
                                    '<p>Роль успешно обновлена!</p></body></html>')
            self.con.commit()

    # Функция удаления пользователя
    def delete_user(self):
        if self.users_table.selectedItems():
            self.selected_user = self.users_table.selectedItems()[0].text()
            if self.selected_user in self.all_users:
                self.cur.execute(f"""DELETE FROM users WHERE username = '{self.selected_user}' """)
                self.con.commit()

    # Функция перезагрузки таблицы
    def reload_users_table(self):
        self.users_table.clear()
        self.search_id_box.setValue(0)
        self.show_users()

    # Функция отображения таблицы
    def show_users(self):
        result = self.cur.execute(f"""SELECT users.id, users.username, roles.Role FROM users 
        INNER JOIN permissions ON users.id = permissions.UserID
        INNER JOIN roles ON permissions.RoleID = roles.id""").fetchall()

        self.users_table.setRowCount(len(result))
        self.users_table.setColumnCount(3)
        self.users_table.setHorizontalHeaderLabels(['id', 'User', 'Роль'])
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.users_table.setItem(i, j, QTableWidgetItem(str(val)))

    # Функция поиска пользователей
    def search_users(self):
        if self.search_id_box.value() == 0:
            self.show_users()
        else:
            result = self.cur.execute(f"""SELECT users.id, users.username, roles.Role FROM users 
                    INNER JOIN permissions ON users.id = permissions.UserID
                    INNER JOIN roles ON permissions.RoleID = roles.id 
                    WHERE users.id = {self.search_id_box.value()}""").fetchall()

            self.users_table.setRowCount(len(result))
            self.users_table.setColumnCount(3)
            self.users_table.setHorizontalHeaderLabels(['id', 'User', 'Роль'])
            for i, elem in enumerate(result):
                for j, val in enumerate(elem):
                    self.users_table.setItem(i, j, QTableWidgetItem(str(val)))