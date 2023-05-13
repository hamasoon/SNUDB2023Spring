from berkeleydb import db
from utils import DB_PATH, DB_EXTENSION

test_list = ['123.123', '234.234', '345.345']
test_list = [elem.split('.') for elem in test_list]
print(test_list)

# my_DB = db.DB()

# my_DB.open(DB_PATH + "ref" + DB_EXTENSION, db.DB_HASH)

# cursor = my_DB.cursor()
# while x := cursor.next():
#     print(x)