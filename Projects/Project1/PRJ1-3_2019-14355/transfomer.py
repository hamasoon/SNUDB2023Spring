import os.path
import datetime
from lark import Transformer
from berkeleydb import db
from utils import *

EXIT_STR = 'exit;' # set exit

# Project 1-1 1st section CustomTransformer
class MyTransformer(Transformer):
    def __init__(self, sch: Schema):
        self.where_not = False
        self.error = Error()
        self.data = ParsedData()
        self.sch = sch 

    def reset(self):  # reset transformer to origin state
        self.where_not = False
        self.error = Error()
        self.data = ParsedData()

    def command(self, items):
        #print(items[0].pretty())

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

        if ref_table not in self.sch.table_names:
            self.error = Error(True, 'ReferenceTableExistenceError')
        elif key_count - 2 != len(self.sch.tables[ref_table].primary_key) \
            | ref_key_count - 2 != len(self.sch.tables[ref_table].primary_key) :
            self.error = Error(True, 'ReferenceNonPrimaryKeyError')
        else:
            for i in range(1, key_count - 1):
                col_name = items[2].children[i].children[0].lower()
                ref_col_name = items[5].children[i].children[0].lower()
                col_type = self.data.dtypes[self.data.column_names.index(col_name)]

                if ref_col_name not in self.sch.tables[ref_table].column_names:
                    self.error = Error(True, 'ReferenceColumnExistenceError')
                    break
                elif ref_col_name != self.sch.tables[ref_table].primary_key[i-1]:
                    self.error = Error(True, 'ReferenceNonPrimaryKeyError')
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
            self.error = Error(True, "DropReferencedTableError", self.data.table_name)

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
        for i in range(len(self.data.select_columns)):
            (t_name, c_name) = self.data.select_columns[i]
            
            if t_name != None:
                if t_name not in self.sch.table_names:
                    self.error = Error(True, "SelectTableExistenceError", t_name)
                    return items
                
                if t_name not in self.data.select_table:
                    self.error = Error(True, "SelectColumnResolveError", t_name, c_name)
                    return items
                
                if c_name not in self.sch.tables[t_name].column_names:
                    self.error = Error(True, "SelectColumnResolveError", t_name, c_name)
                    return items
            else:
                cnt = 0
                for table_name in self.data.select_table:
                    if table_name not in self.sch.table_names:
                        self.error = Error(True, "SelectTableExistenceError", table_name)
                        return items
                    
                    for col_name in self.sch.tables[table_name].column_names:
                        if col_name == c_name:
                            self.data.select_columns[i] = (table_name, c_name)
                            cnt += 1
                
                if cnt > 1:
                    self.error = Error(True, "SelectColumnResolveError", t_name, c_name)
                    return items
                
                elif cnt == 0:
                    self.error = Error(True, "SelectColumnResolveError", t_name, c_name)
                    return items

        for cond in self.data.conditions:
            if cond.comp_type == VALUE_COMP: 
                if cond.compand1.data_type == '':
                    cond.compand1 = self.compand_data_checking(cond.compand1)
                if cond.compand2.data_type == '':
                    cond.compand2 = self.compand_data_checking(cond.compand2)

                if self.error.error:
                    return items

                if cond.compand1.data_type != NULL and cond.compand2.data_type != NULL:
                    if cond.compand1.data_type != cond.compand2.data_type:
                        self.error = Error(True, "WhereIncomparableError")
            else:
                if cond.table_name == '':
                    cnt = 0
                    for t_name in self.data.select_table:
                        if t_name not in self.sch.table_names:
                            self.error = Error(True, 'NoSuchTable', t_name)
                            return items
                        
                        if cond.col_name in self.sch.tables[t_name].column_names:
                            cond.table_name = t_name
                            cnt += 1
                    
                    if cnt == 0:
                        self.error = Error(True, 'WhereColumnNotExist')
                        return items
                    elif cnt > 1:
                        self.error = Error(True, 'WhereAmbiguousReference')
                        return items
                     
                else:
                    if cond.table_name not in self.data.select_table:
                        self.error = Error(True, 'WhereTableNotSpecified')
                        return items
                    elif cond.col_name not in self.sch.tables[cond.table_name].column_names:
                        self.error = Error(True, 'WhereColumnNotExist')
                        return items

        return items

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
            self.error = Error(True, "InsertTypeMismatchError")
            return items

        self.data.values = {col: 'null' for col in self.sch.tables[self.data.table_name].column_names}

        for i in range(1, key_count - 1):
            if items[3] != None:
                column_name = items[3].children[i].children[0].lower()
            else:
                column_name = self.sch.tables[self.data.table_name].column_names[i - 1]

            value = items[5].children[i].children[0]

            if column_name not in self.sch.tables[self.data.table_name].column_names:
                self.error = Error(True, "InsertColumnExistenceError", column_name)
                return items

            if ~self.sch.tables[self.data.table_name].column[column_name].nullable:
                if value == 'null':
                    self.error = Error(True, "InsertColumnNonNullableError", column_name)
                    return items

            if items[5].children[i].children[0].type == 'STR':
                if self.sch.tables[self.data.table_name].column[column_name].data_type != CHAR:
                    self.error = Error(True, "InsertTypeMismatchError")
                    return items
            elif items[5].children[i].children[0].type.lower() != \
                self.sch.tables[self.data.table_name].column[column_name].data_type:
                self.error = Error(True, "InsertTypeMismatchError")
                return items
                
            if self.sch.tables[self.data.table_name].column[column_name].data_type == CHAR:
                value = value[1:len(value)-1]
                if len(value) > self.sch.tables[self.data.table_name].column[column_name].data_length:
                    value = value[:self.sch.tables[self.data.table_name].column[column_name].data_length]

            self.data.values[column_name] = value

        for k, v in self.data.values.items():
            if not self.sch.tables[self.data.table_name].column[k].nullable and v == 'null':
                self.error = Error(True, "InsertColumnNonNullableError", k)
                return items

        return items
    
    def delete_query(self, items):  # handle delete query
        self.data.query_type = "DELETE"
        self.data.table_name = items[2].children[0].lower()

        for cond in self.data.conditions:
            if cond.comp_type == VALUE_COMP: 
                if cond.compand1.data_type == '':
                    cond.compand1 = self.compand_data_checking(cond.compand1)
                if cond.compand2.data_type == '':
                    cond.compand2 = self.compand_data_checking(cond.compand2)
                
                if cond.compand1.data_type != NULL and cond.compand2.data_type != NULL:
                    if cond.compand1.data_type != cond.compand2.data_type:
                        self.error = Error(True, "WhereIncomparableError")

        return items
    
    def where_clause(self, items):
        return items

    def update_query(self, items):  # handle update query
        self.data.query_type = "UPDATE"
        return items
    
    def selected_column(self, items):
        table_name = None
        col_name = None
        if items[0] != None:
            table_name = items[0].children[0].lower()

        col_name = items[1].children[0].lower()
        
        self.data.select_columns.append((table_name, col_name))

        return items

    # simply select query for only 1-2
    # TODO in 1-3
    def referred_table(self, items):
        table_name = items[0].children[0].lower()
        if table_name not in self.sch.table_names:
            self.error = Error(True, "SelectTableExistenceError", table_name)

        self.data.select_table.append(table_name)

        return items
    
    def null_predicate(self, items):
        # print("null_predicate")
        cond = Condition()

        cond.comp_type = NULL_CHECK

        if items[0] != None:
            cond.table_name = items[0].children[0]
        
        cond.col_name = items[1].children[0]

        if items[2].children[1] != None:
            cond.is_not = True

        self.data.conditions.append(cond)

        return items
    
    def compand_data_checking(self, compand: Compand) -> Compand:
        if compand.table_name == '':
            if self.data.query_type == 'DELETE':
                compand.table_name = self.data.table_name
            else:
                count = 0
                for t_name in self.data.select_table:
                    for c_name in self.sch.tables[t_name].column_names:
                        if c_name == compand.column_name:
                            compand.table_name = t_name
                            count += 1

                if count == 0:
                    self.error = Error(True, 'WhereColumnNotExist')
                    return compand
                elif count > 1:
                    self.error = Error(True, 'WhereAmbiguousReference')
                    return compand

        else:
            if self.data.query_type == 'DELETE' and compand.table_name not in self.data.table_name:
                self.error = Error(True, 'WhereTableNotSpecified')
                return compand
            elif self.data.query_type == 'SELECT' and compand.table_name not in self.data.select_table:
                self.error = Error(True, 'WhereTableNotSpecified')
                return compand

            if compand.column_name not in self.sch.tables[compand.table_name].column_names:
                self.error = Error(True, 'WhereColumnNotExist')
                return compand

        compand.data_type = self.sch.tables[compand.table_name].column[compand.column_name].data_type

        return compand

    def parsing_compand(self, items) -> Compand:
        compand = Compand()
        if len(items.children) == 1:
            compand.data_type = items.children[0].children[0].type
            compand.value = items.children[0].children[0]

            if compand.data_type == 'STR':
                compand.data_type= CHAR
                compand.value = compand.value[1:len(compand.value)-1]
            elif compand.data_type == 'INT':
                compand.value = int(compand.value)
            elif compand.data_type == 'DATE':
                compand.value = datetime.datetime.strptime(compand.value, '%Y-%m-%d')
            else:
                compand.data_type = NULL

            compand.data_type = compand.data_type.lower()

        else:
            if items.children[0] != None:
                compand.table_name = items.children[0].children[0].lower()
            compand.column_name = items.children[1].children[0].lower()

        return compand

    def comparison_predicate(self, items):
        # print("comparison_predicate")
        cond = Condition()

        # print(items[0].children[0], items[0].children[1])

        cond.comp_op = items[1].children[0]

        cond.compand1 = self.parsing_compand(items[0])
        cond.compand2 = self.parsing_compand(items[2])

        self.data.conditions.append(cond)

        return items