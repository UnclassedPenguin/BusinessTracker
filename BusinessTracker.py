#!/bin/usr/env python3

'''
Copyright © 2018 UnclassedPenguin
Author: UnclassedPenguin
App: Business Tracker
Description: keep track of your Business 
'''

import os
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox, QMenuBar, \
    QWidget,QScrollArea, QTableWidget, QVBoxLayout,QTableWidgetItem, QAction
from PyQt5.QtWidgets import QApplication
from datetime import datetime
import pandas as pd
import sqlite3
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
database = config['DEFAULT']['database']
businessname = config['DEFAULT']['name']
import mainwindow, searchexpenseswindow, searchincomewindow, printwindow, tablewindow, addtypedialog


class BusinessTracker(QtWidgets.QMainWindow, mainwindow.Ui_MainWindow):

    def __init__(self, parent=None):
        super(BusinessTracker, self).__init__()
        self.setupUi(self)
        self.dialogs = []

        self.initial_config()
        self.button_config()
        self.overallbalance()

    def initial_config(self):
        self.create_tables()
        self.type_setup()
        self.label.setText(businessname)
        self.label_7.setText(businessname)
        self.label_8.setText(businessname)
        self.dateLabel.setText(datetime.now().strftime("%a %b %d, %Y"))
        self.dateLabel_2.setText(datetime.now().strftime("%a %b %d, %Y"))
        self.dateLabel_3.setText(datetime.now().strftime("%a %b %d, %Y"))
        self.dateEdit.setDateTime(QtCore.QDateTime.currentDateTime())
        self.dateEdit_2.setDateTime(QtCore.QDateTime.currentDateTime())

    def button_config(self):
        #Summary Tab
        self.testButton_3.clicked.connect(self.test2Function)

        #Add Expense Tab
        self.addexpenseButton.clicked.connect(self.addexpense_Button)
        self.clearButton.clicked.connect(self.clearExpenses)
        self.searchexpensesButton.clicked.connect(self.goto_searchexpenseswindow)
        self.testButton.clicked.connect(self.testFunction)
        self.displayallButton.clicked.connect(self.displayall_Expenses)
        self.addtypeButton.clicked.connect(self.get_Expensetype)

        #Add Income Tab
        self.addincomeButton.clicked.connect(self.addincome_Button)
        self.clearButton_2.clicked.connect(self.clearIncome)
        self.searchincomeButton.clicked.connect(self.goto_searchincomewindow)
        self.testButton_2.clicked.connect(self.testFunction)
        self.displayallButton_2.clicked.connect(self.displayall_Income)
        self.addtypeButton_2.clicked.connect(self.get_Incometype)

        #Other 
        self.quitButton.clicked.connect(self.close)
        self.quitButton_2.clicked.connect(self.close)
        self.quitButton_3.clicked.connect(self.close)

    def create_tables(self):
        conn = sqlite3.connect(database)
        curs = conn.cursor()
        curs.execute('''create table if not exists Expenses 
                   (numid integer primary key, date, type, item, price, notes)''')
        curs.execute('''create table if not exists Income
                   (numid integer primary key, date, type, item, price,  notes)''')
        '''
        curs.execute("create unique index if not exists" \
                     " numidx_expenses_name on Expenses (item);")
        curs.execute("create unique index if not exists" \
                     " numidx_income_name on Income (item);")
        '''
        conn.commit()
        conn.close()

    def type_setup(self):
        print('\n')
        print("==== def type_setup(self): ====")
        global database
        conn = sqlite3.connect(database)
        curs = conn.cursor()
        curs.execute('CREATE TABLE IF NOT EXISTS type (numid integer primary key, expensetype, incometype)')
        curs.execute("create unique index if not exists" \
                     " numidx_type_name on type (expensetype);")
        curs.execute("create unique index if not exists" \
                     " numidx_type2_name on type (incometype);")
        curs.execute('INSERT INTO type (expensetype) values("Misc");')
        curs.execute('INSERT INTO type (incometype) values("Misc");')
        curs.execute('SELECT expensetype FROM type')
        dirtyexpensetype = curs.fetchall()
        self.expensetype = []
        self.expensetype = list(sum(dirtyexpensetype, ()))
        self.expensetype = list(filter((None).__ne__, self.expensetype))
        self.expensetype.sort()
        print("Clean expense types: {}".format(self.expensetype))
        self.expensetypeBox.clear()
        self.expensetypeBox.addItems(self.expensetype)
        curs.execute('SELECT incometype FROM type')
        dirtyincometype = curs.fetchall()
        self.incometype = []
        self.incometype = list(sum(dirtyincometype, ()))
        self.incometype = list(filter((None).__ne__, self.incometype))
        self.incometype.sort()
        print("Clean income types: {}".format(self.incometype))
        self.incometypeBox.clear()
        self.incometypeBox.addItems(self.incometype)
        conn.close()
        print('\n')

    def get_Expensetype(self):
        expensetype = addtypePage()
        if expensetype.exec_():
            self.add_Expensetype(expensetype.newtypeEntry.text())

    def get_Incometype(self):
        incometype = addtypePage()
        if incometype.exec_():
            self.add_Incometype(incometype.newtypeEntry.text())

    def add_Expensetype(self, typetoenter):
        print('\n')
        print('==== def add_ExpenseType(self, typetoenter): ====')
        global database
        conn = sqlite3.connect(database)
        curs = conn.cursor()
        print("Newgroup: {}".format(typetoenter))
        if len(typetoenter) > 0:
            controlv = typetoenter
            print("Updating Expense Type List...")
            curs.execute("REPLACE INTO type (expensetype) VALUES (?) ", (controlv,))
            conn.commit()
            self.msg('info', 'Info', '', 'Type Added')
        conn.close()
        self.type_setup()
        print('\n')

    def add_Incometype(self, typetoenter):
        print('\n')
        print('==== def add_incomeType(self, typetoenter): ====')
        global database
        conn = sqlite3.connect(database)
        curs = conn.cursor()
        print("Newgroup: {}".format(typetoenter))
        if len(typetoenter) > 0:
            controlv = typetoenter
            print("Updating Income Type List...")
            curs.execute("REPLACE INTO type (incometype) VALUES (?) ", (controlv,))
            conn.commit()
            self.msg('info', 'Info', '', 'Type Added')
        conn.close()
        self.type_setup()
        print('\n')

    def clearExpenses(self):
        self.itemEdit.setText('')
        self.priceEdit.setValue(0)
        self.notesEdit.setText('')

    def clearIncome(self):
        self.itemEdit_2.setText('')
        self.priceEdit_2.setValue(0)
        self.notesEdit_2.setText('')

