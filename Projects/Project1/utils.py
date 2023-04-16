import os.path
from berkeleydb import db

PROMPT_PREFIX = "DB_2019-14355>" # prompt prefix

DB_PATH = 'db/'
DB_EXTENSION = '.db'
SCHEMA_DATA = DB_PATH + "meta" + DB_EXTENSION
TABLE_LIST = '__TABLE_LIST__'
COLUMN_LIST = '__TABLE_LIST__'
SEMI_COLON = ';'

CHAR = 'char'
DATE = 'data'
INT = 'int'
TRUE = 'True'
FALSE = 'False'
PRIMARY_KEY = 'PRIMARY_KEY'
COLUMNS = 'COLUMNS'
KEY_TYPE = 'KEY TYPE'
FOREIGN_KEY = 'FOREIGN_KEY'
COLUMNS_PREFIX = "COLUMNS_"

COLUMNS_PREFIX_LENGTH = len(COLUMNS_PREFIX)
COLUMN_DATA_LENGTH = 6


class Error:
    def __init__(self, error = False, error_type = "") -> None:
        self.error = error
        self.error_type = error_type


class ParsedData:
    def __init__(self) -> None:
        self.query_type = ""
        self.table_name = ""
        self.column_names = []
        self.dtypes = []
        self.dlength = []
        self.nullable = []
        self.primary = []
        self.foreign = dict()

class Schema:
    def __init__(self, my_db) -> None:
        self.my_db = my_db
        self.table_names = get_table_names(DB_PATH)
        self.tables = dict()
            
        for table_name in self.table_names:
            self.tables[table_name] = self.parsing_table(table_name)

        for t in self.tables.values():
            for c in t.column.values():
                if c.is_foreign and c.rtable != '':
                    self.tables[c.reference_table].referenced.add(t)
    def add_table(self, new_table):
        if isinstance(new_table, Table):
            self.tables[new_table.table_name] = new_table
            self.table_names.append(new_table.table_name)

    def remove_table(self, table_name):
        del self.tables[table_name]
        self.table_names.remove(table_name)

    def parsing_table(self, table_name):
        self.my_db.open(DB_PATH + table_name + DB_EXTENSION, dbtype=db.DB_HASH)

        # cursor = self.my_db.cursor()
        # while x := cursor.next():
        #     print(x)

        temp = Table(table_name, self.my_db.get(COLUMN_LIST.encode()).decode().split(SEMI_COLON), self.my_db)

        temp.parsing_columns(self.my_db)

        self.my_db.close()

        return temp


class Table:
    def __init__(self, table_name, column_names, my_db: db) -> None:
        self.table_name = table_name
        self.column_names = column_names
        self.column = dict()
        self.referenced = set()
        self.primary_key = []
        self.my_db = my_db

    def parsing_columns(self, my_db) -> None:
        for column_name in self.column_names:
            if column_name != '':
                col_name = COLUMNS_PREFIX + column_name
                data = my_db.get(col_name.encode()).decode().split(SEMI_COLON)
                print(data)
                self.column[column_name] = Column(column_name, data[0], data[1], data[2], data[3], data[4], data[5])
                if self.column[column_name].is_primary:
                    self.primary_key.append(column_name)

    def add_columns(self, col_name, dtype, dlength, n_ok, is_p, is_f, rtable) -> None:
        new_col = Column(col_name, dtype, dlength, n_ok, is_p, is_f, rtable)
        self.column[col_name] = new_col

    def create_db_file(self):
        self.my_db.open(DB_PATH + self.table_name + DB_EXTENSION, db.DB_HASH, db.DB_CREATE)
        self.my_db.put(COLUMN_LIST.encode(), list_to_bytes(self.column_names))
        for name in self.column_names:
            self.my_db.put(self.column[name].get_encoded_col_name(), self.column[name].to_byte_data())
        self.my_db.close()


class Column:
    def __init__(self, col_name, dtype, dlength, n_ok, is_p, is_f, rtable) -> None:
        self.column_name = col_name
        self.data_type = dtype

        try:
            self.data_length = int(dlength)
        except ValueError as e:
            self.data_length = -1

        if n_ok == 'True' or n_ok:
            self.nullable = True
        else:
            self.nullable = False

        if is_p == 'True' or is_p:
            self.is_primary = True
        else:
            self.is_primary = False

        if is_f == 'True' or is_f:
            self.is_foreign = True
        else:
            self.is_foreign = False

        if rtable == "":
            self.reference_table = ""
        else:
            self.reference_table = rtable

    def get_key_type(self):
        if self.is_primary:
            return 'PRI'
        elif self.is_foreign:
            return 'FOR'
        else:
            return  ''

    def get_type(self):
        if self.data_type == CHAR:
            return f'char({self.data_length})'
        else:
            return self.data_type

    def get_encoded_col_name(self):
        return (COLUMNS_PREFIX + self.column_name).encode()

    def to_byte_data(self):
        ret = (self.data_type + ';' + str(self.data_length) + ';' + str(self.nullable) + ';' + str(self.is_primary) + ';'
               + str(self.is_foreign) + ';' + self.reference_table + ';').encode()

        # print(ret)

        return ret


# Project 1-1 2nd section get input
def get_input():
    sql_input = input(PROMPT_PREFIX + " ")

    while True:
        sql_input = sql_input.strip()

        if sql_input[-1] != ";": # check input end with semi-colon
            sql_input += " " + input() # get_input until end with semi-colon

        else: # remove white space
            sql_input = sql_input.replace("\\r", "")
            sql_input = sql_input.replace("\\n", "")
            sql_input = sql_input.replace("\\t", "")
            sql_input = ' '.join(sql_input.split())
            break

    input_list = sql_input.split("; ")

    for i in range(len(input_list)):
        if input_list[i][-1] != ";":
            input_list[i] += ";"

    return input_list


def list_to_bytes(data):
    ret = ""
    for elem in data:
        ret += elem + ";"
    return ret.encode()


def get_table_names(path):
    files = os.listdir(path)
    db_files = [file for file in files if os.path.isfile(os.path.join(path, file)) and file.endswith(".db")]
    names = [os.path.splitext(file)[0] for file in db_files]

    return [os.path.splitext(name)[0] for name in names]