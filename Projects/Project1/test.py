from berkeleydb import db
import os.path

myDB = db.DB()

db_name = "test"

TABLE_NAME = "table_name"
NOT_NULL = "not null"
INT = 'int'
STR = 'str'

path = "db/"

print("fuck you : " + str(True))

# try :
#     print(bool(""))
# except :
#     print(123)

# myDB.open(db_name, db.DB_HASH, db.DB_CREATE)
# myDB.put("table_name".encode(), "column1;column2;column3;column4".encode())
# myDB.put("table_name_column1".encode(), "data_type;;is_primary;is_foreign;table_name".encode())
# myDB.put("table_name_column2".encode(), "data_type;;is_primary;is_foreign;table_name".encode())
# myDB.put("table_name_column2".encode(), "data_type;;is_primary;is_foreign;table_name".encode())
# myDB.put("table_name_column3".encode(), "data_type;not null;is_primary;is_foreign;table_name".encode())
# myDB.put("table_name_column4".encode(), "data_type;not null;is_primary;is_foreign;table_name".encode())

# columns = myDB.get("table_name".encode()).decode()
# columns = columns.split(";")

# print(columns)

# for column in columns:
#     column_data = myDB.get((TABLE_NAME+"_"+column).encode()).decode().split(";")
#     if column_data[1] == NOT_NULL:
#         column_data[1] = True
#     else:
#         column_data[1] = False
#     print(column_data)