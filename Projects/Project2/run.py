import pymysql
import numpy as np
from DB import Database

my_db = Database.instance()

def initialize_database():
    my_db.initialize_database()

    print('Database successfully initialized')

# Problem 15 (5 pt.)
def reset():
    agreement = input('Are you sure? (y/n) ').lower()
    
    if agreement == 'y':
        my_db.reset_database()
        print('Database successfully reset')
    else:
        print('Database reset aborted')

# Problem 2 (4 pt.)
# 영화 ID, 제목, 감독, 원래 가격, 평균 예매 가격, 예매자 수, 평균 평점 순으로 출력한다.
def print_movies():
    with my_db.connection.cursor() as cursor:
        # get all movies
        cursor.execute('''
            SELECT Movie.ID, Movie.title, Movie.director, Movie.price, AVG(Book.reserve_price), Count(Book.person_id), AVG(Book.rating)
            FROM Movie LEFT OUTER JOIN Book ON Movie.ID = Book.mov_id 
            GROUP BY Movie.ID
            ORDER BY ID ASC
            ''')
        result = cursor.fetchall()
        print('+' + '-' * 5 + '+' + '-' * 70 + '+' + '-' * 35 + '+' + '-' * 15 + '+' + '-' * 15 + '+' + '-' * 15 + '+' + '-' * 15 + '+')
        print(str.format('|{:^5}|{:^70}|{:^35}|{:^15}|{:^15}|{:^15}|{:^15}|', \
            'ID', 'TITLE', 'DIRECTOR', 'ORIGIN PRICE', 'AVG BOOK PRICE', 'COUNT BOOK', 'AVG RATING'))
        print('+' + '-' * 5 + '+' + '-' * 70 + '+' + '-' * 35 + '+' + '-' * 15 + '+' + '-' * 15 + '+' + '-' * 15 + '+' + '-' * 15 + '+')
        for id, title, director, origin_price, avg_price, book_count, avg_rating in result:
            if avg_rating == None:
                avg_rating = "None"
            if avg_price == None:
                avg_price = "None"
            else:
                avg_price = int(avg_price)
            
            print(f'|{id:<5}|{title:<70}|{director:<35}|{origin_price:<15}|{avg_price:<15}|{book_count:<15}|{avg_rating:<15}|')
        print('+' + '-' * 5 + '+' + '-' * 70 + '+' + '-' * 35 + '+' + '-' * 15 + '+' + '-' * 15 + '+' + '-' * 15 + '+' + '-' * 15 + '+')

# Problem 3 (3 pt.)
def print_users():
    with my_db.connection.cursor() as cursor:
        # get all users
        cursor.execute('SELECT * FROM Person ORDER BY ID ASC')
        result = cursor.fetchall()
        print('+' + '-' * 5 + '+' + '-' * 40 + '+' + '-' * 20 + '+' + '-' * 20 + '+')
        print(str.format('|{:^5}|{:^40}|{:^20}|{:^20}|', 'id', 'name', 'age', 'class'))
        print('+' + '-' * 5 + '+' + '-' * 40 + '+' + '-' * 20 + '+' + '-' * 20 + '+')
        for id, name, age, customer_class in result:
            print(f'|{id:<5}|{name:<40}|{age:<20}|{customer_class:<20}|')
        print('+' + '-' * 5 + '+' + '-' * 40 + '+' + '-' * 20 + '+' + '-' * 20 + '+')

    pass

# Problem 4 (4 pt.)
def insert_movie():
    # YOUR CODE GOES HERE
    title = input('Movie title: ')
    director = input('Movie director: ')
    price = input('Movie price: ')
    
    my_db.insert_movie(title, director, price)
    

# Problem 6 (4 pt.)
def remove_movie():
    movie_id = input('Movie ID: ')
    
    with my_db.connection.cursor() as cursor:
        # Check if movie exists
        if not my_db.movie_exists_id(movie_id):
            print(f'Movie {movie_id} does not exist')
            return
        
        cursor.execute('DELETE FROM Movie WHERE ID = %s', movie_id)
        my_db.connection.commit()

    # success message
    print('One movie successfully removed')
    
    
