import pymysql
from DB import Database

my_db = Database.instance()

def initialize_database():
    my_db.initialize_database()

    print('Database successfully initialized')

# Problem 15 (5 pt.)
def reset():
    agreement = input('Are you sure? (y/n) ').lower()
    
    if agreement == 'y':
        my_db.initialize_database()
        print('Database successfully reset')
    else:
        print('Database reset aborted')

# Problem 2 (4 pt.)
# 영화 ID, 제목, 감독, 원래 가격, 평균 예매 가격, 예매자 수, 평균 평점 순으로 출력한다.
def print_movies():
    with my_db.connection.cursor() as cursor:
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
    
    with my_db.connection.cursor() as cursor:
        # Check if movie already exists
        if my_db.movie_exists_title(title):
            print(f'Movie {title} already exists')
            return
        
        # Get price
        price = input('Movie price: ')
        # Check if price is valid
        try:
            cursor.execute('INSERT INTO Movie (title, director, price) VALUES (%s, %s, %s)', (title, director, price))
            my_db.connection.commit()
        except pymysql.err.DataError:
            print('Movie price should be from 0 to 100000')
            return
        except pymysql.err.OperationalError:
            print('Movie price should be from 0 to 100000')
            return

    # success message
    print('One movie successfully inserted')
    

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
    pass

# Problem 5 (4 pt.)
def insert_user():
    # YOUR CODE GOES HERE
    name = input('User name: ')
    age = input('User age: ')
    
    with my_db.connection.cursor() as cursor:
        if my_db.user_exists_name(name, age):
            # error message
            print(f'The user ({name}, {age}) already exists')
            return
        
        customer_class = input('User class: ')
        if customer_class == 'basic' or customer_class == 'premium' or customer_class == 'vip':
            try:
                cursor.execute('INSERT INTO Person (name, age, class) VALUES (%s, %s, %s)', (name, age, customer_class))
            # Check if age is valid
            except pymysql.err.DataError:
                print('User age should be an integer')
                return
            except pymysql.err.OperationalError:
                print('User age should be from 12 to 110')
                return
            
            my_db.connection.commit()
        else:
            print('User class should be basic, premium or vip')
            return
    
    # success message
    print('One user successfully inserted')
    # YOUR CODE GOES HERE
    pass

# Problem 7 (4 pt.)
def remove_user():
    # YOUR CODE GOES HERE
    user_id = input('User ID: ')

    with my_db.connection.cursor() as cursor:
        if not my_db.user_exists_id(user_id):
            # error message
            print(f'User {user_id} does not exist')
            return
        
        cursor.execute('DELETE FROM Person WHERE ID = %s', user_id)
        my_db.connection.commit()

    # success message
    print('One user successfully removed')
    pass

# Problem 8 (5 pt.)
def book_movie():
    # Get movie ID and user ID
    movie_id = input('Movie ID: ')
    user_id = input('User ID: ')
    
    with my_db.connection.cursor() as cursor:
        price = 0
        customer_class = ""
        
        # Check validation of input, movie existence and get price
        # To get price, doesn't use my_db.movie_exists_id() because it returns boolean
        try:
            cursor.execute("SELECT price FROM Movie WHERE ID = %s", movie_id)
        except pymysql.err.DataError:
            print('Movie ID should be an integer')
            return
        
        result = cursor.fetchone()
        if result == None:
            # error message
            print(f'Movie {movie_id} does not exist')
            return
        else:
            price = result[0]

        # Check validation of input, user existence and get class
        # To get class, doesn't use my_db.user_exists_id() because it returns boolean
        try:
            cursor.execute("SELECT class FROM Person WHERE ID = %s", user_id)
        except pymysql.err.DataError:
            print('User ID should be an integer')
            return
        
        result = cursor.fetchone()
        if result == None:
            print(f'User {user_id} does not exist')
            return
        else:
            customer_class = result[0]
        
        # Check same booking already exist
        if my_db.book_exists(movie_id, user_id):
            print(f'User {user_id} already booked movie {movie_id}')
            return
        
        # check movie is fully booked
        cursor.execute("SELECT COUNT(*) FROM Book WHERE mov_id = %s", movie_id)
        result = cursor.fetchone()
        if result[0] >= 10:
            print(f'Movie {movie_id} has already been fully booked')
            return
        
        # calculate price based on customer class
        if customer_class == 'premium':
            price = int(price * 0.75)
        elif customer_class == 'vip':
            price = int(price * 0.5)
        
        cursor.execute("INSERT INTO Book (mov_id, person_id, reserve_price) VALUES (%s, %s, %s)", (movie_id, user_id, price))
        my_db.connection.commit()

    # success message
    print('Movie successfully booked')

