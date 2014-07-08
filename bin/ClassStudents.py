import datetime
import sqlite3
import logging 
import json

# Log everything, and send it to file.
logging.basicConfig(level=logging.DEBUG, filename='guredo_debug.log')

def ordinal(n):
    if 10 <= n % 100 < 20:
        return str(n) + 'th'
    elif n < 0:
        return  str(n*-1) + {9 : 'st', 8 : 'nd', 7 : 'rd'}.get(n % 10, "th")
    else:
       return  str(n) + {1 : 'st', 2 : 'nd', 3 : 'rd'}.get(n % 10, "th")


class ClassStudents:
    """class that abstracts students at the grading, and database operations"""

    def __init__(self):
        self.DATE = datetime.date.today().isoformat() #Date constant
        self.selecteddate = self.DATE
        self.sql = sqlite3.connect('gradings.db')
        #Allow pythonic access tor row fields by name
        self.sql.row_factory = sqlite3.Row 
        #Turn off transactions for increased performance, commit() not required
        self.sql.isolation_level = None
        self.students = []
        self.id = None
        
        self.FEES = {}
        self.BELTFEE = 10.00
        
        try:
            with open('config.json', 'r') as jsonfile:
                config = json.load(jsonfile)
            self.FEES = config['FEES']
            self.BELTFEE = config['BELTFEE']
            self.DOJOS = config['DOJOS']
        except:
            logging.exception("JSON config load failed")
            raise


    def create_tables(self):
        try:
            self.sql.execute\
                ('CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'Date TEXT, Name TEXT, Dojo TEXT, Type TEXT, Grade INT, Belt INT, Paid INT, BeltPaid INT);')
        except:
            logging.exception("Error")

    def add_student(self, form, id=None):
        """Create a new student database record using a dictionary of values"""

        try:
            cur = self.sql.execute\
                ('INSERT INTO students (Date, Name, Dojo, Type, Grade, Belt, Paid, BeltPaid) VALUES'
                 '(:Date, :Name, :Dojo, :Type, :Grade, :Belt, :Paid, :BeltPaid);',
                 form)
            logging.debug(cur.lastrowid)
            #self.sql.commit()
            return True
        except:
            logging.exception("Error")
            raise
    
    def update_student(self, form, id=None):
        """Create a new student database record using a dictionary of values"""

        try:
            form['id'] = id 
            cur = self.sql.execute\
                ('UPDATE students SET Name=:Name, Dojo=:Dojo, Type=:Type, Grade=:Grade, Belt=:Belt, '
                 ' Paid=:Paid, BeltPaid=:BeltPaid WHERE id = :id;',
                 form)
            #self.sql.commit()
            return True
        except:
            logging.exception("Error")
            raise
    
    def delete_student(self, id=None):
        """Create a new student database record using a dictionary of values"""
        if not id:
            id = self.id
        try:
            cur = self.sql.execute\
                ('DELETE FROM students WHERE id = ?', [id,])
            #self.sql.commit()
            return True
        except:
            logging.exception("Error")
            raise
        
    def list_student(self, id=None, date=True, type=None):
        """List students for todays grading, or return a single student by ID"""

        if not id:
            try:
                if date and type:
                    query = 'SELECT Name, Dojo, Type, Grade, Belt, Paid, BeltPaid, id '\
                            'FROM students WHERE Date = ? AND type = ?;'
                    logging.debug(type)
                    rows = self.sql.execute(query, [self.selecteddate,type])
                elif date:
                    query = 'SELECT Name, Dojo, Type, Grade, Belt, Paid, BeltPaid, id '\
                            'FROM students WHERE Date = ?;'
                    rows = self.sql.execute(query, [self.selecteddate,])
                else:
                    rows = self.sql.execute\
                    ('SELECT Name, Dojo, Type, Grade, Belt, Paid, BeltPaid, id '
                     'FROM students;')

                self.students = list(rows)
                return self.students
            except:
                logging.exception("Error")
                return None
        else:
            try:
                query = 'SELECT Name, Dojo, Type, Grade, Belt, Paid, BeltPaid, id '\
                            'FROM students WHERE id = ?;'
                rows = self.sql.execute(query, [id,])
                return rows.fetchone()
            except:
                logging.exception("Error")
                return None
            
    def select_dates(self):
        rows = self.sql.execute\
                    ('SELECT DISTINCT Date '
                     'FROM students WHERE Date <> ? '
                     'ORDER BY Date DESC;', [self.DATE,])
        return rows.fetchall()
        
        
