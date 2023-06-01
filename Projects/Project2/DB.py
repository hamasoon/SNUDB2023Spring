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
    
    
    # Define Schema -> specific schema design is described in report
    # Table1 Movie : title, director, price -> PK(title) 
    # Table2 Person : name, age, class -> PK(name, age)
    # Table3 Book : mov_id, person_id, reserve_price, rating -> PK(title, name), FK(title, name)
    def initialize_database(self) -> None:
        self.make_connection()
        
        with self.connection.cursor() as cursor:
            # Drop tables if exists
            cursor.execute("DROP TABLE IF EXISTS Book")
            cursor.execute("DROP TABLE IF EXISTS Movie")
            cursor.execute("DROP TABLE IF EXISTS Person")
            
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
                    reserve_price INT NOT NULL,
                    rating INT,
                    PRIMARY KEY (mov_id, person_id),
                    FOREIGN KEY (mov_id) REFERENCES Movie(ID),
                    FOREIGN KEY (person_id) REFERENCES Person(ID),
                    CHECK (reserve_price >= 0 AND reserve_price <= 100000),
                    CHECK (rating >= 1 AND rating <= 5)
                )""")
        
        self.connection.close()
        
        # Insert data from csv file
        self.loading_csv()
            
        self.make_connection()

    
    def loading_csv(self) -> None:
        pd.set_option('mode.chained_assignment',  None)
        raw_data = pd.read_csv('data.csv')

        self.movie_table = raw_data[['title', 'director', 'price']].drop_duplicates().reset_index(drop=True)
        self.person_table = raw_data[['name', 'age', 'class']].drop_duplicates().reset_index(drop=True)
        self.book_table = raw_data[['title', 'name']].drop_duplicates().reset_index(drop=True)

        self.book_table['title'] = self.book_table['title'].map(lambda x: self.movie_table[self.movie_table['title'] == x].index[0] + 1)
        self.book_table['name'] = self.person_table['name'].map(lambda x: self.person_table[self.person_table['name'] == x].index[0] + 1)
        self.book_table[['reserve_price', 'rating']] = None

        for idx, elem in self.book_table[['title', 'name']].iterrows():
            price = self.movie_table['price'][elem['title']-1]
            customer_class = self.person_table['class'][elem['name']-1].lower()

            if customer_class == 'vip':
                price = int(price/2)
            elif customer_class == 'premium':
                price = int(price*3/4)
                
            self.book_table['reserve_price'][idx] = price
            
        self.book_table.rename(columns = {"title": "mov_id", "name": "person_id"}, inplace = True)
        
        # 
        engine = create_engine("mysql+pymysql://DB2019_14355:DB2019_14355@astronaut.snu.ac.kr:7000/DB2019_14355", encoding='utf-8')
        db_connection = engine.connect()
        
        self.movie_table.to_sql(name='Movie', con=db_connection, if_exists='append', index=False)  
        self.person_table.to_sql(name='Person', con=db_connection, if_exists='append', index=False)  
        self.book_table.to_sql(name='Book', con=db_connection, if_exists='append', index=False)
        
        db_connection.close()
            
        