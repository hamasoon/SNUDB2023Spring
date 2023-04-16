import json
from lark import Lark
from transfomer import MyTransformer, EXIT_STR
from utils import *
from berkeleydb import db

# prefix for prompt like view
REQUESTED_STR = 'requested' # requested surfix


# myDB.open(DB_NAME, None, db.DB_HASH, db.DB_CREATE)
with open('table_info.json') as f:
    table_info = json.load(f)

# open sql_parser
with open('grammar.lark') as file:
    sql_parser = Lark(file.read(), start="command", lexer="basic")

my_db = db.DB()

my_s = Schema(my_db)


def error_message(e: Error):
    if e.error_type == "TableExistenceError":
        return "Create table has failed: table with the same name already exists"
    elif e.error_type == "NoSuchTable":
        return "No such table"
    else:
        return e.error_type


def handle_request(data: ParsedData):
    if data.query_type == "CREATE TABLE":
        new_table = Table(data.table_name, data.column_names, my_db)

        for idx in range(len(data.column_names)):
            is_p = data.column_names[idx] in data.primary
            is_f = data.column_names[idx] in data.foreign.keys()

            if is_f:
                new_table.add_columns(data.column_names[idx], data.dtypes[idx], data.dlength[idx],
                                      data.nullable[idx] & is_p, is_p, is_f, data.foreign[data.column_names[idx]])
            else:
                new_table.add_columns(data.column_names[idx], data.dtypes[idx], data.dlength[idx],
                                      data.nullable[idx] & is_p, is_p, is_f, "")

        new_table.create_db_file()
        my_s.add_table(new_table)

        return f"'{data.table_name}' table is created"

    elif data.query_type == "DROP TABLE":
        os.remove(DB_PATH + data.table_name + DB_EXTENSION)
        my_s.remove_table(data.table_name)
        return f"'{data.table_name}' table is dropped"

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

    else:
        return data.query_type


program_end = True  # program end trigger
MyTrans = MyTransformer(sch=my_s)

# Project 1-1 3rd section main loop
while program_end:
    input_query = get_input()

    for i in range(len(input_query)):
        try:
            output = sql_parser.parse(input_query[i])
        except Exception as e:
            print(PROMPT_PREFIX, "Syntax error")  # if error occur during querying, print Syntax error
            break
        else:
            MyTrans.reset()
            ret = MyTrans.transform(output)

            if ret == EXIT_STR:  # if get exit command, then end program
                program_end = False
                break

            elif MyTrans.error.error:
                print(PROMPT_PREFIX, error_message(MyTrans.error))

            else:
                print(handle_request(MyTrans.data))