##############################
######### Summary Tab ########
##############################

    def overallbalance(self):
        print('\n')
        print("==== def balance(self): ====")
        global database
        conn = sqlite3.connect(database)
        curs = conn.cursor()
        curs.execute('''select price from Expenses''')
        dirtyexpenses = curs.fetchall()
        curs.execute('''select price from Income''')
        dirtyincome = curs.fetchall()

        expenses = []
        expenses = list(sum(dirtyexpenses, ()))
        expenses = [float(i) for i in expenses]
        income = []
        income = list(sum(dirtyincome, ()))
        income = [float(i) for i in income]

        print("Expenses: {}".format(expenses))
        print("Income: {}".format(income))

        sumexpenses = sum(expenses)
        sumincome = sum(income)

        overallbalance = sumincome + -(sumexpenses)
        overallbalance = f'{overallbalance:.2f}'

        conn.close()

        self.balanceLabel.setText("{}".format(overallbalance))
        self.totalexpenseLabel.setText("{}".format(f'{sumexpenses:.2f}'))
        self.totalincomeLabel.setText("{}".format(f'{sumincome:.2f}'))

        if float(overallbalance) <= 0:
            self.balanceLabel.setStyleSheet('color: red')
        elif float(overallbalance) > 0:
            self.balanceLabel.setStyleSheet('color: green')

        return expenses, income
        print('\n')

##############################
####### End Summary Tab ######
##############################


