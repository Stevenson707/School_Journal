import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QInputDialog
import webbrowser

DB_NAME = 'journal_db.sqlite'


'''Окно авторизации'''
class Authorization(QMainWindow):
    '''Инициализация класса "Authorization"'''
    def __init__(self):
        super().__init__()
        uic.loadUi('Authorization.ui', self)
        self.con = sqlite3.connect(DB_NAME)
        self.pushButton.clicked.connect(self.sign_in)
        self.pushButton_2.clicked.connect(self.sign_up)

    '''Регистрация в системе'''
    def sign_up(self):
        if self.radioButton.isChecked():
            self.statusBar().showMessage("")
            cur = self.con.cursor()
            cur.execute("SELECT * FROM teacher WHERE id=1")
            zapros = cur.fetchall()

            if zapros != []:
                self.statusBar().showMessage("Учитель уже зарегистрирован")

            else:
                log_t = self.lineEdit_loginReg.text()
                pas_t = self.lineEdit_passwordReg.text()
                cur = self.con.cursor()
                cur.execute(f"SELECT * FROM student WHERE login='{log_t}'")  # Изменение "teacher" на "student"
                value_teacher = cur.fetchall()

                if value_teacher != []:
                    self.statusBar().showMessage("Такой пользователь уже существует")

                else:
                    cur.execute("INSERT INTO teacher VALUES (?,?,?)", (1, log_t, pas_t))
                    self.con.commit()
                    self.statusBar().showMessage("Успешная регистрация!")

        if self.radioButton_2.isChecked():
            self.statusBar().showMessage("")
            log_s = self.lineEdit_loginReg.text()
            pas_s = self.lineEdit_passwordReg.text()
            cur = self.con.cursor()
            cur.execute(f"SELECT * FROM student WHERE login='{log_s}'")
            value_student = cur.fetchall()
            cur.execute(f"SELECT * FROM teacher WHERE login='{log_s}'")
            value_t = cur.fetchall()

            if value_student != [] or value_t != []:
                self.statusBar().showMessage("Такой пользователь уже существует")

            else:
                cur.execute("INSERT INTO student VALUES (?,?)", (log_s, pas_s))
                self.con.commit()
                self.statusBar().showMessage("Успешная регистрация!")

    '''Вход в систему'''
    def sign_in(self):
        self.statusBar().showMessage("")
        login = self.lineEdit_loginVhod.text()
        password = self.lineEdit_passwordVhod.text()
        cur = self.con.cursor()
        cur.execute(f"SELECT * FROM student WHERE login='{login}' AND password='{password}'")
        value_student = cur.fetchall()
        cur.execute(f"SELECT * FROM teacher WHERE login='{login}' AND password='{password}'")
        value_teacher = cur.fetchall()

        if value_student != []:
            self.open_journal_student()

        elif value_teacher != []:
            self.open_journal_teacher()

        elif value_student == []:
            self.statusBar().showMessage("Сначала зарегистрируйтесь")

        elif value_teacher == []:
            self.statusBar().showMessage("Сначала зарегистрируйтесь")

    '''Открытие учительского окна'''
    def open_journal_teacher(self):
        login = self.lineEdit_loginVhod.text()
        password = self.lineEdit_passwordVhod.text()
        self.teacher = Teacher(self, login, password)
        self.teacher.show()
        self.lineEdit_loginVhod.clear()
        self.lineEdit_passwordVhod.clear()
        self.lineEdit_loginReg.clear()
        self.lineEdit_passwordReg.clear()
        self.statusBar().showMessage("")
        # Сохраняем логин последнего заходившего пользователя в файл "last_user.txt"
        with open('last_user.txt', 'w', encoding='utf8') as f:
            f.write(login)

    '''Открытие ученического окна'''
    def open_journal_student(self):
        login = self.lineEdit_loginVhod.text()
        password = self.lineEdit_passwordVhod.text()
        self.student = Student(self, login, password)
        self.student.show()
        self.lineEdit_loginVhod.clear()
        self.lineEdit_passwordVhod.clear()
        self.lineEdit_loginReg.clear()
        self.lineEdit_passwordReg.clear()
        self.statusBar().showMessage("")
        # Сохраняем логин последнего заходившего пользователя в файл "last_user.txt"
        with open('last_user.txt', 'w', encoding='utf8') as f:
            f.write(login)