# Problem 5 (4 pt.)
def insert_user():
    # YOUR CODE GOES HERE
    name = input('User name: ')
    age = input('User age: ')
    customer_class = input('User class: ')
    if customer_class == 'basic' or customer_class == 'premium' or customer_class == 'vip':
        my_db.insert_user(name, age, customer_class)
    else:
        print('User class should be basic, premium or vip')
        return

# Problem 7 (4 pt.)
def remove_user():
    user_id = input('User ID: ')

    with my_db.connection.cursor() as cursor:
        # Check if user exists
        if not my_db.user_exists_id(user_id):
            print(f'User {user_id} does not exist')
            return
        
        cursor.execute('DELETE FROM Person WHERE ID = %s', user_id)
        my_db.connection.commit()

    print('One user successfully removed')


# Problem 8 (5 pt.)
def book_movie():
    # Get movie ID and user ID
    movie_id = input('Movie ID: ')
    user_id = input('User ID: ')
    
    my_db.insert_book_with_id(movie_id, user_id)

# Problem 9 (5 pt.)
def rate_movie():
    # Handle invalid inputs
    movie_id = input('Movie ID: ')
    user_id = input('User ID: ')
    rating = input('Ratings (1~5): ')

    with my_db.connection.cursor() as cursor:
        # Check if movie and user exist
        if not my_db.movie_exists_id(movie_id):
            print(f'Movie {movie_id} does not exist')
            return
        
        if not my_db.user_exists_id(user_id):
            print(f'User {user_id} does not exist')
            return
        
        try:
            # Check if rating is valid
            cursor.execute('SELECT rating FROM Book WHERE mov_id = %s AND person_id = %s', (movie_id, user_id))
            result = cursor.fetchone()
            # Data doesn't exist
            if result == None:
                print(f'User {user_id} has not booked movie {movie_id} yet')
                return
            # Data exists but rating is None -> update rating
            elif result[0] is None:
                try:
                    cursor.execute('UPDATE Book SET rating = %s WHERE mov_id = %s AND person_id = %s', (rating, movie_id, user_id))
                    my_db.connection.commit()
                # Handle invalid rating input
                except pymysql.err.DataError:
                    print('Rating should be an integer')
                    return
                except pymysql.err.OperationalError:
                    print('Rating should be from 1 to 5')
                    return
            # Data exists and rating is not None
            else:
                print(f'User {user_id} has already rated movie {movie_id}')
                return
        except pymysql.err.OperationalError:
            print(f'User {user_id} has not booked movie {movie_id} yet')
            return

    print('Movie successfully rated')


# Problem 10 (5 pt.)
def print_users_for_movie():
    movie_id = input('Movie ID: ')

    with my_db.connection.cursor() as cursor:
        # Check if movie exists
        if not my_db.movie_exists_id(movie_id):
            print(f'Movie {movie_id} does not exist')
            return
        
        try:
            # Using INNER JOIN to get all users who booked the movie
            cursor.execute('''
            SELECT DISTINCT Person.ID, Person.name, Person.age, Book.reserve_price, Book.rating
            FROM Person
            INNER JOIN Book ON Person.ID = Book.person_id
            WHERE Book.mov_id = %s
            ORDER BY Person.ID ASC
            ''', movie_id)
            result = cursor.fetchall()
            print('+' + '-' * 5 + '+' + '-' * 40 + '+' + '-' * 15 + '+' + '-' * 15 + '+' + '-' * 15 + '+')
            print(str.format('|{:^5}|{:^40}|{:^15}|{:^15}|{:^15}', 'ID', 'NAME', 'AGE', 'BOOK PRICE', 'RATING'))
            print('+' + '-' * 5 + '+' + '-' * 40 + '+' + '-' * 15 + '+' + '-' * 15 + '+' + '-' * 15 + '+')
            for id, name, age, price, rating in result:
                if rating == None:
                    rating = 'None'
                print(f'|{id:^5}|{name:^40}|{age:^15}|{price:^15}|{rating:^15}')
            print('+' + '-' * 5 + '+' + '-' * 40 + '+' + '-' * 15 + '+' + '-' * 15 + '+' + '-' * 15 + '+')
        # Handle invalid movie ID input
        except pymysql.err.DataError:
            print('Movie ID should be an integer')
            return


