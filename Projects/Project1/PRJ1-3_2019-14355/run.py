import pickle
import datetime
import re
from lark import Lark
from transfomer import MyTransformer, EXIT_STR
from utils import *
from berkeleydb import db

# prefix for prompt like view
# open sql_parser
with open('grammar.lark') as file:
    sql_parser = Lark(file.read(), start="command", lexer="basic")

my_db = db.DB()

my_s = Schema()

class Record:
    def __init__(self, t_names, conditions) -> None:
        self.conditions = conditions
        self.table_names = t_names
        self.col_names = dict()
        self.origin_data = []
        self.data = []
        self.byte_data = []
        self.unknown_state = False
        cnt = 0
        for t_name in t_names:
            for c_name in my_s.tables[t_name].column_names:
                self.col_names['.'.join([t_name, c_name])] = cnt
                cnt += 1

        ret = []
        for t_name in t_names:
            my_db = db.DB()
            my_db.open(DB_PATH + t_name + DB_EXTENSION, db.DB_HASH)
            temp1 = []
            cursor = my_db.cursor()
            while x := cursor.next():
                data = self.to_real_data(x, t_name)
                temp1.append(data)
                
            ret.append(temp1)
            my_db.close()

        for (idx, table) in enumerate(ret):
            if idx == 0:
                self.origin_data = table
            else:
                temp2 = []
                for data_ret in self.origin_data:
                    for data in table:
                        temp2.append(data_ret + data)
                self.origin_data = temp2
            
    def not_operation(self, data):
        return [value for value in self.origin_data if value not in data]

    def to_real_data(self, raw, t_name):
        col_data = raw[1].decode().split(';')[:-1]

        for (idx, c_name) in enumerate(my_s.tables[t_name].column_names):
            if my_s.tables[t_name].column[c_name].data_type == INT:
                col_data[idx] = int(col_data[idx])
            elif my_s.tables[t_name].column[c_name].data_type == DATE:
                col_data[idx] = datetime.datetime.strptime(col_data[idx], '%Y-%m-%d')
            elif col_data[idx] == NULL:
                col_data[idx] = 'null'
        
        return col_data
    
    def check_data_included(self, raw, t_name):
        return self.to_real_data(raw, t_name) in self.data

    def operate_cond(self, cond: Condition):
        temp = []
        if cond.comp_type == NULL_CHECK:
            idx = self.col_names['.'.join([cond.table_name, cond.col_name])]
            for data in self.origin_data:
                if data[idx] == 'null' and not cond.is_not:
                    temp.append(data)
                elif data[idx] != 'null' and  cond.is_not:
                    temp.append(data)
        else:
            idx1 = None
            idx2 = None
            value1 = None
            value2 = None
            if cond.compand1.column_name != '':
                idx1 = self.col_names['.'.join([cond.compand1.table_name, cond.compand1.column_name])]
            else:
                value1 = cond.compand1.value

            if cond.compand2.column_name != '':
                idx2 = self.col_names['.'.join([cond.compand2.table_name, cond.compand2.column_name])]
            else:
                value2 = cond.compand2.value

            for data in self.origin_data:
                if idx1 != None:
                    value1 = data[idx1]
                if idx2 != None:
                    value2 = data[idx2]

                if cond.comp_op == "=":
                    if value1 == value2:
                        temp.append(data)
                elif cond.comp_op == "!=":
                    if value1 != value2:
                        temp.append(data)
                elif cond.comp_op == "<":
                    if value1 < value2:
                        temp.append(data)
                elif cond.comp_op == "<=":
                    if value1 <= value2:
                        temp.append(data)
                elif cond.comp_op == ">":
                    if value1 > value2:
                        temp.append(data)
                elif cond.comp_op == ">=":
                    if value1 >= value2:
                        temp.append(data)
                        
        return temp

    def logic_operation(self, data1, data2, op):
        data = []
        
        if op.lower() == AND:
            data = [value for value in data1 if value in data2]
        elif op.lower() == OR:
            data = data1
            data += [value for value in data2 if value not in data1]
            
        return data

    def operate(self, opeartions):
        if len(opeartions) == 0:
            self.data = self.origin_data
            return
        
        stack = []
        
        for op in opeartions:
            if isinstance(op, int):
                stack.append(self.operate_cond(self.conditions[op]))
            elif op.lower() == 'not':
                stack.append(self.not_operation(stack.pop()))
            else:
                stack.append(self.logic_operation(stack.pop(), stack.pop(), op.lower()))
                
        self.data = stack.pop()


if os.path.exists(SCHEMA_DATA):
    with open(SCHEMA_DATA, "rb") as fr:
        my_s = pickle.load(fr)

