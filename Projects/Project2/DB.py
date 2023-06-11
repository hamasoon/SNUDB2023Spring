import pandas as pd
import numpy as np
import pymysql
from sqlalchemy import create_engine

class Database:
    __instance = None
      
      
    @classmethod
    def __getInstance(cls):
        return cls.__instance


    @classmethod
    def instance(cls, *args, **kargs):
        cls.__instance = cls(*args, **kargs)
        cls.instance = cls.__getInstance
        return cls.__instance
    

    def __init__(self) -> None:
        self.connection = None
        self.make_connection()
        
    
    def __del__(self) -> None:
        self.connection.close()
        
        
    def make_connection(self) -> None:
        self.connection = pymysql.connect(
            host='astronaut.snu.ac.kr',
            port=7000,
            user='DB2019_14355',
            password='DB2019_14355',
            db='DB2019_14355',
            charset='utf8')
    
    
    # Delete all table in database
    def reset_database(self) -> None:
        with self.connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS Book")
            cursor.execute("DROP TABLE IF EXISTS Movie")
            cursor.execute("DROP TABLE IF EXISTS Person")
    
    # Define Schema -> specific schema design is described in report
    # Table1 Movie : title, director, price -> PK(title) 
    # Table2 Person : name, age, class -> PK(name, age)
    # Table3 Book : mov_id, person_id, reserve_price, rating -> PK(title, name), FK(title, name)
    def initialize_database(self) -> None:
        self.reset_database()
        
        with self.connection.cursor() as cursor:
            # Create tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Movie (
                    ID INT NOT NULL AUTO_INCREMENT,
                    title VARCHAR(100) NOT NULL,
                    director VARCHAR(100) NOT NULL,
                    price INT NOT NULL,
                    PRIMARY KEY (ID),
                    CHECK (price >= 0 AND price <= 100000)
                )""")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Person (
                    ID INT NOT NULL AUTO_INCREMENT,
                    name VARCHAR(100) NOT NULL,
                    age INT NOT NULL,
                    class VARCHAR(100) NOT NULL,
                    PRIMARY KEY (ID),
                    CHECK (age >= 12 AND age <= 110)
                )""")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Book (
                    mov_id INT NOT NULL,
                    person_id INT NOT NULL,
                    reserve_price FLOAT NOT NULL,
                    rating INT,
                    PRIMARY KEY (mov_id, person_id),
                    FOREIGN KEY (mov_id) REFERENCES Movie(ID) ON DELETE CASCADE,
                    FOREIGN KEY (person_id) REFERENCES Person(ID) ON DELETE CASCADE,
                    CHECK (reserve_price >= 0 AND reserve_price <= 100000),
                    CHECK (rating >= 1 AND rating <= 5)
                )""")
        
        # Insert data from csv file
        self.loading_csv()
            
    # Insert data from csv file into database
    def loading_csv(self) -> None:
        # loading csv file
        pd.set_option('mode.chained_assignment',  None)
        raw_data = pd.read_csv('data.csv')

        # split data into 3 tables (movie, person, book)
        # drop_duplicates() is used to remove duplicate data(indicate subset to remove duplicate data based on primary key of each table)
        movie_table = raw_data[['title', 'director', 'price']].drop_duplicates(subset='title').reset_index(drop=True)
        person_table = raw_data[['name', 'age', 'class']].drop_duplicates(subset=['name', 'age']).reset_index(drop=True)
        book_table = raw_data[['title', 'name']].drop_duplicates().reset_index(drop=True)
        
        # insert data into database
        # we don't need extra check for data beacasue we already specified constraints when create tables
        with self.connection.cursor() as cursor:
            for row in movie_table.values:
                title, director, price = row
                self.insert_movie(title, director, price, True)
            for row in person_table.values:
                name, age, customer_class = row
                self.insert_user(name, age, customer_class, True)
            for row in book_table.values:
                title, name = row
                self.insert_book_with_name(title, name, True)
    
    # check movie exists in database using title
    def movie_exists_title(self, title, is_first = False) -> bool:
        with self.connection.cursor() as cursor:
            cursor.execute('SELECT COUNT(ID) FROM Movie WHERE title = %s', title)
            result = cursor.fetchone()
            if result is None or result[0] == 0:
                return False
            else:
                return True
    
    # check movie exists in database using movie ID
    def movie_exists_id(self, ID) -> bool:
        with self.connection.cursor() as cursor:
            try:
                cursor.execute('SELECT COUNT(ID) FROM Movie WHERE ID = %s', ID)
                result = cursor.fetchone()
                if result is None or result[0] == 0:
                    return False
                else:
                    return True
            # Exception handling for non-integer input
            except pymysql.err.DataError:
                print('Movie ID should be an integer')
                return False
    
    # check user exists in database using name and age
    def user_exists_name(self, name, age, is_first = False) -> bool:
        with self.connection.cursor() as cursor:
            try:
                cursor.execute('SELECT COUNT(ID) FROM Person WHERE name = %s AND age = %s', (name, age))
                result = cursor.fetchone()
                # if result is 0, there is no user with given name and age
                if result is None or result[0] == 0:
                    return False
                else:
                    return True
            except pymysql.err.DataError:
                if not is_first:
                    print('User age should be an integer')
                return False
    
    # check user exists in database using user ID
    def user_exists_id(self, ID) -> bool:
        with self.connection.cursor() as cursor:
            try:
                cursor.execute('SELECT COUNT(ID) FROM Person WHERE ID = %s', ID)
                result = cursor.fetchone()
                if result is None or result[0] == 0:
                    return False
                else:
                    return True
            except pymysql.err.DataError:
                print('User ID should be an integer')
                return False
            
    # check book exists in database using movie ID and user ID
    def book_exists(self, mov_id, person_id, is_first = False) -> bool:
        with self.connection.cursor() as cursor:
            try:
                cursor.execute('SELECT COUNT(*) FROM Book WHERE mov_id = %s AND person_id = %s', (mov_id, person_id))
                result = cursor.fetchone()
                if result[0] == 0:
                    return False
                else:
                    return True
            except pymysql.err.DataError:
                if not is_first:
                    print('Movie ID and User ID should be an integer')
                return False
    
    # insert movie into database
    def insert_movie(self, title, director, price, is_first = False) -> None:
        with self.connection.cursor() as cursor:
            # Check if movie already exists
            if self.movie_exists_title(title, is_first):
                if not is_first:
                    print(f'Movie {title} already exists')
                return
            
            # insert data into database
            try:
                cursor.execute('INSERT INTO Movie (title, director, price) VALUES (%s, %s, %s)', (title, director, price))
                self.connection.commit()
            # Exception handling for non-integer input
            except pymysql.err.DataError:
                if not is_first:
                    print('Movie price should be from 0 to 100000')
                return
            # Exception handling for invalid input
            except pymysql.err.OperationalError:
                if not is_first:
                    print('Movie price should be from 0 to 100000')
                return

        # success message
        if not is_first:
            print('One movie successfully inserted')
        
    def insert_user(self, name, age, user_class, is_first = False) -> None:
        with self.connection.cursor() as cursor:
            # Check if user already exists
            if self.user_exists_name(name, age, is_first):
                if not is_first:
                    print(f'User {name} already exists')
                return
            
            # user class should be basic, premium or vip
            if user_class == 'basic' or user_class == 'premium' or user_class == 'vip':
                try:
                    cursor.execute('INSERT INTO Person (name, age, class) VALUES (%s, %s, %s)', (name, age, user_class))
                    self.connection.commit()
                # Exception handling for non-integer age
                except pymysql.err.DataError:
                    if not is_first:
                        print('User age should be from 12 to 110')
                    return
                # Exception handling for invalid age
                except pymysql.err.OperationalError:
                    if not is_first:
                        print('User age should be from 12 to 110')
                    return
            else:
                if not is_first:
                    print('User class should be basic, premium or vip')

        # success message
        if not is_first:
            print('One user successfully inserted')
    
    # insert book into database
    def insert_book_with_name(self, title, name, is_first = False) -> None:
        with self.connection.cursor() as cursor:
            mov_id = 0
            user_id = 0
            price = 0
            customer_class = ""
            
            try:
                cursor.execute("SELECT ID, price FROM Movie WHERE title = %s", title)
                
                result = cursor.fetchone()
                if result[0] == None:
                    # error message
                    if not is_first:
                        print(f'Movie {title} does not exist')
                    return
                else :
                    mov_id, price = result[0], result[1]
            except pymysql.err:
                if not is_first:
                    print(f'Movie {title} does not exist')
                return
            
            try:
                cursor.execute("SELECT ID, class FROM Person WHERE name = %s", name)
                
                result = cursor.fetchone()
                if result[0] == None:
                    # error message
                    if not is_first:
                        print(f'User {name} does not exist')
                    return
                else:
                    user_id, customer_class = result[0], result[1]
            except pymysql.err:
                if not is_first:
                    print(f'User {name} does not exist')
                return
            
            self.insert_book(mov_id, user_id, price, customer_class, is_first)
            
            
    def insert_book_with_id(self, mov_id, user_id, is_first = False) -> None:
        with self.connection.cursor() as cursor:
            price = 0
            customer_class = ""
            
            # Check validation of input, movie existence and get price
            # To get price, doesn't use my_db.movie_exists_id() because it returns boolean
            try:
                cursor.execute("SELECT price FROM Movie WHERE ID = %s", mov_id)
            except pymysql.err.DataError:
                if not is_first:
                    print(f'Movie {mov_id} does not exist')
                return
            
            result = cursor.fetchone()
            if result == None:
                # error message
                if not is_first:
                    print(f'Movie {mov_id} does not exist')
                return
            else:
                price = result[0]

            # Check validation of input, user existence and get class
            # To get class, doesn't use my_db.user_exists_id() because it returns boolean
            try:
                cursor.execute("SELECT class FROM Person WHERE ID = %s", user_id)
            except pymysql.err.DataError:
                if not is_first:
                    print(f'User {user_id} does not exist')
                return
            
            result = cursor.fetchone()
            if result == None:
                if not is_first:
                    print(f'User {user_id} does not exist')
                return
            else:
                customer_class = result[0]
            
            self.insert_book(mov_id, user_id, price, customer_class, is_first)
            
    def insert_book(self, mov_id, user_id, price, customer_class, is_first = False) -> None:
        with self.connection.cursor() as cursor:
            # Check same booking already exist
            if self.book_exists(mov_id, user_id):
                if not is_first:
                    print(f'User {user_id} already booked movie {mov_id}')
                return
            
            # check movie is fully booked
            cursor.execute("SELECT COUNT(*) FROM Book WHERE mov_id = %s", mov_id)
            result = cursor.fetchone()
            if result[0] >= 10:
                if not is_first:
                    print(f'Movie {mov_id} has already been fully booked')
                return
            
            # calculate price based on customer class
            if customer_class == 'premium':
                price = int(price * 0.75)
            elif customer_class == 'vip':
                price = int(price * 0.5)
            
            cursor.execute("INSERT INTO Book (mov_id, person_id, reserve_price) VALUES (%s, %s, %s)", (mov_id, user_id, price))
            self.connection.commit()

        # success message
        if not is_first:
            print('Movie successfully booked')