##############################
####### Add Expense Tab ######
##############################

    def addexpense_Button(self):
        print('\n')
        print("==== def addexpense_Button(self): ====")
        global database
        #global counter

        try:
            if len(self.itemEdit.text()) == 0 or len(self.priceEdit.text()) == 0:
                print("Doesn't work!")
                self.msg('crit', 'Error', 'Save Error', 'Please enter item and price')
            else:
                currentdate = datetime.now().strftime('%Y-%m-%d')
                date = self.dateEdit.date().toPyDate()
                expensetype = self.expensetypeBox.currentText()
                item = self.itemEdit.text()
                price = self.priceEdit.text()
                notes = self.notesEdit.text()
                print("Date: {}".format(date))
                print("Type: {}".format(expensetype))
                print("Item: {}".format(item))
                print("Price: {}".format(price))
                print("Notes: {}".format(notes))

                data = (date, expensetype, item, price, notes)

                conn = sqlite3.connect(database)
                curs = conn.cursor()
                curs.execute('''INSERT INTO Expenses(date, type, item, price, notes) VALUES(?,?,?,?,?)''', data)
                conn.commit()
                conn.close()
                self.overallbalance()
        except:
            self.msg('crit', 'Error', 'Save Error', 'Please use a different name, its taken')
        print('\n')

    def displayall_Expenses(self):
        conn = sqlite3.connect(database)
        curs = conn.cursor()

        templist = ['Date', 'Type', 'Item', 'Price', 'Notes']

        self.sql = "SELECT date, type, item, price, notes from Expenses"
        x = pd.read_sql_query(self.sql, conn)
        y=x.sort_values(by=['date'])
        self.window = DisplayPage()
        df = y
        self.window.table.setColumnCount(len(df.columns))
        self.window.table.setRowCount(len(df.index))
        self.window.table.setHorizontalHeaderLabels(templist)
        for i in range(len(df.index)):
            for j in range(len(df.columns)):
                self.window.table.setItem(i,j,QTableWidgetItem\
                                          (str(df.iloc[i, j])))
        self.window.table.setWordWrap(True)
        self.window.table.resizeRowsToContents()
        self.window.table.resizeColumnsToContents()
        self.window.show()
        conn.close()

##############################
##### End Add Expense Tab ####
##############################


##############################
####### Add Income Tab #######
##############################

    def addincome_Button(self):
        print('\n')
        print("==== def addincome_Button(self): ====")
        global database

        try:
            if len(self.itemEdit_2.text()) == 0 or len(self.priceEdit_2.text()) == 0:
                print("Doesn't work!")
                self.msg('crit', 'Error', 'Save Error', 'Please enter item and price')
            else:
                currentdate = datetime.now().strftime('%Y-%m-%d')
                date = self.dateEdit_2.date().toPyDate()
                incometype = self.incometypeBox.currentText()
                item = self.itemEdit_2.text()
                price = self.priceEdit_2.text()
                notes = self.notesEdit_2.text()
                print("Date: {}".format(date))
                print("Type: {}".format(incometype))
                print("Item: {}".format(item))
                print("Price: {}".format(price))
                print("Notes: {}".format(notes))

                data = (date, incometype, item, price, notes)

                conn = sqlite3.connect(database)
                curs = conn.cursor()
                curs.execute('''INSERT INTO Income(date, type, item, price, notes) VALUES(?,?,?,?,?)''', data)
                conn.commit()
                conn.close()

            self.overallbalance()
        except:
            self.msg('crit', 'Error', 'Save Error', 'Please use a different name, its taken')

        print('\n')

    def displayall_Income(self):
        conn = sqlite3.connect(database)
        curs = conn.cursor()

        templist = ['Date', 'Type', 'Item', 'Price', 'Notes']

        self.sql = "SELECT date, type, item, price, notes from Income"
        x = pd.read_sql_query(self.sql, conn)
        y=x.sort_values(by=['date'])
        self.window = DisplayPage()
        df = y
        self.window.table.setColumnCount(len(df.columns))
        self.window.table.setRowCount(len(df.index))
        self.window.table.setHorizontalHeaderLabels(templist)
        for i in range(len(df.index)):
            for j in range(len(df.columns)):
                self.window.table.setItem(i,j,QTableWidgetItem\
                                          (str(df.iloc[i, j])))
        self.window.table.setWordWrap(True)
        self.window.table.resizeRowsToContents()
        self.window.table.resizeColumnsToContents()
        self.window.show()
        conn.close()

##############################
##### End Add Income Tab #####
##############################

