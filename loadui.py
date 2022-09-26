import sqlite3
import sys
from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton, QListWidget, QLineEdit, QMessageBox, \
                            QGridLayout, QWidget, QDialog

# Creating variables to be user globally to check what is the logged user and the last user created in the app session
logged_user = ""
created_user = ""

# Creating database that stores user information
conn = sqlite3.connect('users.db')
cur = conn.cursor()
cur.execute("""CREATE TABLE if not exists login_information(username_id text, user_password text)""")
conn.commit()
conn.close()


def insert_user_db(table, user_id, password):
    """Inserts tasks on the database."""
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute(f"""INSERT INTO {table} VALUES (?,?)""", [user_id, password])
    conn.commit()
    conn.close()


def check_username_exists(db, table, username):
    """Returns True if the username already exists and False otherwise."""
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table} WHERE username_id = '{username}'")
    return cur.fetchone()


def create_tasks_table(username):
    """Creates a task table named after the username"""
    conn = sqlite3.connect('tasks_db.db')
    cur = conn.cursor()
    cur.execute(f"CREATE TABLE if not exists '{username}'(task text)")
    conn.commit()
    conn.close()


def go_to_login():
    """Redirects user back to the login page."""
    login_page = LoginForm()
    widget.addWidget(login_page)
    widget.setCurrentIndex(widget.currentIndex() + 1)


class CreateAccount(QDialog):
    """ GUI class to the Create Account main window."""
    def __init__(self):
        super().__init__()
        uic.loadUi("createacc.ui", self)
        self.setFixedSize(400, 260)
        self.msg = QMessageBox()

        # Defining GUI elements using the findChild method
        self.user_create = self.findChild(QLineEdit, "username_lineEdit")
        self.set_password_field = self.findChild(QLineEdit, "password_lineEdit_2")
        self.confirm_password_field = self.findChild(QLineEdit, "repeatpassword_lineEdit_3")
        self.create_account_button = self.findChild(QPushButton, "createAccountButton")
        self.return_login_button = self.findChild(QPushButton, "backLoginButton")
        self.error_label = self.findChild(QLabel, "error_label")

        # Setting EchoMode to hide password and assigning functions to the buttons
        self.set_password_field.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirm_password_field.setEchoMode(QtWidgets.QLineEdit.Password)
        self.create_account_button.clicked.connect(self.signup_function)
        self.return_login_button.clicked.connect(go_to_login)

    def signup_function(self):
        """Creates new users' (registration)."""
        user_text = self.user_create.text() # Creating variables to convert GUI objects into text (user input)
        password_input = self.set_password_field.text()
        confirm_password_input = self.confirm_password_field.text()

        # Checking if all fields are filled
        if len(user_text) == 0 or len(password_input) == 0 or len(confirm_password_input) == 0:
            self.error_label.setText("Please fill in all inputs!")

        # Checking if passwords match
        elif password_input != confirm_password_input:
            self.error_label.setText("Passwords do not match!")

        # Validate if username is already taken by another user before creating entries on the database
        else:
            if check_username_exists('users.db', 'login_information', user_text):
                self.msg = QMessageBox()
                self.msg.setWindowTitle("Error")
                self.msg.setText("Username already exists, please choose another one")
                self.msg.exec_()

            # Creating a database to store new user's tasks
            else:
                insert_user_db('login_information', user_text, password_input)
                create_tasks_table(user_text)
                global created_user
                created_user = user_text
                self.msg.setWindowTitle("Account Created!")
                self.msg.setText("Your account has been created")
                self.msg.exec_()
                self.close()

                # Returning to the login page
                go_to_login()


def go_to_tasks():
    """Redirects user to tasks page."""
    tasks = UI()
    widget.addWidget(tasks)
    widget.setCurrentIndex(widget.currentIndex() + 1)


def go_to_create():
    """Redirects user to Create Account page."""
    create = CreateAccount()
    widget.addWidget(create)
    widget.setCurrentIndex(widget.currentIndex() + 1)