# Problem 11 (5 pt.)
def print_movies_for_user():
    user_id = input('User ID: ')

    with my_db.connection.cursor() as cursor:
        # Check if user exists
        if not my_db.user_exists_id(user_id):
            print(f'User {user_id} does not exist')
            return
        
        try:
            # Using INNER JOIN to get movies that user has booked
            cursor.execute('''
                SELECT DISTINCT Movie.ID, Movie.title, Movie.director, Book.reserve_price, Book.rating
                FROM Movie INNER JOIN Book ON Movie.ID = Book.mov_id
                WHERE Book.person_id = %s
                ORDER BY Movie.ID ASC
            ''', user_id)
            result = cursor.fetchall()
            print('+' + '-' * 5 + '+' + '-' * 70 + '+' + '-' * 35 + '+' + '-' * 15 + '+' + '-' * 15 + '+')
            print(str.format('|{:^5}|{:^70}|{:^35}|{:^15}|{:^15}', 'ID', 'TITLE', 'DIRECTOR', 'BOOK PRICE', 'RATING'))
            print('+' + '-' * 5 + '+' + '-' * 70 + '+' + '-' * 35 + '+' + '-' * 15 + '+' + '-' * 15 + '+')
            for id, title, director, price, rating in result:
                if rating == None:
                    rating = 'None'
                print(f'|{id:^5}|{title:^70}|{director:^35}|{price:^15}|{rating:^15}')
            print('+' + '-' * 5 + '+' + '-' * 70 + '+' + '-' * 35 + '+' + '-' * 15 + '+' + '-' * 15 + '+')
        # Handle invalid user ID input
        except pymysql.err.DataError:
            print('User ID should be an integer')
            return
        
        
# Problem 12 (6 pt.)
def recommend_popularity():
    user_id = input('User ID: ')
    
    with my_db.connection.cursor() as cursor:
        # Check if user exists
        if not my_db.user_exists_id(user_id):
            print(f'User {user_id} does not exist')
            return
        
        # Using subquery to get movies that user has booked
        # Then grouping and ordering by average rating and movie ID
        cursor.execute('''
            SELECT Movie.ID, Movie.title, AVG(Book.reserve_price), COUNT(Book.reserve_price), AVG(Book.rating)
            FROM Movie JOIN Book ON Movie.ID = Book.mov_id
            WHERE Movie.ID NOT IN (
                SELECT Movie.ID
                FROM Movie JOIN Book ON Movie.ID = Book.mov_id
                WHERE Book.person_id = %s
            )
            GROUP BY Movie.ID
            ORDER BY AVG(Book.rating) DESC, Movie.ID ASC
            LIMIT 1
        ''', user_id)
        
        result = cursor.fetchone()
        if result != None:
            id, title, price, popularity, rating = result
            if rating == None:
                rating = 'None'
            print('-' + '-' * 5 + '-' + '-' * 70 + '-' + '-' * 15 + '-' + '-' * 15 + '-' + '-' * 15 + '-')
            print("Rating-based")
            print(str.format('|{:^5}|{:^70}|{:^15}|{:^15}|{:^15}', 'ID', 'TITLE', 'AVG PRICE', 'POPULARITY', 'RATING'))
            print('+' + '-' * 5 + '+' + '-' * 70 + '+' + '-' * 15 + '+' + '-' * 15 + '+' + '-' * 15 + '+')
            print(f'|{id:^5}|{title:^70}|{price:^15}|{popularity:^15}|{rating:^15}')
            print('+' + '-' * 5 + '+' + '-' * 70 + '+' + '-' * 15 + '+' + '-' * 15 + '+' + '-' * 15 + '+')
        
        # Using subquery to get movies that user has booked
        # Then grouping and ordering by number of bookings and movie ID
        cursor.execute('''
            SELECT Movie.ID, Movie.title, AVG(Book.reserve_price), COUNT(Book.reserve_price), AVG(Book.rating)
            FROM Movie JOIN Book ON Movie.ID = Book.mov_id
            WHERE Movie.ID NOT IN (
                SELECT Movie.ID
                FROM Movie JOIN Book ON Movie.ID = Book.mov_id
                WHERE Book.person_id = %s
            )
            GROUP BY Movie.ID
            ORDER BY COUNT(*) DESC, Movie.ID ASC
            LIMIT 1
        ''', user_id)
        
        result = cursor.fetchone()
        if result != None:
            id, title, price, popularity, rating = result
            if rating == None:
                rating = 'None'
            print("Popularity-based")
            print(str.format('|{:^5}|{:^70}|{:^15}|{:^15}|{:^15}', 'ID', 'TITLE', 'AVG PRICE', 'POPULARITY', 'RATING'))
            print('+' + '-' * 5 + '+' + '-' * 70 + '+' + '-' * 15 + '+' + '-' * 15 + '+' + '-' * 15 + '+')
            print(f'|{id:^5}|{title:^70}|{price:^15}|{popularity:^15}|{rating:^15}')
            print('+' + '-' * 5 + '+' + '-' * 70 + '+' + '-' * 15 + '+' + '-' * 15 + '+' + '-' * 15 + '+')