##############################
####### misc functions #######
##############################

    def msg(self, messagetype, messagetitle, infotext, messagetext):
        if messagetype == 'info':
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText(infotext)
            msg.setInformativeText(messagetext)
            msg.setWindowTitle(messagetitle)
            msg.exec()
        if messagetype == 'crit':
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText(infotext)
            msg.setInformativeText(messagetext)
            msg.setWindowTitle(messagetitle)
            msg.exec()
        if messagetype == "":
            msg = QtWidgets.QMessageBox()
            msg.setText(infotext)
            msg.setInformativeText(messagetext)
            msg.setWindowTitle(messagetitle)
            msg.exec()

    def testFunction(self):
        print("Hello there")

    def test2Function(self):
        price = self.doubleSpinBox.text()
        print(price)
        print(type(price))

    def goto_searchexpenseswindow(self):
        dialog = searchexpenseswindow(self)
        self.dialogs.append(dialog)
        dialog.show()

    def goto_searchincomewindow(self):
        dialog = searchincomewindow(self)
        self.dialogs.append(dialog)
        dialog.show()

class addtypePage(QtWidgets.QDialog, addtypedialog.Ui_Dialog):

    def __init__(self, parent=None):
        super(addtypePage, self).__init__()
        self.setupUi(self)

class searchexpenseswindow(QtWidgets.QMainWindow, searchexpenseswindow.Ui_MainWindow):

    def __init__(self,  parent=None):
        super(searchexpenseswindow, self).__init__()
        self.setupUi(self)
        self.dialogs = []

        self.initial_Config()

        self.searchdateButton.clicked.connect(self.search_Date)
        self.searchtypeButton.clicked.connect(self.search_Type)
        self.quit2Button.clicked.connect(self.close)
        self.dateEdit.setDateTime(QtCore.QDateTime.currentDateTime())

    def initial_Config(self):
        global database
        conn = sqlite3.connect(database)
        curs = conn.cursor()

        curs.execute('SELECT expensetype FROM type')
        dirtyexpensetype = curs.fetchall()
        self.expensetype = []
        self.expensetype = list(sum(dirtyexpensetype, ()))
        self.expensetype = list(filter((None).__ne__, self.expensetype))
        self.expensetype.sort()
        print("Clean expense types: {}".format(self.expensetype))
        self.typeBox.clear()
        self.typeBox.addItems(self.expensetype)

        conn.close()

    def search_Type(self):
        print("\n")
        print("==== def search_Type(self): ====")

        global database
        conn = sqlite3.connect(database)
        curs = conn.cursor()

        templist = ['Date', 'Type', 'Item', 'Price', 'Notes']
        expensetype = self.typeBox.currentText()
        print(expensetype)
        self.sql = "SELECT date, type, item, price, notes from Expenses where type IS " + "'" + \
                    expensetype + "'"
        print(self.sql)
        x = pd.read_sql_query(self.sql, conn)
        x.index = x.index + 1
        if isinstance(x, pd.core.frame.DataFrame):
            self.window = DisplayPage()
            df = x
            self.window.table.setColumnCount(len(df.columns))
            self.window.table.setRowCount(len(df.index))
            self.window.table.setHorizontalHeaderLabels(templist)
            for i in range(len(df.index)):
                for j in range(len(df.columns)):
                    self.window.table.setItem(i,j,QTableWidgetItem(str(df.iloc[i, j])))
            self.window.table.setWordWrap(True)
            self.window.table.resizeRowsToContents()
            self.window.table.resizeColumnsToContents()
            self.window.show()
        elif isinstance(self.y, pd.core.frame.DataFrame) == False:
            pass

        conn.close()

        print("\n")

    def search_Date(self):
        print("\n")
        print("==== def search_Date(self): ====")

        global database
        conn = sqlite3.connect(database)
        curs = conn.cursor()

        templist = ['Date', 'Type', 'Item', 'Price', 'Notes']
        date = str(self.dateEdit.date().toPyDate())
        self.sql = "SELECT date, type, item, price, notes from Expenses where date IS " + "'" + \
                    date + "'"
        print(self.sql)
        x = pd.read_sql_query(self.sql, conn)
        x.index = x.index + 1
        if isinstance(x, pd.core.frame.DataFrame):
            self.window = DisplayPage()
            df = x
            self.window.table.setColumnCount(len(df.columns))
            self.window.table.setRowCount(len(df.index))
            self.window.table.setHorizontalHeaderLabels(templist)
            for i in range(len(df.index)):
                for j in range(len(df.columns)):
                    self.window.table.setItem(i,j,QTableWidgetItem(str(df.iloc[i, j])))
            self.window.table.setWordWrap(True)
            self.window.table.resizeRowsToContents()
            self.window.table.resizeColumnsToContents()
            self.window.show()
        elif isinstance(self.y, pd.core.frame.DataFrame) == False:
            pass

        conn.close()

        print("\n")


