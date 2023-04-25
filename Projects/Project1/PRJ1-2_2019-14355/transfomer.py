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
        col_name = items[0].children[0].lower()
        if col_name in self.data.column_names:
            self.error = Error(True, 'DuplicateColumnDefError')

        self.data.column_names.append(col_name)

        if items[1].children[0].lower() == CHAR:
            self.data.dtypes.append(items[1].children[0].lower())
            self.data.dlength.append(items[1].children[2].lower())
            if int(items[1].children[2].lower()) <= 0:
                self.error = Error(True, 'CharLengthError')
        else:
            self.data.dtypes.append(items[1].children[0].lower())
            self.data.dlength.append(-1)

        if items[2] is None:
            self.data.nullable.append(True)
        else:
            self.data.nullable.append(False)

    def primary_key_constraint(self, items):
        if len(self.data.primary) != 0:
            self.error = Error(True, 'DuplicatePrimaryKeyDefError')
        else:
            key_count = len(items[2].children)
            for i in range(1, key_count - 1):
                if items[2].children[i].children[0].lower() in self.data.primary:
                    self.error = Error(True, 'DuplicatePrimaryKeyDefError')
                    break
                self.data.primary.append(items[2].children[i].children[0].lower())

    def referential_constraint(self, items):
        key_count = len(items[2].children)
        ref_key_count = len(items[5].children)
        ref_table = items[4].children[0].lower()

        print(key_count, len(self.sch.tables[ref_table].primary_key))

        if ref_table not in self.sch.table_names:
            self.error = Error(True, 'ReferenceTableExistenceError')
        elif key_count - 2 != len(self.sch.tables[ref_table].primary_key) \
            | ref_key_count - 2 != len(self.sch.tables[ref_table].primary_key) :
            self.error = Error(True, 'ReferenceNonPrimaryKeyError')
            print('ReferenceNonPrimaryKeyError')
        else:
            for i in range(1, key_count - 1):
                col_name = items[2].children[i].children[0].lower()
                ref_col_name = items[5].children[i].children[0].lower()
                col_type = self.data.dtypes[self.data.column_names.index(col_name)]

                if ref_col_name not in self.sch.tables[ref_table].column_names:
                    self.error = Error(True, 'ReferenceColumnExistenceError')
                    print('ReferenceColumnExistenceError')
                    break
                elif ref_col_name != self.sch.tables[ref_table].primary_key[i-1]:
                    self.error = Error(True, 'ReferenceNonPrimaryKeyError')
                    print('ReferenceNonPrimaryKeyError - 2')
                    break
                elif col_name not in self.data.column_names:
                    self.error = Error(True, 'NonExistingColumnDefError', '', col_name)
                    break
                elif col_type != self.sch.tables[ref_table].column[ref_col_name].data_type:
                    self.error = Error(True, 'ReferenceTypeError')
                    break
                elif col_type == CHAR:
                    col_length = int(self.data.dlength[self.data.column_names.index(col_name)])
                    if col_length != self.sch.tables[ref_table].column[ref_col_name].data_length:
                        self.error = Error(True, 'ReferenceTypeError')
                        break
                elif col_name in self.data.ref_table.keys():
                    self.error = Error(True, 'DuplicateColumnDefError')
                    break

                self.data.ref_table[col_name] = ref_table
                self.data.ref_column[col_name] = ref_col_name

        return items
        # How about col_count is different?
        # TODO

    def drop_table_query(self, items): # handle drop table query
        self.data.query_type = "DROP TABLE"
        self.data.table_name = items[2].children[0].lower()

        if self.data.table_name not in self.sch.table_names:
            self.error = Error(True, "NoSuchTable")
        elif bool(self.sch.tables[self.data.table_name].referenced):
            self.error = Error(True, "DropReferencedTableError")

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

    # from 절에 있는 테이블이 존재하지 않는다면, SelectTableExistenceError(#tabName)에 해당하는 메시지를 출력
    def select_query(self, items):  # handle select query
        self.data.query_type = "SELECT"
        return items

    # simply select query for only 1-2
    # TODO in 1-3
    def referred_table(self, items):
        self.data.table_name = items[0].children[0].lower()
        if self.data.table_name not in self.sch.table_names:
            self.error = Error(True, "SelectTableExistenceError", self.data.table_name)
        return items

    # 테이블 컬럼 개수와 입력된 value 개수가 일치
    # 각 컬럼의 자료형과 입력된 value 들의 자료형이 모두 일치
    # not null에 해당하는 컬럼에는 null 값이 들어가지 않음
    # 해당 오류들에 대한 건 1-3에서 수정할 것 TODO
    # 길이 오류에 대한 출력 확인해야함
    def insert_query(self, items):  # handle insert query
        self.data.query_type = "INSERT"
        self.data.table_name = items[2].children[0].lower()
        if self.data.table_name not in self.sch.table_names:
            self.error = Error(True, "NoSuchTable")
            return items
        
        key_count = len(items[5].children)

        if items[3] != None:
            col_len = len(items[3].children) - 2
        else:
            col_len = len(self.sch.tables[self.data.table_name].column_names)

        if col_len != key_count - 2:
            self.error = Error(True, "ValueColumnLengthUnmatch")
            return items

        for i in range(1, key_count - 1):
            if items[3] != None:
                column_name = items[3].children[i].children[0].lower()
            else:
                column_name = self.sch.tables[self.data.table_name].column_names[i - 1]

            value = items[5].children[i].children[0]

            if self.sch.tables[self.data.table_name].column[column_name].data_type == CHAR:
                value = value[1:len(value)-1]
                if len(value) > self.sch.tables[self.data.table_name].column[column_name].data_length:
                    value = value[:self.sch.tables[self.data.table_name].column[column_name].data_length]

            self.data.values[column_name] = value

        return items
    
    def delete_query(self, items):  # handle delete query
        self.data.query_type = "DELETE"
        return items
    
    def update_query(self, items):  # handle update query
        self.data.query_type = "UPDATE"
        return items