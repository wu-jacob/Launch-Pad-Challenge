from fastapi import FastAPI
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
import time

app = FastAPI()

class Order(BaseModel):
    customer_name: str
    item: str
    quantity: int
    amount_paid: float
    order_status: str

while True:
    try:
        conn = psycopg2.connect(host="localhost",database="launchpizza",user="postgres",password="pizzaisawesome123", cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successfull!")
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error: ", error)
        time.sleep(2)

@app.post("/orders")
def create_order(order: Order):
    cursor.excecute("""INSERT INTO orders (customer_name, item, quantity, amount_paid, order_status) VALUES(%s, %s, %s, %s, %s) RETURNING * """, (order.customer_name, order.item, order.quantity, order.amount_paid, order.order_status, order.date))
    new_order = cursor.fetchone()
    conn.commit()
    return {"data": new_order}

@app.get("/orders")
def get_orders():
    cursor.excecute("""SELECT * FROM orders WHERE order_status = "Order Received" """)
    orders = cursor.fetchall()
    return {"data": orders}

@app.get("/orders/{id}")
def get_order(id: int):
    cursor.excecute("""SELECT * FROM orders WHERE id = %s """, (str(id)))
    order = cursor.fetchone()
    return {"data": order}

@app.patch("orders/{id}")
def update_order(id: int, order: Order):
    cursor.excecute("""UPDATE orders SET order_status = %s WHERE id = %s RETURNING * """, (order.order_status, str(id)))
    updated_order = cursor.fetchone()
    conn.commit()
    return {"data": updated_order}

@app.delete("/orders/{id}")
def delete_order(id: int):
    cursor.excecute("""DELETE * FROM orders WHERE id = %s RETURNING * """, (str(id)))
    deleted_order = cursor.fetchone()
    conn.commit()
    return {"data": deleted_order}