import pymysql


connection = pymysql.connect(
    host='astronaut.snu.ac.kr',
    port=7000,
    user='DB2019_14355',
    password='DB2019_14355',
    db='DB2019_14355',
    charset='utf8')

with connection.cursor() as cursor:
    cursor.execute("show tables")
    result = cursor.fetchall()
    print(result)
    
connection.close()