def to_postfix(input) -> list:
    precedence = {'not': 3, 'NOT': 3, 'AND': 2, 'and': 2, 'OR': 1, 'or': 1}

    operator_stack = []
    result_stack = []

    for token in input:
        if token in precedence:
            while operator_stack and operator_stack[-1] != '(' and precedence[operator_stack[-1]] >= precedence[token]:
                result_stack.append(operator_stack.pop())
            operator_stack.append(token)
        elif token == '(':
            operator_stack.append(token)
        elif token == ')':
            while operator_stack and operator_stack[-1] != '(':
                result_stack.append(operator_stack.pop())
            operator_stack.pop()
        else:
            result_stack.append(token)

    while operator_stack:
        result_stack.append(operator_stack.pop())

    return result_stack

    
def where_clasue_parser(input) -> list:
    where_clause = re.split(r'(?i)\bwhere\b', input)
    if len(where_clause) < 2:
        return []

    where_clause = where_clause[1][:-1].strip()
    words = [word for word in re.split(r'(\W)', where_clause) if word not in [' ', '']]

    result = []
    cnt = 0
    previous = True

    for (idx, word) in enumerate(words):
        if word in OPS:
            if (word == 'NOT' or word == 'not') and (idx > 0 and idx < len(words) - 1):
                if (words[idx - 1] == 'is' or words[idx - 1] == 'IS') and \
                    (words[idx + 1] == 'null' or words[idx + 1] == 'NULL'):
                    previous = False
                    continue
                else:
                    if not previous:
                        result.append(cnt)
                        cnt += 1
                    result.append(word)
                    previous = True
            else:
                if not previous:
                    result.append(cnt)
                    cnt += 1
                result.append(word)
                previous = True
        else:
            previous = False

    if len(result) == 0:
        result.append(cnt)
    elif result[len(result) - 1] in ['not', 'NOT', 'AND', 'and', 'or', 'OR']:
        result.append(cnt)

    return to_postfix(result)

def error_message(e: Error):
    if e.error_type == 'DuplicateColumnDefError':  # Done
        return 'Create table has failed: column definition is duplicated'
    elif e.error_type == 'DuplicatePrimaryKeyDefError':  # Done
        return 'Create table has failed: primary key definition is duplicated'
    elif e.error_type == 'ReferenceTypeError': # Done
        return 'Create table has failed: foreign key references wrong type'
    elif e.error_type == 'ReferenceNonPrimaryKeyError':  # Done
        return 'Create table has failed: foreign key references non primary key column'
    elif e.error_type == 'ReferenceColumnExistenceError':  # Done
        return 'Create table has failed: foreign key references non existing column'
    elif e.error_type == 'ReferenceTableExistenceError':  # Done
        return 'Create table has failed: foreign key references non existing table'
    elif e.error_type == 'NonExistingColumnDefError':  # Done
        return f'Create table has failed: {e.error_col} does not exist in column definition'
    elif e.error_type == "TableExistenceError":  # Done
        return "Create table has failed: table with the same name already exists"
    elif e.error_type == "NoSuchTable":
        return "No such table"
    elif e.error_type == 'CharLengthError':  # Done
        return 'Char length should be over 0'
    elif e.error_type == 'DropReferencedTableError':
        return f'Drop table has failed: {e.error_table} is referenced by other table'
    elif e.error_type == 'SelectTableExistenceError':  # error in FROM clause
        return f'Selection has failed: {e.error_table} does not exist'
    elif e.error_type == 'SelectColumnResolveError':
        return f'Selection has failed: fail to resolve {e.error_col}'
    elif e.error_type == 'WhereIncomparableError':
        return 'Where clause trying to compare incomparable values'
    elif e.error_type == 'WhereTableNotSpecified': 
        return 'Where clause trying to reference tables which are not specified'
    elif e.error_type == 'WhereColumnNotExist':
        return 'Where clause trying to reference non existing column'
    elif e.error_type == 'WhereAmbiguousReference':
        return 'Where clause contains ambiguous reference'
    elif e.error_type == 'InsertTypeMismatchError':
        return 'Insertion has failed: Types are not matched'
    elif e.error_type == 'InsertColumnExistenceError':
        return f'Insertion has failed: {e.error_col} does not exist'
    elif e.error_type == 'InsertColumnNonNullableError':
        return f'Insertion has failed: {e.error_col} is not nullable'

