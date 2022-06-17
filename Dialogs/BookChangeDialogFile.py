import sqlite3

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QTableWidgetItem


# Добавление/Удаление книг
class BookChangeDialog(QDialog):
    def __init__(self):
        super(BookChangeDialog, self).__init__()
        uic.loadUi('BookChangeDialogWindow.ui', self)

        # Подключение сигналов
        self.add_new_book_btn.clicked.connect(self.add_book)
        self.delete_book_btn.clicked.connect(self.delete_book)
        self.reload_del_books_btn.clicked.connect(self.reload_del_books)
        self.delete_search_btn.clicked.connect(self.delete_book_with_src)

        # Подключение БД
        self.con = sqlite3.connect('library.db')
        self.cur = self.con.cursor()

        # Список всех книг
        self.all_books = self.cur.execute("""SELECT book FROM books""").fetchall()
        self.all_books = list(map(lambda x: x[0], self.all_books))

        # Список жанров и заполнение выпадающего списка
        self.genres = self.cur.execute("""SELECT genre FROM genres""").fetchall()
        self.genres = [self.genres[i][0] for i in range(len(self.genres))]
        self.new_book_genre.addItem('')
        for i in range(len(self.genres)):
            self.new_book_genre.addItem(self.genres[i])

        self.show_books()

    # Отображение книг в таблице
    def show_books(self):
        result = self.cur.execute(f"""SELECT books.id, book, author, genres.genre 
        FROM books INNER JOIN genres ON genres.id = books.genre""").fetchall()

        self.del_books_table.setRowCount(len(result))
        self.del_books_table.setColumnCount(4)
        self.del_books_table.setHorizontalHeaderLabels(['id', 'Книга', 'Автор', 'Жанр'])
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.del_books_table.setItem(i, j, QTableWidgetItem(str(val)))

    # Функция добавления книги
    def add_book(self):
        self.new_book_exists = self.cur.execute(f"""SELECT book FROM books 
        WHERE book = '{self.new_book_name.text()}' """).fetchone()

        if not self.new_book_exists:
            if self.new_book_name.text() and self.new_book_author.text() and \
                    self.new_book_genre.currentText():
                self.new_book = (f'{self.new_book_name.text()}', f'{self.new_book_author.text()}',
                                 self.new_book_genre.currentIndex())

                self.cur.execute(f"""INSERT INTO books(book, author, genre) 
                VALUES ('{self.new_book[0]}', '{self.new_book[1]}', {self.new_book[2]})""")
                self.con.commit()
                self.add_status.setText('<html><head/><body><p>'
                                        '<span style=" font-size:10pt;">Книга успешно добавлена!'
                                        '</span></p></body></html>')

    # Функция поиска книги
    def delete_book_with_src(self):
        result = self.cur.execute(f"""SELECT books.id, book, author, genres.genre 
        FROM books INNER JOIN genres ON genres.id = books.genre 
        WHERE book LIKE '{self.delete_search.text()}%'""").fetchall()

        self.del_books_table.setRowCount(len(result))
        self.del_books_table.setColumnCount(4)
        self.del_books_table.setHorizontalHeaderLabels(['id', 'Книга', 'Автор', 'Жанр'])
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.del_books_table.setItem(i, j, QTableWidgetItem(str(val)))

    # Функция перезагрузки таблицы
    def reload_del_books(self):
        self.delete_search.clear()
        self.del_books_table.clear()
        self.show_books()

    # Функиця удаления книги
    def delete_book(self):
        if self.del_books_table.selectedItems():
            self.selected_book_del = self.del_books_table.selectedItems()[0].text()

            self.all_books = self.cur.execute("""SELECT book FROM books""").fetchall()
            self.all_books = list(map(lambda x: x[0], self.all_books))

            if self.selected_book_del in self.all_books:
                self.cur.execute(f"""DELETE FROM books WHERE book = '{self.selected_book_del}'""")
                self.con.commit()