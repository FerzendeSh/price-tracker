import sqlite3

DB_NAME = "users.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # user table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL
    )
    """)

    # protducts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        url TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        UNIQUE(user_id, url),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # price history
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS price_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        price REAL NOT NULL,
        currency TEXT NOT NULL DEFAULT 'SEK',
        checked_at TEXT NOT NULL DEFAULT (datetime('now')),
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
    )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_user_id ON products(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_history_product_id ON price_history(product_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_history_checked_at ON price_history(checked_at)")

    conn.commit()
    conn.close()



def init_user_table():
    pass

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