# Problem 9 (5 pt.)
def rate_movie():
    # Handle invalid inputs
    movie_id = input('Movie ID: ')
    user_id = input('User ID: ')
    rating = input('Ratings (1~5): ')

    with my_db.connection.cursor() as cursor:
        if my_db.movie_exists_id(movie_id):
            print(f'Movie {movie_id} does not exist')
            return
        
        if my_db.user_exists_id(user_id):
            print(f'User {user_id} does not exist')
            return
        
        try:
            cursor.execute('SELECT rating FROM Book WHERE mov_id = %s AND person_id = %s', (movie_id, user_id))
            result = cursor.fetchone()
            if result == None:
                try:
                    cursor.execute('UPDATE Book SET rating = %s WHERE mov_id = %s AND person_id = %s', (rating, movie_id, user_id))
                    my_db.connection.commit()
                except pymysql.err.DataError:
                    print('Rating should be an integer')
                    return
                except pymysql.err.OperationalError:
                    print('Rating should be from 1 to 5')
                    return
            else:
                print(f'User {user_id} has already rated movie {movie_id}')
                return
        except pymysql.err.OperationalError:
            print(f'User {user_id} has not booked movie {movie_id} yet')
            return

    # success message
    print('Movie successfully rated')
    # YOUR CODE GOES HERE
    pass

# Problem 10 (5 pt.)
def print_users_for_movie():
    # YOUR CODE GOES HERE
    movie_id = input('Movie ID: ')

    with my_db.connection.cursor() as cursor:
        if not my_db.movie_exists_id(movie_id):
            # error message
            print(f'Movie {movie_id} does not exist')
            return
        
        try:
            cursor.execute('''
            SELECT DISTNCT Person.ID, Person.name, Person.age, Book.reserve_price, Book.rating
            FROM Person NATURAL JOIN Book ON Person.ID = Book.person_id
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
        except pymysql.err.DataError:
            print('Movie ID should be an integer')
            return


# Problem 11 (5 pt.)
def print_movies_for_user():
    user_id = input('User ID: ')

    with my_db.connection.cursor() as cursor:
        if my_db.user_exists_id(user_id):
            print(f'User {user_id} does not exist')
            return
        
        try:
            cursor.execute('''
                SELECT DISTINCT Movie.ID, Movie.title, Movie.director, Book.reserve_price, Book.rating
                FROM Movie NATURAL JOIN Book ON Movie.ID = Book.mov_id
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
        except pymysql.err.DataError:
            print('User ID should be an integer')
            return
        
        
# Problem 12 (6 pt.)
def recommend_popularity():
    # YOUR CODE GOES HERE
    user_id = input('User ID: ')
    
    with my_db.connection.cursor() as cursor:
        if my_db.user_exists_id(user_id):
            print(f'User {user_id} does not exist')
            return

    # error message
    print(f'User {user_id} does not exist')
    # YOUR CODE GOES HERE
    pass


# Problem 13 (10 pt.)
def recommend_item_based():
    # YOUR CODE GOES HERE
    user_id = input('User ID: ')


    # error message
    print(f'User {user_id} does not exist')
    print('Rating does not exist')
    # YOUR CODE GOES HERE
    pass


# Total of 70 pt.
def main():
    my_db.initialize_database()

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
        print('11. print all movies rated by an user')
        print('12. recommend a movie for a user using popularity-based method')
        print('13. recommend a movie for a user using item-based collaborative filtering')
        print('14. exit')
        print('15. reset database')
        print('============================================================')
        menu = int(input('Select your action: '))

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