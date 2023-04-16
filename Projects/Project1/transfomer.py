import os.path
from lark import Transformer
from berkeleydb import db
from utils import *

EXIT_STR = 'exit;' # set exit

# Project 1-1 1st section CustomTransformer
class MyTransformer(Transformer):
    def __init__(self, sch: Schema):
        self.error = Error()
        self.data = ParsedData()
        self.sch = sch 

    def reset(self):  # reset transformer to origin state
        self.error = Error()
        self.data = ParsedData()

    def command(self, items):
        if items[0] == 'exit': # handle exit case
            return EXIT_STR
        else:
            return self.data.query_type
        
    def create_table_query(self, items): # handle create table query
        self.data.query_type = "CREATE TABLE"
        self.data.table_name = items[2].children[0].lower()

        if self.data.table_name in self.sch.table_names :
            self.error = Error(True, "TableExistenceError")

        return items
    
    def column_definition(self, items):
        self.data.column_names.append(items[0].children[0].lower())

        if items[1].children[0].lower() == CHAR:
            self.data.dtypes.append(items[1].children[0].lower())
            self.data.dlength.append(items[1].children[2].lower())
        else:
            self.data.dtypes.append(items[1].children[0].lower())
            self.data.dlength.append(-1)

        if items[2] is None:
            self.data.nullable.append(True)
        else:
            self.data.nullable.append(False)

    def primary_key_constraint(self, items):
        key_count = len(items[2].children)
        for i in range(1, key_count - 1):
            self.data.primary.append(items[2].children[i].children[0].lower())

    def referential_constraint(self, items):
        # TODO
        # Have to do this first!!!!!!!!!!
        pass
        #print(items[2])

    def drop_table_query(self, items): # handle drop table query
        self.data.query_type = "DROP TABLE"
        self.data.table_name = items[2].children[0].lower()

        if self.data.table_name not in self.sch.table_names:
            self.error = Error(True, "NoSuchTable")

        return items
    
    def describe_query(self, items):  # handle describe query
        self.data.query_type = "DESCRIBE"
        self.data.table_name = items[1].children[0].lower()

        if self.data.table_name not in self.sch.table_names:
            self.error = Error(True, "NoSuchTable")
        return items
    
    def explain_query(self, items):  # handle explain query
        self.data.query_type = "EXPLAIN"
        self.data.table_name = items[1].children[0].lower()

        if self.data.table_name not in self.sch.table_names:
            self.error = Error(True, "NoSuchTable")
        return items
    
    def desc_query(self, items):  # handle desc query
        self.data.query_type = "DESC"
        self.data.table_name = items[1].children[0].lower()

        if self.data.table_name not in self.sch.table_names:
            self.error = Error(True, "NoSuchTable")
        return items
    
    def show_tables_query(self, items):  # handle show tables query
        self.data.query_type = "SHOW TABLES"
        return items
    
    def select_query(self, items):  # handle select query
        self.data.query_type = "SELECT"
        return items
    
    def insert_query(self, items):  # handle insert query
        self.data.query_type = "INSERT"
        return items
    
    def delete_query(self, items):  # handle delete query
        self.data.query_type = "DELETE"
        return items
    
    def update_query(self, items):  # handle update query
        self.data.query_type = "UPDATE"
        return items