import sqlite3
from langchain.tools import tool

DB_PATH = "app/data/orders.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            user_name TEXT,
            status TEXT,
            items TEXT
        )
    ''')
    cursor.execute("SELECT count(*) FROM orders")
    if cursor.fetchone()[0] == 0:
        data = [
            (1001, "Ahmed", "Shipped", "Laptop, Mouse"),
            (1002, "Mohamed", "Processing", "Monitor"),
            (1003, "Sarah", "Delivered", "Headphones"),
            (1004, "Ali", "Cancelled", "Keyboard")
        ]
        cursor.executemany("INSERT INTO orders VALUES (?,?,?,?)", data)
        conn.commit()
        print("--- Dummy Database Created ---")
    conn.close()

init_db()

@tool
def get_order_status(order_id: int):
    """
    Use this tool to fetch the status of an order. 
    Input should be the Order ID (integer).
    Returns the order status and items.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT status, items FROM orders WHERE order_id=?", (order_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return f"Order #{order_id} is currently {result[0]}. Items: {result[1]}."
    else:
        return f"Order #{order_id} not found."

@tool
def cancel_order(order_id: int):
    """
    Use this tool to cancel an order.
    Input should be the Order ID (integer).
    Returns a confirmation message.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT status FROM orders WHERE order_id=?", (order_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return f"Error: Order #{order_id} does not exist."
    
    if result[0] == "Shipped" or result[0] == "Delivered":
        conn.close()
        return f"Cannot cancel Order #{order_id} because it is already {result[0]}."
    
    cursor.execute("UPDATE orders SET status='Cancelled' WHERE order_id=?", (order_id,))
    conn.commit()
    conn.close()
    return f"Success: Order #{order_id} has been cancelled."

@tool
def return_order(order_id: int):
    """
    Use this tool to return an order.
    Input should be the Order ID (integer).
    Returns a confirmation message.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT status FROM orders WHERE order_id=?", (order_id,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return f"Error: Order #{order_id} does not exist."

    if result[0] != "Delivered":
        conn.close()
        return f"Cannot return Order #{order_id} because it is in {result[0]} state."

    cursor.execute("UPDATE orders SET status='Returned' WHERE order_id=?", (order_id,))
    conn.commit()
    conn.close()
    return f"Success: Order #{order_id} has been returned."
    
        