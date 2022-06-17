import datetime
import sqlite3

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QTableWidgetItem


# Диалог "Взять почитать"
class ReadingDialog(QDialog):
    def __init__(self, cur_user):
        super(ReadingDialog, self).__init__()
        uic.loadUi('ReadingDialog.ui', self)

        # Подключение БД
        self.con = sqlite3.connect('library.db')
        self.cur = self.con.cursor()

        # Заполнение таблицы
        result = self.cur.execute("""SELECT book, author, genres.genre FROM books 
        INNER JOIN genres ON genres.id = books.genre""").fetchall()

        self.books_table.setRowCount(len(result))
        self.books_table.setColumnCount(3)
        self.books_table.setHorizontalHeaderLabels(['Книга', 'Автор', 'Жанр'])
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.books_table.setItem(i, j, QTableWidgetItem(str(val)))

        # Заполнение выпадающего списка жанров
        self.genres = self.cur.execute("""SELECT genre FROM genres""").fetchall()
        self.genres_filter.addItem('Все')
        self.genres = [self.genres[i][0] for i in range(len(self.genres))]
        for i in range(len(self.genres)):
            self.genres_filter.addItem(self.genres[i])

        # Подключение сигналов
        self.genres_filter.currentTextChanged.connect(self.use_filters)
        self.order_btn.clicked.connect(lambda: self.order_book(cur_user))

    # Функция фильтрации по выбранному жанру в выпадающем списке
    def use_filters(self):
        self.filtered_genre = self.genres_filter.currentText()

        if self.filtered_genre == 'Все':
            result = self.cur.execute("""SELECT book, author, genres.genre FROM books 
                    INNER JOIN genres ON genres.id = books.genre""").fetchall()
            self.books_table.setRowCount(len(result))
            self.books_table.setColumnCount(3)
            for i, elem in enumerate(result):
                for j, val in enumerate(elem):
                    self.books_table.setItem(i, j, QTableWidgetItem(str(val)))

        else:
            result = self.cur.execute(f"""SELECT book, author, genres.genre FROM books 
            INNER JOIN genres ON genres.id = books.genre 
            WHERE genres.genre = '{self.filtered_genre}' """).fetchall()

            self.books_table.setRowCount(len(result))
            self.books_table.setColumnCount(3)
            for i, elem in enumerate(result):
                for j, val in enumerate(elem):
                    self.books_table.setItem(i, j, QTableWidgetItem(str(val)))

    # Функция записи книги в ЛК текущего пользователя
    def order_book(self, cur_user):
        self.ordered_book = ''

        self.cur_user_id = self.cur.execute(f"""SELECT id FROM users
                        WHERE username = '{cur_user}' """).fetchone()[0]

        if self.books_table.selectedItems():
            self.ordered_book = self.books_table.selectedItems()[-1].text()

            self.con = sqlite3.connect('library.db')
            self.cur = self.con.cursor()

            self.all_books = self.cur.execute("""SELECT book FROM books""").fetchall()
            self.all_books = list(map(lambda x: x[0], self.all_books))

            if self.ordered_book in self.all_books:
                self.ordered_book_id = self.cur.execute(f"""SELECT id FROM books
                WHERE book = '{self.ordered_book}' """).fetchone()[0]

                self.book_already_taken = self.cur.execute(f"""SELECT user_id, book_id FROM returns 
                WHERE user_id = '{self.cur_user_id}' 
                AND book_id = '{self.ordered_book_id}' """).fetchone()

                if not self.book_already_taken:
                    self.cur.execute(f"""INSERT INTO returns(book_id, user_id, return_date)
                    VALUES ({self.ordered_book_id},
                    {self.cur_user_id}, 
                    '{(datetime.datetime.now() + datetime.timedelta(5)).strftime('%d.%m.%Y')}')""")
                    self.con.commit()
                    self.close()
