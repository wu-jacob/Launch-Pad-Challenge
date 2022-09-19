
# Launch-Pizza

Because we are only focused on coding the backend for Launch-Pizza's online store, we will assume that the frontend of the website has a way to retreive the customer's order information and convert it to a json object. This json object should contain the name of the customer, the different items ordered, the quantity, the price of the order, the status of the order, and when the order was placed. 

We will be using python and fastAPI to write our backend, and PostgreSQL as our database management system, however, other languages and frameworks should work as well. Although using an object-relational mapper such as SQLAlchemy might be more convenient in the long run, we will use the default PostgreSQL driver Psycopg to connect our code and database as it is a bit simpler.

To connect our code to an existing database using Psycopg, we simply follow the module's documentation. An example of this is shown below:

```
conn = psycopg2.connect(host="localhost",database="launchpizza",user="postgres",password="pizzaisawesome123", cursor_factory=RealDictCursor)
cursor = conn.cursor()
```

In case the connection to the database fails, we can wrap this code in a try except as well as a while loop to continue trying to establish a connection if we fail to connect to the database:

```
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
```

Now that we have a way to connect to our database, we will take the json object given to us by the front end and convert it into a python dictionary in order to better work with the data. For example:

```
{"customer_name": "Jacob", "item": "Cheeze Pizza", "quantity": 2, "amount_paid": 24.00, "order_status": "Order Received"}
```

Before we do anything with this data, we should create a schema that defines exactly what data we want. This will ensure that the data we are receiving from the frontend is of the correct type and format. To do so, we will use a python module called Pydantic. Using Pydantic, we can define a class to represent the orders Launch-Pizza receives. This class will then extend from a class in Pydantic known as BaseModel. Using this class, we can then define the name of each input, and exactly what type of data it should be. If we receive data from the frontend that does not match what we have defined in our class, then Pydantic will return an error. 

An example of a class that extends from BaseModel:

```
class Order(BaseModel):

    customer_name: str

    item: str

    quantity: int

    amount_paid: float

    order_status: str
```

To store the details of this new order in our database, we must first call a POST HTTP request method in fastAPI with the path ("/orders") to create a new "order". In the function body for this method, we will use the python module Psycopg to help us insert the data from our dictionary into a table in PostgreSQL. 

```
@app.post("/orders")

def create_order(order: Order):

    cursor.excecute("""INSERT INTO orders (customer_name, item, quantity, amount_paid, order_status) VALUES(%s, %s, %s, %s, %s) RETURNING * """, (order.customer_name, order.item, order.quantity, order.amount_paid, order.order_status, order.date))

    new_order = cursor.fetchone()

    conn.commit()

    return {"data": new_order}
```

Additionally, we can use SQL to code it so that every new order that is inserted into the database will automatically be assigned a unique primary key. This will help the restaurant keep track of each individual order. An example table that would be stored in the database would look something like this:

| Customer Name | Item                | Quantity    | Amount Paid ($) | Order Status   | Date                       | Order ID |
| -----------   | ------------------- | ----------- | --------------- | -------------- | -------------------------- | -------- |
| Jacob Wu      | Cheese Pizza        | 2           | 24.00           | Delivered      | 2022-09-18 06:44:09 +00:00 | 1        |
| John Wayne    | Hawaiian Pizza      | 1           | 12.00           | In Progress    | 2022-09-18 07:01:21 +00:00 | 2        |
| Don Quixote   | House Special Pizza | 1           | 14.00           | Order Received | 2022-09-18 07:06:14 +00:00 | 3        |


To display the newest orders to the workers making the pizza, we can call a GET HTTP request method using FastAPI. Inside the function body, we can use Psycopg to perform a SQL query to our database and return a list of all the orders that the restaurant has yet to fufill.

```
@app.get("/orders")

def get_orders():

    cursor.excecute("""SELECT * FROM orders WHERE order_status = "Order Received" """)

    orders = cursor.fetchall()

    return {"data": orders}
```

Similarily to display the customer's order to them, we can use the GET HTTP request method with the path ("/orders/{id}") and use Psycopg to communicate with our database and retrieve the data related to that specific customer's order. This data can then be used by the frontend to display to the customer all their order details in a user friendly format.

```
@app.get("/orders/{id}")

def get_order(id: int):

    cursor.excecute("""SELECT * FROM orders WHERE id = %s """, (str(id)))

    order = cursor.fetchone()

    return {"data": order}
```

Once the workers at Launch-Pizza have finished making an order, they can use the software to trigger an event listener in the frontend which calls on the backend to update the order status. To do so, we can use the PUT or PATCH with the path  ("/orders/{id}") HTTP request method. In the function body for either of these methods, we can once again use Psycopg to execute a SQL command that updates the specified order's status. In the same way, if a customer wanted to change their order, we can also use a similar request method to do so.

```
@app.patch("orders/{id}")

def update_order(id: int, order: Order):

    cursor.excecute("""UPDATE orders SET order_status = %s WHERE id = %s RETURNING * """, (order.order_status, str(id)))

    updated_order = cursor.fetchone()

    conn.commit()

    return {"data": updated_order}
```

Finally, once a year has passed after a customer's order, we can delete their order information from our database with the DELETE HTTP request method with the path ("/orders/{id}"). Similar to the other HTTP request methods, we simply use Psycopg to execute a SQL command that deletes the specified order from our database.

```
@app.delete("/orders/{id}")

def delete_order(id: int):

    cursor.excecute("""DELETE * FROM orders WHERE id = %s RETURNING * """, (str(id)))

    deleted_order = cursor.fetchone()

    conn.commit()

    return {"data": deleted_order}
```

All of the code snippets used in this file are also contained in the "http-reques-methods.py" file for easier reference.
