import sqlite3

# TODO create User model  

DB_NAME = 'users.db'

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        username text UNIQUE NOT NULL, 
        email text UNIQUE NOT NULL, 
        hashed_password TEXT NOT NULL
    )''')

    conn.commit()

    conn.close()


def create_user(username : str, email : str, hashed_password : str):
    conn = None
    try: 
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""INSERT INTO users (username, email, hashed_password) 
                       VALUES (?, ?, ?)""", 
                       (username, email, hashed_password))
        
        conn.commit()

        return cursor.lastrowid
    
    except sqlite3.IntegrityError as e:
        # username or email already exists
        raise ValueError("Username or email already exists")    

    finally:
        if conn:
            conn.close()
            
def get_user_by_username(username : str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, hashed_password FROM users WHERE username = ?", (username,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return {
        "id" : row[0],
        "username" : row[1],
        "email" : row[2],
        "hashed_password" : row[3]
    }