class LoginForm(QWidget):
    """GUI class for the Login Form window."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login Form")
        self.resize(500, 120)

        # Creates grid layout and adds elements manually (without *.ui file)
        layout = QGridLayout()
        label_name = QLabel("<font size='4'> Username </font>")
        self.lineEdit_username = QLineEdit()
        self.lineEdit_username.setPlaceholderText("Please enter your username")
        layout.addWidget(label_name, 0, 0)
        layout.addWidget(self.lineEdit_username, 0, 1)

        label_password = QLabel("<font size='4'> Password</font>")
        self.lineEdit_password = QLineEdit()
        self.lineEdit_password.setPlaceholderText("Please enter your password")
        self.lineEdit_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(label_password, 1, 0)
        layout.addWidget(self.lineEdit_password, 1, 1)

        button_login = QPushButton("Login")
        button_login.clicked.connect(self.check_password)
        layout.addWidget(button_login, 2, 0, 1, 3)

        button_create_account = QPushButton("Create Account")
        button_create_account.clicked.connect(go_to_create)
        layout.addWidget(button_create_account, 3, 0, 1, 3)
        self.setLayout(layout)

    def get_logged_user(self):
        """Retrieves the logged or the recently created user to search on the database and retrieve password."""
        global logged_user
        global created_user
        if created_user != "":
            self.lineEdit_username.setText(created_user)
        logged_user = self.lineEdit_username.text()

    def check_password(self):
        """Checks if the password is valid."""
        msg = QMessageBox()
        login.get_logged_user()
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()

        cur.execute(f"SELECT user_password FROM login_information WHERE username_id = '{logged_user}'")
        if not check_username_exists('users.db', 'login_information', logged_user):
            msg.setText("User not found. Please create an account or try again later")
            msg.setWindowTitle("Incorrect user!")
            msg.exec_()
            quit()

        stored_password = cur.fetchone()[0]
        conn.commit()
        if self.lineEdit_password.text() == stored_password:
            msg.setText("Welcome back, {}!".format(str(self.lineEdit_username.text())))
            msg.setWindowTitle("Login successful!")
            msg.exec_()

            go_to_tasks()

        else:
            msg.setText("Incorrect password!")
            msg.setWindowTitle("Wrong credentials!")
            msg.exec_()


class UI(QMainWindow):
    """ GUI class: Main window of the To-do app"""
    def __init__(self):
        super().__init__()

        # Load UI file
        uic.loadUi("to_do.ui", self)
        self.setFixedSize(409, 515)

        # Message pop ur box
        self.msg = QMessageBox()
        self.msg.setWindowTitle("Saved to Database!")
        self.msg.setText("Your Todo List has been successfully saved!")
        self.msg.setIcon(QMessageBox.Information)

        # Define widgets: make reference to the widget type and name found on *.ui file
        self.create_task_label = self.findChild(QLabel, "createtask_label")
        self.ongoing_tasks_label = self.findChild(QLabel, "ongoingtasks_label")
        self.lineedit = self.findChild(QLineEdit, "lineEdit")
        self.add_button = self.findChild(QPushButton, "additem_pushButton")
        self.delete_button = self.findChild(QPushButton, "deleteitem_pushButton_2")
        self.clear_button = self.findChild(QPushButton, "clearall_pushButton_3")
        self.list_widget = self.findChild(QListWidget, "mylist_listWidget")
        self.save_button = self.findChild(QPushButton, "save_pushButton_4")

        # Creating Functionality (linking the action - button clicked - to the function that defines what will be done)
        self.add_button.clicked.connect(self.add_item)
        self.delete_button.clicked.connect(self.delete_item)
        self.clear_button.clicked.connect(self.clear_all)
        self.save_button.clicked.connect(self.save_it)

        # Grab all items from database
        self.grab_all()

        # Show the app
        self.show()

    def add_item(self):
        """Adds task to the to-do list"""
        item = self.lineedit.text()
        self.list_widget.addItem(item)
        self.lineedit.setText("")

    def delete_item(self):
        """Deletes item from the to-do list."""
        selection = self.list_widget.currentRow()
        self.list_widget.takeItem(selection)

    def clear_all(self):
        """Clears all items from the to-do list."""
        self.list_widget.clear()

    def save_it(self):
        """Saves the to-do list to the database."""
        conn = sqlite3.connect('tasks_db.db')
        cur = conn.cursor()

        # Store all tasks in a list
        items = [self.list_widget.item(i) for i in range(self.list_widget.count())]

        # Delete all items currently in database to avoid duplicates
        cur.execute(f"DELETE FROM {logged_user};", )

        for item in items:
            # Add items to table
            cur.execute(f"INSERT INTO {logged_user} VALUES (:item)",
                        {
                            'item': item.text(),
                        })
        conn.commit()
        conn.close()
        self.msg.exec_()

    def grab_all(self):
        """Retrieves all data currently on database to show on screen."""
        conn = sqlite3.connect('tasks_db.db')

        cur = conn.cursor()

        cur.execute(f"SELECT * FROM '{logged_user}'")
        records = cur.fetchall()

        conn.commit()
        conn.close()

        # Loop through records to add to screen
        for record in records:
            self.list_widget.addItem(str(record[0]))


# Initialize the app
app = QApplication(sys.argv)
login = LoginForm()

widget = QtWidgets.QStackedWidget()
widget.addWidget(login)
widget.show()
app.exec_()