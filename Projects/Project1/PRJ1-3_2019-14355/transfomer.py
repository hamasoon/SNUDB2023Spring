import os.path
import datetime
from lark import Transformer
from berkeleydb import db
from utils import *

EXIT_STR = 'exit;'


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

    # select query
    def select_query(self, items):
        self.data.query_type = "SELECT"
        
        # check selected columns are valid
        for i in range(len(self.data.select_columns)):
            (t_name, c_name) = self.data.select_columns[i]
            
            # case 1 : table name is specified
            if t_name != None:
                # selected table is non-exist case
                if t_name not in self.sch.table_names:
                    self.error = Error(True, "SelectTableExistenceError", t_name)
                    return items
                
                # check specified table is in selected table
                if t_name not in self.data.select_table:
                    self.error = Error(True, "SelectColumnResolveError", t_name, c_name)
                    return items
                
                # selected column is not exist in table
                if c_name not in self.sch.tables[t_name].column_names:
                    self.error = Error(True, "SelectColumnResolveError", t_name, c_name)
                    return items
                
            # case 2 : table name is skipped
            else:
                cnt = 0
                # search which selected table contain column name
                for table_name in self.data.select_table:
                    # selected table is non-exist case
                    if table_name not in self.sch.table_names:
                        self.error = Error(True, "SelectTableExistenceError", table_name)
                        return items
                    
                    for col_name in self.sch.tables[table_name].column_names:
                        if col_name == c_name:
                            self.data.select_columns[i] = (table_name, c_name)
                            cnt += 1
                
                # if multiple table contain column, then return ambigious error
                if cnt > 1:
                    self.error = Error(True, "SelectColumnResolveError", t_name, c_name)
                    return items
                # if any table doesn't contain, then return non-exist column error
                elif cnt == 0:
                    self.error = Error(True, "SelectColumnResolveError", t_name, c_name)
                    return items

        # where clause valid checking process
        for cond in self.data.conditions:
            # case 1 : value comparision condition
            if cond.comp_type == VALUE_COMP: 
                # compand valid checking
                if cond.compand1.data_type == '':
                    cond.compand1 = self.compand_data_checking(cond.compand1)
                if cond.compand2.data_type == '':
                    cond.compand2 = self.compand_data_checking(cond.compand2)

                if self.error.error:
                    return items

                # if make comparision between non null and different type values, send error
                if cond.compand1.data_type != NULL and cond.compand2.data_type != NULL:
                    if cond.compand1.data_type != cond.compand2.data_type:
                        self.error = Error(True, "WhereIncomparableError")
                        
            # case 2 : null checking conditions
            else:
                # case 2-1 : non specfied column
                if cond.table_name == '':
                    cnt = 0
                    # check table name valid
                    for t_name in self.data.select_table:
                        # specified table non-exist
                        if t_name not in self.sch.table_names:
                            self.error = Error(True, 'NoSuchTable', t_name)
                            return items
                        
                        if cond.col_name in self.sch.tables[t_name].column_names:
                            cond.table_name = t_name
                            cnt += 1
                            
                    # column is not exist
                    if cnt == 0:
                        self.error = Error(True, 'WhereColumnNotExist')
                        return items
                    # column refered by more than 2 tables
                    elif cnt > 1:
                        self.error = Error(True, 'WhereAmbiguousReference')
                        return items
                # case 2-2 : specfied case 
                else:
                    # table existence check
                    if cond.table_name not in self.data.select_table:
                        self.error = Error(True, 'WhereTableNotSpecified')
                        return items
                    # column existence check
                    elif cond.col_name not in self.sch.tables[cond.table_name].column_names:
                        self.error = Error(True, 'WhereColumnNotExist')
                        return items

        return items

    # handle insert query
    def insert_query(self, items):
        self.data.query_type = "INSERT"
        self.data.table_name = items[2].children[0].lower()
        
        # table existence check
        if self.data.table_name not in self.sch.table_names:
            self.error = Error(True, "NoSuchTable")
            return items
        
        # length of inserted values
        key_count = len(items[5].children)

        # column names specified case
        if items[3] != None:
            col_len = len(items[3].children) - 2
        else:
            col_len = len(self.sch.tables[self.data.table_name].column_names)

        # if column length doesn't fit with value length -> return error
        if col_len != key_count - 2:
            self.error = Error(True, "InsertTypeMismatchError")
            return items

        # set non-specified values as null
        self.data.values = {col: 'null' for col in self.sch.tables[self.data.table_name].column_names}

        # parsing inserted values
        for i in range(1, key_count - 1):
            if items[3] != None:
                column_name = items[3].children[i].children[0].lower()
            else:
                column_name = self.sch.tables[self.data.table_name].column_names[i - 1]

            value = items[5].children[i].children[0]

            # column name existence check
            if column_name not in self.sch.tables[self.data.table_name].column_names:
                self.error = Error(True, "InsertColumnExistenceError", "", column_name)
                return items

            if value != "'null'":
                # data type matching check
                if items[5].children[i].children[0].type == 'STR':
                    if self.sch.tables[self.data.table_name].column[column_name].data_type != CHAR:
                        self.error = Error(True, "InsertTypeMismatchError")
                        return items
                elif items[5].children[i].children[0].type.lower() != \
                    self.sch.tables[self.data.table_name].column[column_name].data_type:
                    self.error = Error(True, "InsertTypeMismatchError")
                    return items
                    
                # slicing data if datatype is str and lnger than char length
                if self.sch.tables[self.data.table_name].column[column_name].data_type == CHAR:
                    value = value[1:len(value)-1]
                    if len(value) > self.sch.tables[self.data.table_name].column[column_name].data_length:
                        value = value[:self.sch.tables[self.data.table_name].column[column_name].data_length]
                        
            # nullable check
            else:
                if not self.sch.tables[self.data.table_name].column[column_name].nullable:
                    self.error = Error(True, "InsertColumnNonNullableError", "", column_name)
                    return items
                
                value = value[1:len(value)-1]

            self.data.values[column_name] = value

        for k, v in self.data.values.items():
            if not self.sch.tables[self.data.table_name].column[k].nullable and v == 'null':
                self.error = Error(True, "InsertColumnNonNullableError", "", k)
                return items

        return items
    
    # handle delete query
    def delete_query(self, items):
        self.data.query_type = "DELETE"
        self.data.table_name = items[2].children[0].lower()

        for cond in self.data.conditions:
            # case 1 : value comparsion
            if cond.comp_type == VALUE_COMP: 
                # compand valid checking
                if cond.compand1.data_type == '':
                    cond.compand1 = self.compand_data_checking(cond.compand1)
                if cond.compand2.data_type == '':
                    cond.compand2 = self.compand_data_checking(cond.compand2)
                
                # type mismatching check
                if cond.compand1.data_type != NULL and cond.compand2.data_type != NULL:
                    if cond.compand1.data_type != cond.compand2.data_type:
                        self.error = Error(True, "WhereIncomparableError")

            # case 2 : null checking conditions
            else:
                cond.table_name = self.data.table_name
                
                # table existence check
                if cond.table_name not in self.sch.table_names:
                    self.error = Error(True, 'NoSuchTable')
                    return items
                
                # column existence check
                elif cond.col_name not in self.sch.tables[cond.table_name].column_names:
                    self.error = Error(True, 'WhereColumnNotExist')
                    return items

        return items
    
    def where_clause(self, items):
        return items

    def update_query(self, items):  # handle update query
        self.data.query_type = "UPDATE"
        return items
    
    # prasing selected columns
    def selected_column(self, items):
        table_name = None
        col_name = None
        if items[0] != None:
            table_name = items[0].children[0].lower()

        col_name = items[1].children[0].lower()
        
        self.data.select_columns.append((table_name, col_name))

        return items

    # parsing selected table
    def referred_table(self, items):
        table_name = items[0].children[0].lower()
        if table_name not in self.sch.table_names:
            self.error = Error(True, "SelectTableExistenceError", table_name)

        self.data.select_table.append(table_name)

        return items
    
    # parse null checking statement(is null, is not null)
    def null_predicate(self, items):
        cond = Condition()

        cond.comp_type = NULL_CHECK

        if items[0] != None:
            cond.table_name = items[0].children[0]
        
        cond.col_name = items[1].children[0]

        if items[2].children[1] != None:
            cond.is_not = True

        self.data.conditions.append(cond)

        return items
    
    # comapnd setting
    def compand_data_checking(self, compand: Compand) -> Compand:
        # if table name is not specified
        if compand.table_name == '':
            # delete case
            if self.data.query_type == 'DELETE':
                # set as target table name
                compand.table_name = self.data.table_name
            # select case
            else:
                count = 0
                # find column name inside table's column name
                for t_name in self.data.select_table:
                    for c_name in self.sch.tables[t_name].column_names:
                        if c_name == compand.column_name:
                            compand.table_name = t_name
                            count += 1

                # column name non exist case
                if count == 0:
                    self.error = Error(True, 'WhereColumnNotExist')
                    return compand
                
                # ambigious case
                elif count > 1:
                    self.error = Error(True, 'WhereAmbiguousReference')
                    return compand
                
        # table name specfied case
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

    # parsing each compand
    def parsing_compand(self, items) -> Compand:
        compand = Compand()
        if len(items.children) == 1:
            compand.data_type = items.children[0].children[0].type
            compand.value = items.children[0].children[0]

            # data transfrom by each types
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

    # prasing condition statement
    def comparison_predicate(self, items):
        cond = Condition()
        
        cond.comp_op = items[1].children[0]

        # parsing each compand
        cond.compand1 = self.parsing_compand(items[0])
        cond.compand2 = self.parsing_compand(items[2])

        self.data.conditions.append(cond)

        return items