import os.path
import pickle
from berkeleydb import db

PROMPT_PREFIX = "DB_2019-14355>" # prompt prefix

DB_PATH = 'db/'
DB_EXTENSION = '.db'
SCHEMA_DATA = "schema.pickle"
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
    def __init__(self, error=False, error_type='', table='', col='') -> None:
        self.error = error
        self.error_type = error_type
        self.error_table = table
        self.error_col = col


class ParsedData:
    def __init__(self) -> None:
        self.query_type = ""
        self.table_name = ""
        self.column_names = []
        self.dtypes = []
        self.dlength = []
        self.nullable = []
        self.primary = []
        self.values = dict()
        self.ref_table = dict()
        self.ref_column = dict()


class Schema:
    def __init__(self) -> None:
        self.table_names = get_table_names(DB_PATH)
        self.tables = dict()

    def add_table(self, new_table):
        if isinstance(new_table, Table):
            self.tables[new_table.table_name] = new_table
            self.table_names.append(new_table.table_name)

    def remove_table(self, table_name):
        target = self.tables[table_name]

        for col in target.column.values():
            if col.reference_table != '':
                ref_table = col.reference_table

                del self.tables[ref_table].referenced[table_name, col.column_name]

        del self.tables[table_name]
        self.table_names.remove(table_name)

    def save_schema(self) -> None:
        with open(SCHEMA_DATA,"wb") as fw:
            pickle.dump(self, fw)


class Table:
    def __init__(self, table_name, column_names) -> None:
        self.table_name = table_name
        self.column_names = column_names
        self.column = dict()
        self.referenced = dict()
        self.primary_key = []
        self.elem_count = 0
        
    def add_columns(self, col_name, dtype, dlength, n_ok, is_p, is_f, rtable, rcol_name) -> None:
        new_col = Column(col_name, dtype, dlength, n_ok, is_p, is_f, rtable, rcol_name)

        if is_p:
            self.primary_key.append(col_name)

        self.column[col_name] = new_col
    

class Column:
    def __init__(self, col_name, dtype, dlength, n_ok, is_p, is_f, rtable, rcol_name) -> None:
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

        if rcol_name == '':
            self.reference_column_name = ''
        else:
            self.reference_column_name = rcol_name

    def get_key_type(self):
        ret = ''

        if self.is_primary & self.is_foreign:
            ret = 'PRI/FOR'
        elif self.is_primary:
            ret = 'PRI'
        elif self.is_foreign:
            ret += 'FOR'

        return ret

    def get_type(self):
        if self.data_type == CHAR:
            return f'char({self.data_length})'
        else:
            return self.data_type

    def get_encoded_col_name(self):
        return (COLUMNS_PREFIX + self.column_name).encode()


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

    input_list = sql_input.split(";")

    for i in range(len(input_list)):
        input_list[i] = input_list[i].strip()
        if input_list[i] == '':
            continue
        elif input_list[i][-1] != ";":
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