# Problem 13 (10 pt.)
def recommend_item_based():
    # YOUR CODE GOES HERE
    try:
        user_id = int(input('User ID: '))
    except ValueError:
        print('User ID should be an integer')
    
    try:
        rec_count = int(input('Recommend Count: '))
    except ValueError:
        print('Recommend Count should be an integer')
    
    with my_db.connection.cursor() as cursor:
        if not my_db.user_exists_id(user_id):
            print(f'User {user_id} does not exist')
            return
        
        # Check if user has rated any movie
        cursor.execute('''
            SELECT COUNT(*)
            FROM Book
            WHERE person_id = %s AND rating IS NOT NULL    
            ''', user_id)
        if cursor.fetchone()[0] == 0:
            print("Rating does not exist")
            return
        
        # get maximum ID of movie and user(due to MAX(ID) != COUNT(ID))
        cursor.execute("SELECT MAX(ID) FROM Person")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT MAX(ID) FROM Movie")
        movie_count = cursor.fetchone()[0]
        
        # create rating table matrix(User x Movie) and fill with nan
        item_table = np.zeros((user_count, movie_count))
        item_table[:] = np.nan

        # get all rating data
        cursor.execute('''
            SELECT *
            FROM Book
            ''')
        
        result = cursor.fetchall()
        for mov_id, person_id , _, rating in result:
            # fill rating table with rating data if rating is exist
            if rating != None and rating > 0.5:
                item_table[person_id-1][mov_id-1] = rating
    
        # get movie_id index that user has not watched
        target_index = np.where(np.isnan(item_table[user_id-1]))
        item_table = np.nan_to_num(item_table)

        col_mean = np.nanmean(item_table, axis=0)
        inds = np.where(np.isnan(item_table))
        item_table[inds] = np.take(col_mean, inds[1])
        
        test = np.mean(item_table, axis=0)
        
        sim_data = np.round(consine_similiarity_array(np.transpose(np.copy(item_table)), np.mean(item_table), movie_count), 4)
        
        result_array = np.ndarray(movie_count)
        
        for i in range(len(result_array)):
            if i not in target_index[0]:
                result_array[i] = -1000
            else:
                weight_dot_product = np.dot(sim_data[i], item_table[user_id-1]) - item_table[user_id-1][i]
                weight_sum = np.sum(sim_data[i]) - 1
                result_array[i] = weight_dot_product / weight_sum
        
        print('-' + '-' * 5 + '-' + '-' * 70 + '-' + '-' * 15 + '-' + '-' * 15 + '-' + '-' * 15 + '-')
        print("Item-based")
        print(str.format('|{:^5}|{:^70}|{:^15}|{:^15}|{:^15}', 'ID', 'TITLE', 'AVG PRICE', 'AVG RATING', 'PREDICTED RATING'))
        print('+' + '-' * 5 + '+' + '-' * 70 + '+' + '-' * 15 + '+' + '-' * 15 + '+' + '-' * 15 + '+')
        
        iterate_count = 0
        
        #can't use for Loop becuse sometime movie ID is not exist due to deletion
        while iterate_count < rec_count:
            max_index = np.argmax(result_array)
            predicted_rating = np.round(result_array[max_index], 2)
            if (predicted_rating == -1000):
                break
            result_array[max_index] = -1000
            
            cursor.execute('''
                SELECT Movie.ID, Movie.title, AVG(Book.reserve_price), AVG(Book.rating)
                FROM Movie INNER JOIN Book ON Movie.ID = Book.mov_id
                WHERE Movie.ID = %s
                GROUP BY Movie.ID
                ''', max_index + 1)
                
            result = cursor.fetchone()
            if result != None:
                id, title, price, rating = result
                if rating == None:
                    rating = 'None'
        
                print(f'|{id:^5}|{title:^70}|{price:^15}|{rating:^15}|{predicted_rating:^15}')
                
                iterate_count += 1
        
        print('+' + '-' * 5 + '+' + '-' * 70 + '+' + '-' * 15 + '+' + '-' * 15 + '+' + '-' * 15 + '+')


