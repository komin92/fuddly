import os
import sys
import datetime

from libs.external_modules import *
from fuzzfmk.data_model import Data
import fuzzfmk.global_resources as gr

class Database(object):

    DDL_fname = 'fmk_db.sql'

    def __init__(self):
        self.name = 'fmkDB.db'
        self.log_db = os.path.join(gr.trace_folder, self.name)
        self._con = None
        self._cur = None
        self.enabled = False

    def start(self):
        if not sqlite_module:
            print("/!\\ WARNING /!\\: Fuddly's LogDB unavailable because python-sqlite3 is not installed!")
            return False

        if os.path.isfile(self.log_db):
            self._con = sqlite.connect(self.log_db)
            self._cur = self._con.cursor()

        else:
            self._con = sqlite.connect(self.log_db)
            fmk_db_sql = open(gr.fmk_folder + self.DDL_fname).read()
            with self._con:
                self._cur = self._con.cursor()
                self._cur.executescript(fmk_db_sql)

        self.enabled = True

    def stop(self):
        if self._con:
            self._con.close()

        self._con = None
        self._cur = None
        self.enabled = False

    def commit(self):
        try:
            self._con.commit()
        except sqlite.Error as e:
            self._con.rollback()
            return -1
        else:
            return 0

    def insert_data_model(self, dm_name):
        try:
            self._cur.execute(
                    "INSERT INTO DATAMODEL(DM_NAME) VALUES(?)",
                    (dm_name,))
        except sqlite.Error as e:
            self._con.rollback()
            print("\n*** ERROR[SQL:{:s}] while inserting a value into table DATAMODEL!".format(e.args[0]))
            return -1
        else:
            return self._cur.lastrowid

    def insert_dmaker(self, dm_name, dtype, name, is_gen, stateful, clone_type=None):
        clone_name = None if clone_type is None else name
        try:
            self._cur.execute(
                    "INSERT INTO DMAKERS(DM_NAME,TYPE,NAME,CLONE_TYPE,CLONE_NAME,GENERATOR,STATEFUL)"
                    " VALUES(?,?,?,?,?,?,?)",
                    (dm_name, dtype, name, clone_type, clone_name, is_gen, stateful))
        except sqlite.Error as e:
            self._con.rollback()
            print("\n*** ERROR[SQL:{:s}] while inserting a value into table DMAKERS!".format(e.args[0]))
            return -1
        else:
            return self._cur.lastrowid

    def insert_data(self, dtype, dm_name, raw_data, sz, sent_date, ack_date, group_id=None):
        blob = sqlite.Binary(raw_data)
        try:
            self._cur.execute(
                    "INSERT INTO DATA(GROUP_ID,TYPE,DM_NAME,CONTENT,SIZE,SENT_DATE,ACK_DATE)"
                    " VALUES(?,?,?,?,?,?,?)",
                    (group_id, dtype, dm_name, blob, sz, sent_date, ack_date))
            self._con.commit()
        except sqlite.Error as e:
            self._con.rollback()
            print("\n*** ERROR[SQL:{:s}] while inserting a value into table DATA!".format(e.args[0]))
            return -1
        else:
            return self._cur.lastrowid

    def insert_steps(self, data_id, step_id, dmaker_type, dmaker_name, user_input, info):
        if info:
            info = sqlite.Binary(info)
        try:
            self._cur.execute(
                    "INSERT INTO STEPS(DATA_ID,STEP_ID,DMAKER_TYPE,DMAKER_NAME,USER_INPUT,INFO)"
                    " VALUES(?,?,?,?,?,?)",
                    (data_id, step_id, dmaker_type, dmaker_name, user_input, info))
        except sqlite.Error as e:
            self._con.rollback()
            print("\n*** ERROR[SQL:{:s}] while inserting a value into table STEPS!".format(e.args[0]))
            return -1
        else:
            return self._cur.lastrowid

    def insert_feedback(self, data_id, source, content):
        if content:
            content = sqlite.Binary(content)
        try:
            self._cur.execute(
                    "INSERT INTO FEEDBACK(DATA_ID,SOURCE,CONTENT)"
                    " VALUES(?,?,?)",
                    (data_id, source, content))
            self._con.commit()
        except sqlite.Error as e:
            self._con.rollback()
            print("\n*** ERROR[SQL:{:s}] while inserting a value into table FEEDBACK!".format(e.args[0]))
            return -1
        else:
            return self._cur.lastrowid

    def insert_comment(self, data_id, content, date):
        try:
            self._cur.execute(
                    "INSERT INTO COMMENTS(DATA_ID,CONTENT,DATE)"
                    " VALUES(?,?,?)",
                    (data_id, content, date))
            self._con.commit()
        except sqlite.Error as e:
            self._con.rollback()
            print("\n*** ERROR[SQL:{:s}] while inserting a value into table COMMENTS!".format(e.args[0]))
            return -1
        else:
            return self._cur.lastrowid

    def insert_fmk_info(self, data_id, content, date, error=False):
        try:
            self._cur.execute(
                    "INSERT INTO FMKINFO(DATA_ID,CONTENT,DATE,ERROR)"
                    " VALUES(?,?,?,?)",
                    (data_id, content, date, error))
            self._con.commit()
        except sqlite.Error as e:
            try:
                self._con.rollback()
                print("\n*** ERROR[SQL:{:s}] while inserting a value into table FMKINFO!".format(e.args[0]))
                return -1
            except sqlite.ProgrammingError as e:
                print("\n*** ERROR[SQLite]: {:s}".format(e.args[0]))
                print("*** Not currently handled by fuddly.")
                return -1
        else:
            return self._cur.lastrowid
