import psycopg2
# psycopg2 is a popular Python adapter for PostgreSQL that allows you to interact with PostgreSQL databases using Python code

try:
    conn = psycopg2.connect("dbname= meat user=postgres password=1234")
    cur =conn.cursor()
except Exception as e:
    print(e)


def fetch_data(tbname):
    try:
        q = "SELECT * FROM " + tbname + ";"
        cur.execute(q)
        records = cur.fetchall()
        return records 
    except Exception as e:
        return e   


def add_user(v):
    vs = str(v)
    q = "insert into users(fullname,email,phone,address,h_password,created_at) "\
        "values" + vs
    cur.execute(q)
    conn.commit()
    return q


def insert_product(v):
    vs = str(v)
    q = "insert into products(name,category,buying_price,selling_price, image_url) "\
        "values" + vs
    cur.execute(q)
    conn.commit()
    return q


def update_products(vs):
        pid = vs[0]
        name = vs[1]
        category = vs[2]
        buying_price = vs[3]
        selling_price = vs[4]
        image_url = vs[5]
        q = "UPDATE products SET name = %s, category = %s, buying_price = %s, selling_price = %s, image_url = %s WHERE pid = %s"
        cur.execute(q, (name, category,buying_price, selling_price, image_url,pid))
        conn.commit()
        return q


def delete_product(id):
    q_delete_product = "DELETE FROM products WHERE pid = %s;"
    cur.execute(q_delete_product, (id,))
    conn.commit()


def insert_sales(v):
    vs = str(v)
    q = "insert into sales(pid,quantity,created_at) "\
        "values" + vs
    cur.execute(q)
    conn.commit()
    return q


def insert_stock(v):
    pid, quantity, created_at, expiry_date = v
    # Format the timestamps as strings in the format 'YYYY-MM-DD HH:MM:SS'
    created_at_str = created_at.strftime('%Y-%m-%d %H:%M:%S')
    expiry_date_str = expiry_date.strftime('%Y-%m-%d %H:%M:%S')
    # Construct the SQL query with placeholders
    q = "INSERT INTO stock (pid, quantity, expiry_date, created_at) VALUES (%s, %s, %s, %s)"
    # Execute the query with the provided values
    cur.execute(q, (pid, quantity, expiry_date_str, created_at_str))
    conn.commit()
    return q


def sales_per_day():
    q = " SELECT * FROM sales_per_day;" 
    cur.execute(q) 
    results = cur.fetchall()
    return results


def sales_per_month():
    q = " SELECT * FROM sales_per_month;" 
    cur.execute(q) 
    results = cur.fetchall()
    return results