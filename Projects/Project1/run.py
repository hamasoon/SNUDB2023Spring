import pickle
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

if os.path.exists(SCHEMA_DATA):
    with open(SCHEMA_DATA, "rb") as fr:
        my_s = pickle.load(fr)

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


def handle_request(data: ParsedData):
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

        if key == '':
            key = str(my_s.tables[data.table_name].elem_count).encode()

        my_db.put(key, value)

        my_db.close()
        print(PROMPT_PREFIX + ' The row is inserted')

    elif data.query_type == 'SELECT':
        my_db.open(DB_PATH + data.table_name + DB_EXTENSION, db.DB_HASH)
        column_names = my_s.tables[data.table_name].column_names

        len_list = []
        column_format = []
        value_format = []
        for name in column_names:
            dlength = my_s.tables[data.table_name].column[name].data_length
            dlength = (8 if len(name) + 2 < 8 else len(name) + 2) if len(name) + 2 > dlength \
                else (8 if dlength + 2 < 8 else dlength + 2)
            len_list.append(dlength)
            column_format.append(f'{{:^{dlength}}}')
            value_format.append(f'{{:<{dlength}}}')


        bar = '+' + '+'.join(['-' * i for i in len_list]) + '+'
        print(bar)
        print('|' + '|'.join([column_format[i].format(column_names[i].capitalize()) for i in range(len(column_names))]) + '|')
        print(bar)

        cursor = my_db.cursor()
        while x := cursor.next():
            values = x[1].decode().split(';')[:-1]
            print('|' + '|'.join([value_format[i].format(values[i]) for i in range(len(values))]) + '|')

        print(bar)

        my_db.close()
    else:
        print(data.query_type)


program_end = True  # program end trigger
MyTrans = MyTransformer(sch=my_s)

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
                program_end = False
                break

            elif MyTrans.error.error:
                print(PROMPT_PREFIX, error_message(MyTrans.error))

            else:
                handle_request(MyTrans.data)