class searchincomewindow(QtWidgets.QMainWindow, searchincomewindow.Ui_MainWindow):

    def __init__(self,  parent=None):
        super(searchincomewindow, self).__init__()
        self.setupUi(self)
        self.dialogs = []

        self.initial_Config()

        self.searchdateButton.clicked.connect(self.search_Date)
        self.searchtypeButton.clicked.connect(self.search_Type)
        self.quit2Button.clicked.connect(self.close)
        self.dateEdit.setDateTime(QtCore.QDateTime.currentDateTime())

    def initial_Config(self):
        global database
        conn = sqlite3.connect(database)
        curs = conn.cursor()

        curs.execute('SELECT incometype FROM type')
        dirtyincometype = curs.fetchall()
        self.incometype = []
        self.incometype = list(sum(dirtyincometype, ()))
        self.incometype = list(filter((None).__ne__, self.incometype))
        self.incometype.sort()
        print("Clean income types: {}".format(self.incometype))
        self.typeBox.clear()
        self.typeBox.addItems(self.incometype)
        conn.close()

    def search_Type(self):
        print("\n")
        print("==== def search_Type(self): ====")

        global database
        conn = sqlite3.connect(database)
        curs = conn.cursor()

        templist = ['Date', 'Type', 'Item', 'Price', 'Notes']
        incometype = self.typeBox.currentText()
        print(incometype)
        self.sql = "SELECT date, type, item, price, notes from Income where type IS " + "'" + \
                    incometype + "'"
        print(self.sql)
        x = pd.read_sql_query(self.sql, conn)
        x.index = x.index + 1
        if isinstance(x, pd.core.frame.DataFrame):
            self.window = DisplayPage()
            df = x
            self.window.table.setColumnCount(len(df.columns))
            self.window.table.setRowCount(len(df.index))
            self.window.table.setHorizontalHeaderLabels(templist)
            for i in range(len(df.index)):
                for j in range(len(df.columns)):
                    self.window.table.setItem(i,j,QTableWidgetItem(str(df.iloc[i, j])))
            self.window.table.setWordWrap(True)
            self.window.table.resizeRowsToContents()
            self.window.table.resizeColumnsToContents()
            self.window.show()
        elif isinstance(self.y, pd.core.frame.DataFrame) == False:
            pass

        conn.close()

        print("\n")

    def search_Date(self):
        print("\n")
        print("==== def search_Date(self): ====")

        global database
        conn = sqlite3.connect(database)
        curs = conn.cursor()

        templist = ['Date', 'Type', 'Item', 'Price', 'Notes']
        date = str(self.dateEdit.date().toPyDate())
        self.sql = "SELECT date, type, item, price, notes from Income where date IS " + "'" + \
                    date + "'"
        print(self.sql)
        x = pd.read_sql_query(self.sql, conn)
        x.index = x.index + 1
        if isinstance(x, pd.core.frame.DataFrame):
            self.window = DisplayPage()
            df = x
            self.window.table.setColumnCount(len(df.columns))
            self.window.table.setRowCount(len(df.index))
            self.window.table.setHorizontalHeaderLabels(templist)
            for i in range(len(df.index)):
                for j in range(len(df.columns)):
                    self.window.table.setItem(i,j,QTableWidgetItem(str(df.iloc[i, j])))
            self.window.table.setWordWrap(True)
            self.window.table.resizeRowsToContents()
            self.window.table.resizeColumnsToContents()
            self.window.show()
        elif isinstance(self.y, pd.core.frame.DataFrame) == False:
            pass

        conn.close()

        print("\n")


class DisplayPage(QtWidgets.QMainWindow, tablewindow.Ui_MainWindow):

    def __init__(self, parent=None):
        super(DisplayPage, self).__init__()
        self.widget = QWidget()
        self.setupUi(self)

class printpage(QtWidgets.QMainWindow, printwindow.Ui_MainWindow):

    def __init__(self, parent=None):
        super(printpage, self).__init__()
        self.widget = QWidget()
        self.setupUi(self)
        self.closeButton.clicked.connect(self.close)


def main():
    app = QApplication(sys.argv)
    main = BusinessTracker()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