'''Окно журнала учителя'''
class Teacher(QMainWindow):
    '''Инициализация класса "Teacher"'''
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('teacher_journal.ui', self)
        # Подключаемся к базе
        self.con = sqlite3.connect(DB_NAME)
        self.login = args[1]
        self.password = args[2]
        self.deleteAction.triggered.connect(self.delete_user)
        self.exitAction.triggered.connect(self.close_app)
        self.button_add_db.clicked.connect(self.add_db)
        self.button_add_student.clicked.connect(self.add_student)
        self.button_delete_student.clicked.connect(self.delete_student)
        self.button_desc_prog.clicked.connect(self.show_desc_program)


    '''Получаем путь к выбранному файлу'''
    def add_db(self):
        # Получаем путь к выбранной базе
        self.fname = QFileDialog.getOpenFileName(self, 'Выбор базы')[0]
        self.show_journal()

    '''Показываем последнюю версию журнала'''
    def show_journal(self):
        db = QSqlDatabase.addDatabase('QSQLITE')
        # Укажем имя базы данных
        db.setDatabaseName(self.fname)
        # И откроем подключение
        db.open()

        # QTableView - виджет для отображения данных из базы
        view = self.tableView
        # Создадим объект QSqlTableModel,
        # зададим таблицу, с которой он будет работать,
        #  и выберем все данные
        model = QSqlTableModel(self, db)
        model.setTable('klass')
        model.select()
        self.model = model

        # Для отображения данных на виджете
        # свяжем его и нашу модель данных
        view.setModel(model)

    '''Добавляем строку в таблице'''
    def add_student(self):
        self.statusBar().showMessage("")
        try:
            # берем структуру записи из имеющейся модели
            rec = self.model.record()
            # добавляем запись в конец таблицы
            self.model.insertRecord(-1, rec)
            self.tableView.selectColumn(2)
            self.tableView.selectRow(self.model.rowCount() - 1)
            self.tableView.setFocus()
            self.show_journal()
        except:
            self.statusBar().showMessage("Загрузите базу для её редактирования")

    '''Удаляем, выбранную в диалоговом окне, строку'''
    def delete_student(self):
        self.statusBar().showMessage("")
        try:
            fname = self.fname.split('/')[-1]
            fname1 = sqlite3.connect(fname)
            name, ok_pressed = QInputDialog.getText(self, "Удаление",
                                                "Введите id ученика")
            if ok_pressed:
                cur = fname1.cursor()
                cur.execute(f"DELETE FROM klass WHERE id='{int(name)}'")
                fname1.commit()
                self.show_journal()
        except:
            self.statusBar().showMessage("Загрузите базу для её редактирования")

    '''Показываем окно с описанием программы'''
    def show_desc_program(self):
        self.p = Program()
        self.p.show()

    '''Закрываем окно учителя'''
    def close_app(self):
        self.close()

    '''Удаляем аккаунт, в котором сейчас находимся'''
    def delete_user(self):
        cur = self.con.cursor()
        cur.execute(f"DELETE FROM teacher WHERE login = '{self.login}' AND password = '{self.password}'")
        self.con.commit()
        self.close()


'''Окно ученика'''
class Student(QMainWindow):
    '''Инициализация класса "Student"'''
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('student_journal.ui', self)
        # Подключение к базе
        self.con = sqlite3.connect(DB_NAME)
        self.login = args[1]
        self.password = args[2]
        self.action_2.triggered.connect(self.delete_user)
        self.action.triggered.connect(self.close_app)
        self.button_add_db.clicked.connect(self.add_db)
        self.button_desc_prog.clicked.connect(self.show_desc_program)

    '''Получаем путь к выбранному файлу'''
    def add_db(self):
        # Получаем путь к выбранной базе
        self.fname = QFileDialog.getOpenFileName(self, 'Выбор базы')[0]
        self.show_journal()

    '''Показываем последнюю версию журнала'''
    def show_journal(self):
        db = QSqlDatabase.addDatabase('QSQLITE')
        # Укажем имя базы данных
        db.setDatabaseName(self.fname)
        # И откроем подключение
        db.open()

        # QTableView - виджет для отображения данных из базы
        view = self.tableView
        # Создадим объект QSqlTableModel,
        # зададим таблицу, с которой он будет работать,
        #  и выберем все данные
        model = QSqlTableModel(self, db)
        model.setTable('klass')
        model.select()

        # Для отображения данных на виджете
        # свяжем его и нашу модель данных
        view.setModel(model)
        self.tableView.setEnabled(False)

    '''Показываем окно с описанием программы'''
    def show_desc_program(self):
        self.p = Program()
        self.p.show()

    '''Закрываем окно ученика'''
    def close_app(self):
        self.close()

    '''Удаляем аккаунт, в котором сейчас находимся'''
    def delete_user(self):
        cur = self.con.cursor()
        cur.execute(f"DELETE FROM student WHERE login = '{self.login}' AND password = '{self.password}'")
        self.con.commit()
        self.close()


'''Окно описания программы'''
class Program(QMainWindow):
    '''Инициализация класса "Program"'''
    def __init__(self):
        super().__init__()
        uic.loadUi('desc_program.ui', self)
        self.button_vk.clicked.connect(self.vk)
        self.button_github.clicked.connect(self.github)
        self.button_discord.clicked.connect(self.discord)

    '''Отправляем пользователя по ссылке на свой профиль VK'''
    def vk(self):
        webbrowser.open_new(r"https://vk.com/k_r_d123")
    '''Отправляем пользователя по ссылке на свой профиль GitHub'''
    def github(self):
        webbrowser.open_new(r"https://github.com/Stevenson707")

    '''Отправляем пользователя по ссылке на свой профиль Discord'''
    def discord(self):
        webbrowser.open_new(r"https://discord.com/channels/@me")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Authorization()
    ex.show()
    sys.exit(app.exec())