def consine_similiarity_array(data: np.ndarray, tot_avg, movie_count) -> np.ndarray:
    consine_similiarity = np.zeros((movie_count, movie_count))
    
    for i in range(movie_count):
        for j in range(i, movie_count):
            if i == j:
                consine_similiarity[i][j] = 1
            else:
                consine_similiarity[i][j] = calc_cosine_similarity(data[i] - tot_avg, data[j] - tot_avg)
                consine_similiarity[j][i] = consine_similiarity[i][j]
    
    return consine_similiarity
                
def calc_cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:    
    return np.dot(a, b) / (np.sqrt(np.sum(np.square(a))) * np.sqrt(np.sum(np.square(b))))
            
    
# Total of 70 pt.
def main():
    
    while True:
        print('============================================================')
        print('1. initialize database')
        print('2. print all movies')
        print('3. print all users')
        print('4. insert a new movie')
        print('5. remove a movie')
        print('6. insert a new user')
        print('7. remove an user')
        print('8. book a movie')
        print('9. rate a movie')
        print('10. print all users who booked for a movie')
        print('11. print all movies booked by an user')
        print('12. recommend a movie for a user using popularity-based method')
        print('13. recommend a movie for a user using item-based collaborative filtering')
        print('14. exit')
        print('15. reset database')
        print('============================================================')
        try:
            menu = int(input('Select your action: '))
        except ValueError:
            print('Invalid action')

        if menu == 1:
            initialize_database()
        elif menu == 2:
            print_movies()
        elif menu == 3:
            print_users()
        elif menu == 4:
            insert_movie()
        elif menu == 5:
            remove_movie()
        elif menu == 6:
            insert_user()
        elif menu == 7:
            remove_user()
        elif menu == 8:
            book_movie()
        elif menu == 9:
            rate_movie()
        elif menu == 10:
            print_users_for_movie()
        elif menu == 11:
            print_movies_for_user()
        elif menu == 12:
            recommend_popularity()
        elif menu == 13:
            recommend_item_based()
        elif menu == 14:
            print('Bye!')
            break
        elif menu == 15:
            reset()
        else:
            print('Invalid action')


if __name__ == "__main__":
    main()