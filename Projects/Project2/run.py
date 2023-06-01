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
            SELECT Movie.title, Movie.director, Movie.price, AVG(Book.reserve_price), Count(Book.person_id), AVG(Book.rating)
            FROM Movie LEFT OUTER JOIN Book ON Movie.ID = Book.mov_id 
            GROUP BY Movie.ID
            ORDER BY ID ASC
            ''')
        result = cursor.fetchall()
        print('-' * 140)
        print(str.format('{:^70}{:^35}{:^15}{:^15}{:^15}{:^15}', 'TITLE', 'DIRECTOR', 'ORIGIN PRICE', 'AVG BOOK PRICE', 'COUNT BOOK', 'AVG RATING'))
        for title, director, origin_price, avg_price, book_count, avg_rating in result:
            if avg_rating == None:
                avg_rating = "None"
            print(f'{title:<70}{director:<35}{origin_price:<15}{int(avg_price):<15}{book_count:<15}{avg_rating:<15}')
        print('-' * 140)

# Problem 3 (3 pt.)
def print_users():
    with my_db.connection.cursor() as cursor:
        cursor.execute('SELECT * FROM Person ORDER BY ID ASC')
        result = cursor.fetchall()
        print('-' * 140)
        print(str.format('{:^40}{:^20}{:^20}', 'name', 'age', 'class'))
        for _, name, age, customer_class in result:
            print(f'{name:<40}{age:<20}{customer_class:<20}')
        print('-' * 140)

    pass

# Problem 4 (4 pt.)
def insert_movie():
    # YOUR CODE GOES HERE
    title = input('Movie title: ')
    director = input('Movie director: ')
    
    with my_db.connection.cursor() as cursor:
        # Check if movie already exists
        cursor.execute('SELECT COUNT(ID) FROM Movie WHERE title = %s', title)
        result = cursor.fetchone()
        if result[0] != 0:
            # error message
            print(f'Movie {title} already exists')
            return
        else:
            # Get price
            price = input('Movie price: ')
            # Check if price is valid
            if int(price) >= 0 and int(price) <= 100000:
                cursor.execute('INSERT INTO Movie (title, director, price) VALUES (%s, %s, %s)', (title, director, price))
                my_db.connection.commit()
            else:
                print('Movie price should be from 0 to 100000')

    # success message
    print('One movie successfully inserted')
    

# Problem 6 (4 pt.)
def remove_movie():
    movie_id = input('Movie ID: ')
    
    with my_db.connection.cursor() as cursor:
        # Check if movie exists
        cursor.execute('SELECT COUNT(ID) FROM Movie WHERE ID = %s', movie_id)
        result = cursor.fetchone()
        if result[0] == 0:
            # error message
            print(f'Movie {movie_id} does not exist')
            return
        else:
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
    
    if age < 12 or age > 110:
         print('User age should be from 12 to 110')
    
    with my_db.connection.cursor() as cursor:
        cursor.execute('SELECT COUNT(ID) FROM Person WHERE name = %s', name)
        result = cursor.fetchone()
        if result[0] != 0:
            # error message
            print(f'The user ({name}, {age}) already exists')
            return
        else:
            customer_class = input('User class: ')
            if customer_class == 'basic' or customer_class == 'premium' or customer_class == 'vip':
                cursor.execute('INSERT INTO Person (name, age, customer_class) VALUES (%s, %s, %s)', (name, age, customer_class))
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
        cursor.execute('SELECT COUNT(ID) FROM Person WHERE ID = %s', user_id)
        result = cursor.fetchone()
        
        if result[0] == 0:
            # error message
            print(f'User {user_id} does not exist')
            return
        else:
            cursor.execute('DELETE FROM Person WHERE ID = %s', user_id)
            my_db.connection.commit()

    # success message
    print('One user successfully removed')
    # YOUR CODE GOES HERE
    pass

# Problem 8 (5 pt.)
def book_movie():
    # YOUR CODE GOES HERE
    movie_id = input('Movie ID: ')
    user_id = input('User ID: ')

    with my_db.connection.cursor() as cursor:
        # Check movie exists
        cursor.execute("SELECT COUNT(ID) FROM Movie WHERE ID = %s", movie_id)
        result = cursor.fetchone()
        if result[0] == 0:
            # error message
            print(f'Movie {movie_id} does not exist')
            return

        # Check user exists
        cursor.execute("SELECT COUNT(ID) FORM Person WHERE ID = %s", user_id)
        result = cursor.fetchone()
        if result[0] == 0:
            print(f'User {user_id} does not exist')
            return
        
        # Check same booking already exist
        cursor.execute("SELECT COUNT(*) FROM Booking WHERE mov_id = %s AND usr_id = %s", (movie_id, user_id))
        result = cursor.fetchone()
        if result[0] != 0:
            print(f'User {user_id} already booked movie {movie_id}')
            return
        
        cursor.execute("SELECT COUNT(*) FROM Booking WHERE mov_id = %s", movie_id)
        result = cursor.fetchone()
        if result[0] >= 10:
            print(f'Movie {movie_id} has already been fully booked')
            return

    # success message
    print('Movie successfully booked')
    # YOUR CODE GOES HERE
    pass

# Problem 9 (5 pt.)
def rate_movie():
    # YOUR CODE GOES HERE
    movie_id = input('Movie ID: ')
    user_id = input('User ID: ')
    rating = input('Ratings (1~5): ')


    # error message
    print(f'Movie {movie_id} does not exist')
    print(f'User {user_id} does not exist')
    print(f'Wrong value for a rating')
    print(f'User {user_id} has not booked movie {movie_id} yet')
    print(f'User {user_id} has already rated movie {movie_id}')

    # success message
    print('Movie successfully rated')
    # YOUR CODE GOES HERE
    pass

# Problem 10 (5 pt.)
def print_users_for_movie():
    # YOUR CODE GOES HERE
    user_id = input('User ID: ')

    
    # error message
    print(f'User {user_id} does not exist')
    # YOUR CODE GOES HERE
    pass


# Problem 11 (5 pt.)
def print_movies_for_user():
    # YOUR CODE GOES HERE
    user_id = input('User ID: ')


    # error message
    print(f'User {user_id} does not exist')
    # YOUR CODE GOES HERE
    pass

# Problem 12 (6 pt.)
def recommend_popularity():
    # YOUR CODE GOES HERE
    user_id = input('User ID: ')


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