import sqlite3

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog

from exceptions.ExceptionsFile import WrongLoginError, LoginLengthError, \
    PasswordLengthError, PasswordDigitError, PasswordLetterError, WrongPasswordError


# Регистрация
class RegDialog(QDialog):
    def __init__(self):
        super(RegDialog, self).__init__()
        uic.loadUi('RegDialog.ui', self)

        # Подключение сигналов
        self.reg_btn.clicked.connect(self.registration)

    def registration(self):
        try:
            # Подключение базы данных
            self.con = sqlite3.connect('library.db')
            self.cur = self.con.cursor()

            # Проверка логина
            self.login_exists = self.cur.execute(f"""SELECT username FROM users 
            WHERE username = '{self.reg_login_line.text()}' """).fetchall()

            if self.login_exists:
                raise WrongLoginError
            elif len(self.reg_login_line.text()) <= 6 or len(self.reg_login_line.text()) >= 14:
                raise LoginLengthError

            # Проверка пароля
            elif len(self.reg_password_line.text()) < 6:
                raise PasswordLengthError
            elif self.reg_password_line.text().isalpha():
                raise PasswordDigitError
            elif self.reg_password_line.text().isdigit():
                raise PasswordLetterError
            else:
                self.cur.execute(f"""INSERT INTO users (username, password) 
                VALUES ('{self.reg_login_line.text()}', '{self.reg_password_line.text()}')""")

                self.new_id = self.cur.execute(f"""SELECT id FROM users 
                WHERE username = '{self.reg_login_line.text()}'""").fetchone()

                self.cur.execute(f"""INSERT INTO permissions (UserID, RoleID) 
                VALUES ({self.new_id[0]}, 3)""")

                self.status_lbl.setText('Регистрация успешна!')
                self.con.commit()

        except LoginLengthError:
            self.status_lbl.setText('Логин должен быть от 6 до 14 символов.')
        except WrongLoginError:
            self.status_lbl.setText('Логин уже существует, выберите другой.')
        except PasswordLengthError:
            self.status_lbl.setText('Пароль должен быть не менее 6 символов.')
        except PasswordDigitError:
            self.status_lbl.setText('В пароле должны использоваться цифры.')
        except PasswordLetterError:
            self.status_lbl.setText('В пароле должны использоваться буквы.')


# Вход
class LogDialog(QDialog):
    def __init__(self, window):
        super(LogDialog, self).__init__()
        uic.loadUi('LoginDialog.ui', self)
        # Предзагрузка основного окна
        self.main_window = window

        # Подключение сигналов
        self.enter_btn.clicked.connect(self.to_login)

    # Функция входа
    def to_login(self):
        try:
            # Подключение БД
            self.con = sqlite3.connect('library.db')
            self.cur = self.con.cursor()

            # Проверка логина
            self.login_exists = self.cur.execute(f"""SELECT username FROM users 
                        WHERE username = '{self.login_line.text()}' """).fetchone()

            if not self.login_exists:
                raise WrongLoginError

            # Проверка пароля
            self.correct_password = self.cur.execute(f"""SELECT password FROM users 
            WHERE username = '{self.login_exists[0]}'""").fetchone()

            if self.password_line.text() != str(self.correct_password[0]):
                raise WrongPasswordError
        except WrongLoginError:
            self.status_lbl.setText('Такого пользователя не существует.')
        except WrongPasswordError:
            self.status_lbl.setText('Пароль неверный.')
        else:
            self.status_lbl.setText('Успешный вход!')
            cur_user = f'{self.login_exists[0]}'
            # Инициализация ЛК для текущего пользователя.
            self.main_window.open_personal_acc(cur_user)
            self.close()
