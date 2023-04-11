from itertools import chain
from lark import Lark, Transformer

# prefix for prompt like view
PROMPT_PREFIX = "DB_2019-14355>" # prompt prefix
EXIT_STR = 'exit;' # set exit
REQUESTED_STR = 'requested' # requested surfix

# Project 1-1 1st section CustomTransformer
class MyTransformer(Transformer):
    def __init__(self):
        self.query_type = "" # save query type
        self.error = False # if error occur, set self.error True

    def command(self, items): 
        if(items[0] == 'exit'): # handle exit case
            return EXIT_STR
        else:
            return self.query_type
        
    def create_table_query(self, items): # handle create table query
        self.query_type = "'CREATE TABLE'"
        return items
    
    def drop_table_query(self, items): # handle drop table query
        self.query_type = "'DROP TABLE'"
        return items
    
    def describe_query(self, items): # handle describe query
        self.query_type = "'DESCRIBE'"
        return items
    
    def explain_query(self, items): # handle explain query
        self.query_type = "'EXPLAIN'"
        return items
    
    def desc_query(self, items): # handle desc query
        self.query_type = "'DESC'"
        return items
    
    def show_tables_query(self, items): # handle show tables query
        self.query_type = "'SHOW TABLES'"
        return items
    
    def select_query(self, items): # handle select query
        self.query_type = "'SELECT'"
        return items
    
    def insert_query(self, items): # handle insert query
        self.query_type = "'INSERT'"
        return items
    
    def delete_query(self, items): # handle delete query
        self.query_type = "'DELETE'"
        return items
    
    def update_query(self, items): # handle update query
        self.query_type = "'UPDATE'"
        return items
    

# open sql_parser
with open('grammar.lark') as file:
    sql_parser = Lark(file.read(), start="command", lexer="basic")

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

program_end = True # prgram end trigger

# Project 1-1 3rd section main loop
while program_end:
    input_query = get_input()

    for i in range(len(input_query)):
        try:
            output = sql_parser.parse(input_query[i])
        except Exception as e:
            print(PROMPT_PREFIX, "Syntax error") # if error occur during querying, print Syntax error
            break
        else:
            ret = MyTransformer().transform(output)

            if ret == EXIT_STR: # if get exit command, then end program
                program_end = False
                break
            
            else:
                print(PROMPT_PREFIX, ret, REQUESTED_STR) # print output
