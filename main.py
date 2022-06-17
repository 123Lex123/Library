import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
import sqlite3
from PyQt5 import uic

from Dialogs.BookChangeDialogFile import BookChangeDialog
from Dialogs.ReadingDialogFile import ReadingDialog
from Dialogs.UsersChangeDialogFile import UsersChangeDialog
from RegistrationAndLogin.RegisterLoginFile import RegDialog, LogDialog


# Основное окно
class LibMain(QMainWindow):
    def __init__(self):
        super(LibMain, self).__init__()
        uic.loadUi('RegLog.ui', self)

        # Подключение сигналов
        self.register_btn.clicked.connect(self.open_reg_form)
        self.login_btn.clicked.connect(self.open_log_form)

    # Открытие окна регистрации
    def open_reg_form(self):
        self.reg_dialog = RegDialog()
        self.reg_dialog.show()

    # Открытие окна входа
    def open_log_form(self):
        self.log_dialog = LogDialog(self)
        self.log_dialog.show()

    # Открытие ЛК
    def open_personal_acc(self, cur_user):
        self.con = sqlite3.connect('library.db')
        self.cur = self.con.cursor()

        # Определение роли текущего пользователя
        self.cur_user_role = self.cur.execute(f"""SELECT Role FROM roles 
        WHERE id = (SELECT RoleID FROM permissions 
        WHERE UserID = ((SELECT id FROM users WHERE username = '{cur_user}'))) """).fetchone()[0]

        # Определение ID текущего пользователя
        self.cur_user_id = self.cur.execute(f"""SELECT id FROM users
                                        WHERE username = '{cur_user}' """).fetchone()[0]

        # Инициализация ЛК в соответствии с ролью
        if self.cur_user_role == 'ADMIN':
            uic.loadUi('AdminPanel.ui', self)
            self.admin_panel_settings(cur_user)
        elif self.cur_user_role == 'LIBRARIAN':
            uic.loadUi('LibrarianPanel.ui', self)
            self.librarian_panel_settings(cur_user)
        elif self.cur_user_role == 'USER':
            uic.loadUi('UserPanel.ui', self)
            self.user_panel_settings(cur_user)

    # Настройки ЛК для администратора
    def admin_panel_settings(self, cur_user):
        self.user_permissions(cur_user)
        self.librarian_permissions()
        self.admin_permissions()

    # Настройки ЛК для библиотекаря
    def librarian_panel_settings(self, cur_user):
        self.user_permissions(cur_user)
        self.librarian_permissions()

    # Настройки ЛК для обычного пользовователя
    def user_panel_settings(self, cur_user):
        self.user_permissions(cur_user)

    # Инициализация пользовательских возможностей
    def user_permissions(self, cur_user):
        self.hello_lbl.setText(f'<html><head/><body><p><span style=" font-size:18pt;">'
                               f'Добрый день, {cur_user}</span></p></body></html>')
        self.reading_btn.clicked.connect(lambda: self.reading_dialog(cur_user))
        self.show_returns()
        self.return_btn.clicked.connect(self.return_book)
        self.reload_returns_btn.clicked.connect(self.reload_returns)

    # Инициализация возможностей библиотекаря
    def librarian_permissions(self):
        self.books_change_btn.clicked.connect(self.book_change_dialog)

    def admin_permissions(self):
        self.users_change_btn.clicked.connect(self.users_change_dialog)

    # Инициализация диалога на добавление/удаление книги
    def book_change_dialog(self):
        self.b_change = BookChangeDialog()
        self.b_change.show()

    # Инициализация диалога на изменение пользователей
    def users_change_dialog(self):
        self.u_change = UsersChangeDialog()
        self.u_change.show()

    # Вывод книг, которые нужно вернуть.
    def show_returns(self):
        self.return_books = self.cur.execute(f"""SELECT books.book, return_date FROM returns 
            INNER JOIN books ON returns.book_id = books.id 
            WHERE user_id = {self.cur_user_id}""").fetchall()

        for i in range(len(self.return_books)):
            self.return_list.addItem(f'{self.return_books[i][0]} - {self.return_books[i][1]}')

    # Перезагрузка списка книг на возврат
    def reload_returns(self):
        self.return_list.clear()
        self.show_returns()

    # Инициализация диалога "Взять почитать"
    def reading_dialog(self, cur_user):
        self.r_dialog = ReadingDialog(cur_user)
        self.r_dialog.show()

    # Возврат выделенных книг в списке
    def return_book(self):
        self.selected_book = ''
        if self.return_list.selectedItems():
            self.book_item = self.return_list.selectedItems()[0].text()
            self.selected_book = (self.book_item[:self.book_item.find('-')]).strip()

            self.selected_book_id = self.cur.execute(f"""SELECT id FROM books 
            WHERE book = '{self.selected_book}' """).fetchone()[0]

            self.return_list.takeItem(self.return_list.currentRow())

            self.cur.execute(f"""DELETE from RETURNS 
            WHERE book_id = {self.selected_book_id} AND user_id = {self.cur_user_id} """)
            self.con.commit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LibMain()
    ex.show()
    sys.exit(app.exec())