def handle_request(data: ParsedData, operation):
    if data.query_type == "CREATE TABLE":
        new_table = Table(data.table_name, data.column_names)

        for idx in range(len(data.column_names)):
            is_p = data.column_names[idx] in data.primary
            is_f = data.column_names[idx] in data.ref_table.keys()

            # print (data.nullable[idx], is_p, is_f, data.nullable[idx] & (not is_p))

            if is_f:
                new_table.add_columns(data.column_names[idx], data.dtypes[idx], data.dlength[idx],
                                      data.nullable[idx] & (not is_p), is_p, is_f, data.ref_table[data.column_names[idx]],
                                      data.ref_column[data.column_names[idx]])
                my_s.tables[data.ref_table[data.column_names[idx]]].referenced[(data.table_name, data.column_names[idx])] \
                    = data.ref_column[data.column_names[idx]]
            else:
                new_table.add_columns(data.column_names[idx], data.dtypes[idx], data.dlength[idx],
                                      data.nullable[idx] & (not is_p), is_p, is_f, "", "")
        my_db = db.DB()
        my_db.open(DB_PATH + data.table_name + DB_EXTENSION, db.DB_HASH, db.DB_CREATE)
        my_db.close()

        my_s.add_table(new_table)

        my_s.save_schema()

        print(PROMPT_PREFIX + f" '{data.table_name}' table is created")

    elif data.query_type == "DROP TABLE":
        os.remove(DB_PATH + data.table_name + DB_EXTENSION)
        my_s.remove_table(data.table_name)

        my_s.save_schema()

        print(PROMPT_PREFIX + f" '{data.table_name}' table is dropped")

    elif data.query_type in ['DESCRIBE', 'DESC', 'EXPLAIN']:
        print('-----------------------------------------------------------------')
        print(f'table_name {data.table_name}')
        print("{:<15} {:<8} {:<8} {:<8}".format('column_name', 'type', 'null', 'key'))
        for col in my_s.tables[data.table_name].column.values():
            print("{:<15} {:<8} {:<8} {:<8}".format(col.column_name, col.get_type(),
                                               "Y" if col.nullable else "N", col.get_key_type()))
        print('-----------------------------------------------------------------')

    elif data.query_type == "SHOW TABLES":
        print('------------------------')
        for t_name in my_s.table_names:
            print(t_name)
        print('------------------------')

    elif data.query_type == 'INSERT':
        my_db = db.DB()
        my_db.open(DB_PATH + data.table_name + DB_EXTENSION, db.DB_HASH)

        value = ''
        key = ''
        for idx in range(len(my_s.tables[data.table_name].column_names)):
            value += data.values[my_s.tables[data.table_name].column_names[idx]] + ';'

        for idx in range(len(my_s.tables[data.table_name].primary_key)):
            key += data.values[my_s.tables[data.table_name].primary_key[idx]] + ';'

        value = value.encode()
        key = key.encode()

        my_s.tables[data.table_name].elem_count += 1

        if key == b'':
            key = str(my_s.tables[data.table_name].elem_count).encode()

        my_db.put(key, value)

        my_db.close()
        print(PROMPT_PREFIX + ' The row is inserted')

    elif data.query_type == 'SELECT':
        record = Record(data.select_table, data.conditions)
        record.operate(operation)
        
        if len(data.select_columns) == 0:
            for elem in record.col_names:
                x = elem.split('.')
                data.select_columns.append((x[0], x[1]))
        
        len_list = []
        tot_name_list = []
        column_format = []
        value_format = []
        for (t_name, c_name) in data.select_columns:
            tot_name = '.'.join([t_name, c_name])
            tot_name_list.append(tot_name)
            dlength = my_s.tables[t_name].column[c_name].data_length
            dlength = max([dlength, len(tot_name), 8]) + 2
            len_list.append(dlength)
            column_format.append(f'{{:^{dlength}}}')
            value_format.append(f'{{:<{dlength}}}')


        bar = '+' + '+'.join(['-' * i for i in len_list]) + '+'
        print(bar)
        print('|' + '|'.join([column_format[idx].format(name.upper()) for (idx, name) in enumerate(tot_name_list)]) + '|')
        print(bar)

        for x in record.data:
            print('|' + '|'.join([value_format[idx].format(str(x[record.col_names[name]])) for (idx, name) in enumerate(tot_name_list)]) + '|')

        print(bar)
    
    elif data.query_type == 'DELETE':
        record = Record([data.table_name], data.conditions)
        record.operate(operation)

        cnt = 0

        my_db = db.DB()
        my_db.open(DB_PATH + data.table_name + DB_EXTENSION, db.DB_HASH)

        cursor = my_db.cursor()
        while x := cursor.next():
            if record.check_data_included(x, data.table_name):
                cursor.delete()
                cnt += 1

        my_s.tables[data.table_name].elem_count -= cnt

        my_db.close()
        print(PROMPT_PREFIX + f' {cnt} row(s) is inserted')
    
    else:
        print(data.query_type)


program_end = True  # program end trigger
MyTrans = MyTransformer(sch=my_s)
where_clause = ""

# Project 1-1 3rd section main loop
while program_end:
    input_query = get_input()

    for i in range(len(input_query)):
        my_db = db.DB()
        try:
            output = sql_parser.parse(input_query[i])
        except Exception as e:
            print(PROMPT_PREFIX, "Syntax error")  # if error occur during querying, print Syntax error
            break
        else:
            MyTrans.reset()
            ret = MyTrans.transform(output)

            if ret == EXIT_STR:
                my_s.save_schema()
                program_end = False
                break

            elif MyTrans.error.error:
                print(PROMPT_PREFIX, error_message(MyTrans.error))
                break

            else:
                where_clause = where_clasue_parser(input_query[i])
                handle_request(MyTrans.data, where_clause)
