import sqlite3
from datetime import datetime

# Database Setup and Connection
con = sqlite3.connect('family_finances_management.db')
con.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
cursor = con.cursor()

# Tables Initialization
# Main user table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS user(
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT NOT NULL,
        address TEXT NOT NULL,
        phone TEXT
    )
''')
con.commit()

# Function to create a transaction table for each user
def create_transaction_table(user_id):
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS transaction_{user_id} (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
        )
    ''')
    con.commit()

# User Management Functions
def list_users():
    """Display all users in the database."""
    cursor.execute("SELECT * FROM user")
    for row in cursor.fetchall():
        print(row)

def add_user():
    """Add a new user and create a personal transaction table."""
    user_name = input("Enter the user name: ")
    address = input("Enter your address: ")
    phone = input("Enter phone: ")
    cursor.execute("INSERT INTO user (user_name, address, phone) VALUES (?, ?, ?)", (user_name, address, phone))
    con.commit()
    user_id = cursor.lastrowid  # Get the ID of the newly created user
    create_transaction_table(user_id)
    ask = input("user added succesfully . do like deposit (y/n) ? ")
    if ask=='y':
        amount = float(input("\nEnter amount to deposit: ₹"))
        deposit(user_id,amount)

def update_user():
    """Update user details in the database."""
    user_id = input("Enter the user ID you want to update: ")
    user_name = input("Enter your name: ")
    address = input("Enter your address: ")
    phone = input("New phone: ")
    cursor.execute("UPDATE user SET user_name = ?, address = ?, phone = ? WHERE user_id = ?", (user_name, address, phone, user_id))
    con.commit()

def delete_user():
    """Delete a user and their transaction history."""
    user_id = input("Enter the user ID you want to delete: ")
    cursor.execute("DELETE FROM user WHERE user_id = ?", (user_id,))
    cursor.execute(f"DROP TABLE IF EXISTS transaction_{user_id}")
    con.commit()
    print("User and associated transactions deleted successfully.")

# Financial Transaction Functions
def deposit(user_id):
    """Deposit a specified amount for a user."""
    timestamp = datetime.now().strftime('%d-%m-%y %H:%M:%S')
    amount = float(input("\nEnter amount to deposit: ₹"))
    cursor.execute(f'''
        INSERT INTO transaction_{user_id} (user_id, transaction_type, amount, timestamp) 
        VALUES (?, 'deposit', ?, ?)
    ''', (user_id, amount, timestamp))
    con.commit()
    print("Deposit successful.")

def withdraw(user_id):
    """Withdraw a specified amount if balance is sufficient."""
    timestamp = datetime.now().strftime('%d-%m-%y %H:%M:%S')
    current_balance = get_balance(user_id)
    amount = float(input("\nEnter amount to withdraw: ₹"))
    if current_balance >= amount:
        cursor.execute(f'''
            INSERT INTO transaction_{user_id} (user_id, transaction_type, amount, timestamp) 
            VALUES (?, 'withdraw', ?, ?)
        ''', (user_id, -amount, timestamp))
        con.commit()
        print("Withdrawal successful.")
    else:
        print("Insufficient balance.")

def get_balance(user_id):
    """Fetch and display the current balance of a user."""
    cursor.execute(f'''
        SELECT COALESCE(SUM(amount), 0) FROM transaction_{user_id}
    ''')
    balance = cursor.fetchone()[0]
    print(f"Current balance for user {user_id} is: ₹{balance}")
    return balance

def view_transaction_history(user_id):
    """Show the transaction history for a user."""
    cursor.execute(f"SELECT * FROM transaction_{user_id}")
    transactions = cursor.fetchall()
    print("Transaction History:")
    for transaction in transactions:
        print(transaction)

# User Interaction Functions
def existing_user_menu():
    """Display menu for existing user functionalities."""
    user_id = input("Enter your User ID: ")

    # Validate if user exists
    cursor.execute("SELECT * FROM user WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        print("User not found. Please check the User ID.")
        return

    while True:
        print("\n|-|-| Existing User Menu |-|-|\n")
        print("1. Deposit Amount")
        print("2. Withdraw Amount")
        print("3. View Balance")
        print("4. View Transaction History")
        print("5. Back to Main Menu")
        
        choice = input("\nEnter your choice: ")
        
        match choice:
            case '1':
                deposit(user_id)
            case '2':
                withdraw(user_id)
            case '3':
                get_balance(user_id)
            case '4':
                view_transaction_history(user_id)
            case '5':
                print("\nReturning to main menu.")
                break
            case _:
                print("\nInvalid input. Please select a valid option.")

# Main Menu Function
def main():
    """Main program loop displaying the general menu."""
    while True:
        print("\nFamily Finance Management")
        print("\n------ MENU -------\n")
        print("1. List Existing Users")
        print("2. Add a New User")
        print("3. Access your account")
        print("4. Update Existing User Details")
        print("5. Delete User")
        print("6. Exit")
        choice = input("\nEnter your choice: ")

        match choice:
            case '1':
                list_users()
            case '2':
                add_user()
            case '3':
                existing_user_menu()
            case '4':
                update_user()
            case '5':
                delete_user()
            case '6':
                print("\nThanks for using our program :)\n")
                break
            case _:
                print("Invalid input.")

    con.close()

# Program Entry Point
if __name__ == "__main__":
    main()
