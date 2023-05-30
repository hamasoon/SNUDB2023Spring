import pandas as pd
import pymysql
import DB

# raw_data = pd.read_csv('data.csv')

# movie_table = raw_data[['title', 'director', 'price']].drop_duplicates().reset_index(drop=True)
# person_table = raw_data[['name', 'age', 'class']].drop_duplicates().reset_index(drop=True)
# book_table = raw_data[['title', 'name']].drop_duplicates().reset_index(drop=True)


# book_table['title'] = book_table['title'].map(lambda x: movie_table[movie_table['title'] == x].index[0] + 1)
# book_table['name'] = person_table['name'].map(lambda x: person_table[person_table['name'] == x].index[0] + 1)
# book_table[['reserve_price', 'rating']] = 0

# for idx, elem in book_table[['title', 'name']].iterrows():
#     price = movie_table['price'][elem['title']-1]
#     customer_class = person_table['class'][elem['name']-1].lower()

#     if customer_class == 'vip':
#         price = int(price/2)
#     elif customer_class == 'premium':
#         price = int(price*3/4)
        
#     book_table['reserve_price'][idx] = price
    
# print(movie_table)

my_db = DB.Database()