from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

( Ui_MainWindow, QMainWindow) = uic.loadUiType( 'mainwindow.ui' )

#Import Equipment Window (before logging so we dont log for Qt)
from bin.EquipmentWindow import EquipmentWindow 

# Log everything, and send it to file.
import logging 
logging.basicConfig(level=logging.DEBUG, filename='guredo_debug.log')

#Import my Student class, and ordinal (st, nd, rd, th) helper
from ClassStudents import ClassStudents, ordinal
import os, csv, shutil

from datetime import datetime


class MainWindow ( QMainWindow ):
    """MainWindow inherits QMainWindow"""

    def __init__ ( self, parent = None ):
        """Initialize GUI, setup student object and database"""
        #pyqt boiler plate
        QMainWindow.__init__( self, parent )
        self.ui = Ui_MainWindow()
        self.ui.setupUi( self )
        
        #Connect Add/Update button to slot
        self.ui.pushButton.clicked.connect(self.add_update)
        self.ui.pushButton_clear.clicked.connect(self.clear_delete)
        
        #Connect Export Certificate
        self.ui.pushButton_certificate.clicked.connect(self.export_certificate)
        
        #Connect Export Report
        self.ui.pushButton_report.clicked.connect(self.export_report)
        
        #Connect Export Belts
        self.ui.pushButton_belts.clicked.connect(self.export_belts)
        
        
        
        
        #Remove edit function from table until I go pro
        self.ui.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.tableWidget.setColumnWidth(0,200)
        self.ui.tableWidget.setColumnWidth(1,150)
        #Hide id column
        self.ui.tableWidget.setColumnHidden(7,True)
        #Connect table view row select to slot
        self.ui.tableWidget.cellClicked.connect(self.select_student)
        
        try:
            self.students = ClassStudents()
            #Create a database file if non-existant
            self.students.create_tables()

            #Select todays students from sqlite3, fill table
            self.refresh_table()
            
            #Fake a dojo list
            dojos = self.students.DOJOS
            for dojo in dojos:
                self.ui.comboBoxDojo.addItem(dojo)
            
            #Populate the grading selectbox, so that historical gradings can be viewed
            dates = self.students.select_dates()
            self.ui.comboBoxDates.addItem(self.students.DATE)
            for date in dates:
                self.ui.comboBoxDates.addItem(date['Date'])
            
            #Connect Date selector to slot
            self.ui.comboBoxDates.currentIndexChanged.connect(self.change_date)
            #Connect Grade and BeltPaid selector to slot
            self.ui.comboBoxGrade.currentIndexChanged.connect(self.change_grade)
            self.ui.comboBoxBeltPaid.currentIndexChanged.connect(self.change_grade)
            
            #Force Fee Update
            self.change_grade()
            
            #Temp code to open second window
            self.EquipmentWindow = EquipmentWindow()
            #Connect Equipment to new window
            self.ui.pushButton_equipment.clicked.connect(self.EquipmentWindow.open)
            #dialog.ui = EquipmentWindow()
            #dialog.ui.setupUi(dialog)
            #dialog.setAttribute(WA_DeleteOnClose)
            #dialog.open()
            
        except Exception as e:
            #Handle init errors, log and report to user
            errorDialog = QErrorMessage(self)
            errorDialog.showMessage("App Init Error: "+ str(e))
            logging.exception("App Init Error: ")
    
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Return or  key == Qt.Key_Enter: 
            self.add_update()
        
    def __del__ ( self ):
        self.ui = None
    
    def refresh_table(self):
        """Method to reload the student data table"""
        list = self.students.list_student()
        #Edit tableWidget to have correct amount of rows
        self.ui.tableWidget.setRowCount(len(list))
        
        #Edit tableWidget sorting disabled, re enable after fill
        self.ui.tableWidget.setSortingEnabled(False)
        
        gfee, bfee, adults, kids = 0.00,0.00,0,0
        
        if list:
            #Populate the tableWidget
            for r, row in enumerate(list):
                c = 0
                for key, value in zip(row.keys(), row):
                    #logic for 1st, 2nd, 3rd ordinal ending
                    if key == 'Grade':
                        try:
                            if row['Paid'] == 1:
                                gfee += self.students.FEES[str(value)]
                            
                            if value == 0:
                                value = 'Shodan Ho'
                            else:
                                unit = 'Kyu'
                                if value < 1:
                                    unit = 'Dan'
                                value = str(ordinal(value)+' '+unit)
                        except:
                            logging.debug('Grade to text conversion error')
                            value = ''
                    
                    #use exception to test value is int - Python exceptions fast
                    if key == 'Belt':
                        try:
                            int(value)
                        except:
                            value = ''
                    
                    if key == 'Type' and value == 'Adult':
                        adults += 1
                    elif key == 'Type':
                        kids += 1
                        
                    
                    #logic for converting boolean to english
                    if key in ['Paid', 'BeltPaid']:
                        if value == 1:
                            value = 'Yes'
                            if key == 'BeltPaid':
                                bfee += self.students.BELTFEE
                        elif value == 3:
                            value = 'Reattempt'
                        else:
                            value = 'No'
                            

                    #create table cell and add to table
                    item = QTableWidgetItem(str(value))
                    self.ui.tableWidget.setItem(r, c, item)
                    c += 1
        self.ui.tableWidget.setSortingEnabled(True)
        
        #Update counters
        self.ui.label_gfee.setText("${:,.2f}".format(gfee))
        self.ui.label_bfee.setText("${:,.2f}".format(bfee))
        self.ui.label_fees.setText("${:,.2f}".format(gfee+bfee))
        self.ui.label_kids.setText(str(kids))
        self.ui.label_adults.setText(str(adults))
        self.ui.label_total.setText(str(kids+adults))

        
    def clear_form (self):
        """Method to clear the data entry form, and reset for next entry"""
        self.ui.inputName.clear()
        self.ui.inputName.selectAll()
        self.ui.inputName.setFocus()
        

        self.ui.comboBoxGrade.setCurrentIndex(0)
        self.ui.comboBoxBeltSize.setCurrentIndex(0)
        
        self.ui.comboBoxDojo.setCurrentIndex(0)
        self.ui.comboBoxPaid.setCurrentIndex(0)
        self.ui.comboBoxBeltPaid.setCurrentIndex(0)
        
        #Force Fee Update
        self.change_grade()
        
        
    def add_update (self):
        """Qt Slot for handling the primary app button, which will alternate between Add / Save"""

        #convert booleans
        paid, beltpaid = 0, 0
        if self.ui.comboBoxPaid.currentText() == 'Yes':
            paid = 1
        if self.ui.comboBoxPaid.currentText() == 'Reattempt':
            paid = 2
        if self.ui.comboBoxBeltPaid.currentText() == 'Yes':
            beltpaid = 1
        
        #exception test inputs are integers
        grade = str(str(self.ui.comboBoxGrade.currentText()))
        try:
            int(grade)
        except:
            grade = ''
        belt = str(str(self.ui.comboBoxBeltSize.currentText()))
        try:
            int(belt)
        except:
            belt = ''
        
        #assemble data structure to go in DB
        form = {'Date':self.students.DATE, 'Name':str(self.ui.inputName.text()), 
                'Dojo':str(self.ui.comboBoxDojo.currentText()), 'Type':str(self.ui.comboBoxType.currentText()), 
                'Grade':grade, 'Belt':belt, 'Paid':paid, 'BeltPaid':beltpaid}
        
        if self.ui.pushButton.text() == 'Add':
            self.students.add_student(form)
        else:
            self.students.update_student(form, id = self.students.id)
        
        #clean up form after add
        self.refresh_table()
        self.students.id = None
        self.clear_form()
        
        #Update Buttons to Add / Clear
        self.ui.pushButton.setText('Add')
        self.ui.pushButton_clear.setText('Clear')
        
    
    def clear_delete (self):
        if self.ui.pushButton_clear.text() == 'Clear':
            self.clear_form()
        else:
            #Code to delete an entry
            self.students.delete_student(self.students.id)
            self.students.id = None
            self.clear_form()
            self.refresh_table()
        self.ui.pushButton.setText('Add')
        self.ui.pushButton_clear.setText('Clear')
    
    def change_date (self):
        """Qt Slot for handling the date selector to view previous gradings"""
        self.students.selecteddate = str(self.ui.comboBoxDates.currentText())
        logging.debug(self.students.selecteddate)
        self.refresh_table()
    
    def change_grade (self):
        """Qt Slot for handling the date selector to view previous gradings"""
        #Update due
        try:
            self.ui.label_due.setText("${:,.2f}".format(self.students.FEES[str(self.ui.comboBoxGrade.currentText())]))
        except:
            self.ui.label_due.setText("Grade ERROR")
            
        try:
            fee = self.students.FEES[str(self.ui.comboBoxGrade.currentText())]
            if self.ui.comboBoxBeltPaid.currentText() == 'Yes':
                bfee = self.students.BELTFEE
            else:
                bfee = 0.00
            self.ui.label_gdue.setText("${:,.2f}".format(fee))
            self.ui.label_bdue.setText("${:,.2f}".format(bfee))
            self.ui.label_due.setText("${:,.2f}".format(fee+bfee))
        except:
            self.ui.label_gdue.setText("Grade ERROR")
        
    
    def select_student (self):
        #Get sql id of person we are after
        self.students.id = str(self.ui.tableWidget.item(self.ui.tableWidget.currentRow(),7).text())
        
        student = self.students.list_student(id=self.students.id)
        
        #Update form inputs
        self.ui.inputName.setText(student['Name'])
        #self.ui.inputGrade.setText(str(student['Grade']))
        #self.ui.inputBeltSize.setText(str(student['Belt']))
        
        c = self.ui.comboBoxGrade.findText(str(student['Grade']))
        self.ui.comboBoxGrade.setCurrentIndex(c)
        c = self.ui.comboBoxBeltSize.findText(str(student['Belt']))
        self.ui.comboBoxBeltSize.setCurrentIndex(c)
        
        #Update form combo boxes dojo
        c = self.ui.comboBoxDojo.findText(student['Dojo'])
        self.ui.comboBoxDojo.setCurrentIndex(c)
        
        #Update form combo boxes type
        c = self.ui.comboBoxType.findText(student['Type'])
        self.ui.comboBoxType.setCurrentIndex(c)
        
        if student['Paid']==1:
            c = self.ui.comboBoxPaid.findText('Yes')
        elif student['Paid']==2:
            c = self.ui.comboBoxPaid.findText('Reattempt')
        else:
            c = self.ui.comboBoxPaid.findText('No')
        self.ui.comboBoxPaid.setCurrentIndex(c)
        
        if student['BeltPaid']==1:
            c = self.ui.comboBoxBeltPaid.findText('Yes')
            bfee = self.students.BELTFEE
        else:
            c = self.ui.comboBoxBeltPaid.findText('No')
            bfee = 0.00
        self.ui.comboBoxBeltPaid.setCurrentIndex(c)
        
        #Update due
        try:
            fee = self.students.FEES[str(student['Grade'])]
            self.ui.label_gdue.setText("${:,.2f}".format(fee))
            self.ui.label_bdue.setText("${:,.2f}".format(bfee))
            self.ui.label_due.setText("${:,.2f}".format(fee+bfee))
        except:
            self.ui.label_gdue.setText("Grade ERROR")
        
        #Update Buttons to Delete / Update
        self.ui.pushButton.setText('Update')
        self.ui.pushButton_clear.setText('Delete')
        
    def export_certificate(self):
        """Logic to ui select student type, generate csv of result, and copy/launch mailmerge template"""
        type, ok = QInputDialog.getItem(self, "Export which entries", "Type:", ['Adult','Child'], 0, False)
        if ok:
            list = self.students.list_student(type=str(type))
            with open('export/certificate_export.csv', 'wb') as csvfile:
                w = csv.writer(csvfile, dialect='excel')
                w.writerow(['Name','Grade','+'])
                for student in list:
                    w.writerow([student['Name'],student['grade'],str(ordinal(student['grade'])).replace(str(student['grade']),'')])
            shutil.copy('template/template.docx', 'export/template.docx')
            try:
                os.startfile('export\\template.docx', 'open')
            except:
                #This will make the above windows command work on linux for dev testing
                import webbrowser
                webbrowser.open('export/template.docx')
        
    def export_report(self):
            students = self.students.list_student()
            with open('export/report_export.csv', 'wb') as csvfile:
                w = csv.writer(csvfile, dialect='excel')
                #w.writerow(['Name', 'Dojo', 'Type', 'Grade', 'Belt', 'Paid', 'BeltPaid', 'ID', 'GradeFull','Fee', 'BeltFee', 'TotalFee'])
                w.writerow(['Date','Name', 'Grade Full','Fee','Dojo', 'Type', 'Grade', 'Belt', 'Paid', 'BeltPaid', 'ID', 'BeltFee', 'TotalFee'])
                for student in students:
                    row = list(student)
                    
                    try:
                        if student['Paid'] == 1:
                            fee = self.students.FEES[str(student['Grade'])]
                        else:
                            fee = 0
                    except:
                        fee = 0
                    
                    try:
                        if student['BeltPaid'] == 1:
                            bfee = self.students.BELTFEE
                        else:
                            bfee = 0
                    except:
                        bfee = 0 
                    date = datetime.strptime(self.students.selecteddate, '%Y-%m-%d')
                    row.insert(0,date.strftime('%d-%m-%Y'))
                    row.insert(2,str(ordinal(student['Grade'])+' Kyu'))
                    row.insert(3, fee)
                    row.append(bfee)
                    row.append(fee+bfee)
                    
                    
                    w.writerow(row)
            try:
                os.startfile('export\\report_export.csv', 'open')
            except:
                #This will make the above windows command work on linux for dev testing
                import webbrowser
                webbrowser.open('export/report_export.csv')
    
    def export_belts(self):
            students = self.students.list_student()
            with open('export/report_belts.csv', 'wb') as csvfile:
                w = csv.writer(csvfile, dialect='excel')
                
                cols = ['Size', '2', '3', '4', '5', '6', '7']
                w.writerow(cols)

                grademap = {8:"Yellow",7:"Orange",6:"Green",5:"Blue",4:"Red",3:"Brown",2:"Brown",1:"Brown",0:"Black"}
                belts = {"Yellow":{},"Orange":{},"Green":{},"Blue":{},"Red":{},"Brown":{},"Black":{}}
                order = ["Yellow","Orange","Green","Blue","Red","Brown","Black"]
                
                
                for student in students:
                    if student['BeltPaid']:
                        try:
                            colour = grademap[student['Grade']]
                            if belts[colour].has_key(student['Belt']):
                                belts[colour][student['Belt']] += 1
                            else:
                                belts[colour][student['Belt']] = 1
                        except KeyError:
                            logging.exception("Student with unsupported grade")
                
                
                for colour in order:
                    row = []
                    for col in cols:
                        if col == "Size":
                            row.append(colour)
                        elif col == "Total":
                            row.append('')
                        else:
                            try:
                                row.append(belts[colour][int(col)])
                            except KeyError:
                                row.append(0)
                            
                    w.writerow(row)
                
            try:
                os.startfile('export\\report_belts.csv', 'open')
            except:
                #This will make the above windows command work on linux for dev testing
                import webbrowser
                webbrowser.open('export/report_belts.csv')
            

