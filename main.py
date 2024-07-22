from flask import Flask, render_template, redirect, request,session,jsonify
from database import *
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import pygal
import random,os
from collections import Counter

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def hello():
    prods = fetch_data("products")
    random.shuffle(prods)
    r_products = random.sample(prods, 7)
    return render_template("index.html", prods=prods, r_products=r_products)

@app.route("/users")
def students():
   user = fetch_data("users")
   return render_template("register.html", user = user)

@app.route("/customers")
def customer():
    user = fetch_data("users")
    return render_template("customers.html", renny= user)

@app.route("/register") 
def register():
   return render_template("register.html")

@app.route("/products")
def products():
    prods = fetch_data("products")
    random.shuffle(prods)
    r_products = random.sample(prods, 7)
    # Extract unique service types (categories)
    ser = {i[2] for i in prods}
    # Create a dictionary to store items grouped by category
    items_by_category = {category: [] for category in ser}
    # Populate the items_by_category dictionary
    for item in prods:
        category = item[2]  # Assuming servicetype is at index 1
        items_by_category[category].append(item)
    return render_template("products.html", items_by_category=items_by_category,r_products = r_products, prods=prods)

@app.route("/inventory")
def inventory():
    inve= fetch_data("products")
    return render_template("inventory.html", inve= inve)



@app.route("/sales")
def sales():
       sales = fetch_data("sales")
       prods= fetch_data("products")
       return render_template('sales.html', sales=sales, prods=prods)

@app.route("/dashboard")
def dashboard():
    return render_template("layout1.html")


@app.route('/adduser', methods=["POST", "GET"])
def signup():
   if request.method=="POST":
      fullname = request.form["fullname"]
      email = request.form["email"]
      phone = request.form["phone"]
      password = request.form["password"]
      address = request.form["address"]
      h_password = generate_password_hash(password)
      user=(fullname,email,phone,address,h_password,'now()')
      add_user(user)
   return redirect("/register")

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'cart' in session:
        # Iterate over each item in the cart and insert into the sales table
        for item in session['cart']:
            sales = (item['pid'], item['quantity'], 'now()')
            insert_sales(sales)
        # After inserting sales, clear the cart
        session.pop('cart', None)
        return render_template('cart.html', thank_you=True)    # Redirect to the sales page or any other desired page
    else:
        return "Your cart is empty"

@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]
        users = fetch_data('users')
        for user in users:
            dbemail = user[2]
            dbpass = user[5]
            if dbemail == email and check_password_hash(dbpass, password):
                # Redirect to dashboard or homepage after successful login
                return redirect('/')  # Assuming you have a route named 'dashboard'
    return render_template('login.html')

@app.route("/addproducts", methods=["POST", "GET"])
def addproducts():
   if request.method=="POST":
      name = request.form["name"]
      category= request.form["category"]
      buying_price= request.form["buying_price"]
      selling_price=request.form["selling_price"]
      image_url=request.form["image_url"]
      products=(name,category,buying_price,selling_price,image_url)
      insert_product(products)
      return redirect("/inventory")
  
  
@app.route("/editproduct", methods=["POST", "GET"])
def editproducts():
   if request.method=="POST":
      pid = request.form['pid']
      name = request.form["name"]
      category = request.form['category']
      buying_price= request.form["buying_price"]
      selling_price=request.form["selling_price"]
      image_url=request.form["image_url"]
      vs=(pid,name,category,buying_price,selling_price,image_url)
      update_products(vs)
      return redirect("/inventory")
  
  
@app.route("/deleteproduct", methods=["POST"])
def deleteproduct():
    if request.method == "POST":
        product_id = request.form["pid"]
        delete_product(product_id)
        return redirect("/inventory")
    
def addsales():
    if request.method == "POST":
        pid = request.form["pid"]
        quantity = request.form["quantity"]
        sales = (pid, quantity, datetime.now())
        insert_sales(sales)

        # Remove the item from the cart after adding to sales
        cart = session.get('cart', [])
        for item in cart:
            if item['pid'] == pid:
                cart.remove(item)
                session['cart'] = cart
                break

        return redirect("/sales")
  


@app.route('/addstock', methods=["POST"])
def addstock():
    if request.method == "POST":
        pid = request.form["pid"]
        quantity = request.form["quantity"]
        
        # Calculate expiry date (current date + 2 days)
        expiry_date = datetime.now() + timedelta(days=2)

        stock = (pid, quantity, datetime.now(), expiry_date)
        insert_stock(stock)
        return redirect("/stock")

  
  
@app.route("/stock")
def stockk():
           stock = fetch_data("stocks")
           prods= fetch_data("products")
           return render_template('stock.html', stock=stock, prods=prods)


@app.route("/graph")
def bar1():  
   #  bar graph for sales per product
    line_graph = pygal.Line()
    line_graph.title = 'sales per day'
    sale_product = sales_per_day()
    name1 = []
    sale1 = []
    for j in sale_product:
       name1.append(j[0])
       sale1.append(j[1])
    line_graph.x_labels = name1
    line_graph.add('Sale', sale1)
    line_graph=line_graph.render_data_uri()
    
    
      #  bar graph for sales per product
    line_graph1 = pygal.Line()
    line_graph1.title = 'sales per month'
    sale_product = sales_per_month()
    name1 = []
    sale1 = []
    for j in sale_product:
       name1.append(j[0])
       sale1.append(j[1])
    line_graph1.x_labels = name1
    line_graph1.add('Sale', sale1)
    line_graph1=line_graph1.render_data_uri()
    return render_template('dashboard.html', line_graph=line_graph,line_graph1=line_graph1)



@app.route('/addtocart', methods=["POST"])
def add_to_cart():
    if 'cart' not in session:
        session['cart'] = []

    pid = request.form["pid"]
    quantity = int(request.form["quantity"])

    # Fetch product information from the database
    cur.execute("SELECT * FROM products WHERE pid = %s", (pid,))
    product = cur.fetchone()

    if product:
        # Check if the product is already in the cart
        product_found = False
        for item in session['cart']:
            if item['pid'] == pid:
                # If the product is already in the cart, update the quantity
                item['quantity'] += quantity
                product_found = True
                break

        if not product_found:
            # If the product is not in the cart, add it
            session['cart'].append({
                'pid': pid,
                'name': product[1],
                'image': product[6],
                'price': product[3],
                'quantity': quantity
            })

        # Reconstruct the entire session cart with updated item quantities
        session['cart'] = reconstruct_cart(session['cart'])

        

        # Redirect to view_cart route
        return redirect('/#py-5')
    else:
        return "Product not found"

def insert_sales(sale_data):
    q = "INSERT INTO sales (pid, quantity, created_at) VALUES (%s, %s, %s)"
    cur.execute(q, sale_data)
    conn.commit()


def reconstruct_cart(cart):
    reconstructed_cart = []
    seen_pids = set()  # Track seen product IDs
    for item in cart:
        if item['pid'] not in seen_pids:
            # If product ID is not seen before, add the item directly
            reconstructed_cart.append(item)
            seen_pids.add(item['pid'])
        else:
            # If product ID is seen before, update the quantity
            for existing_item in reconstructed_cart:
                if existing_item['pid'] == item['pid']:
                    existing_item['quantity'] += item['quantity']
                    break
    return reconstructed_cart



@app.route('/deletefromcart', methods=['POST'])
def delete_from_cart():
    if 'cart' in session:
        pid = request.json.get('pid')
        for item in session['cart']:
            if item['pid'] == pid:
                session['cart'].remove(item)  # Remove the item from the cart
                session.modified = True  # Mark the session as modified after deletion
                break
        # Recalculate total price after deleting item
        total_price = sum(float(item['price']) * int(item['quantity']) for item in session['cart'])
        # Return JSON response with updated total price
        return jsonify({'success': True, 'total_price': total_price})
    return jsonify({'success': False})
    


@app.route('/updatecart', methods=["POST"])
def update_cart():
    pid = request.form["pid"]
    quantity = int(request.form["quantity"])
    # Update quantity of item in session cart based on pid
    for item in session['cart']:
        if item['pid'] == pid:
            item['quantity'] = quantity
            break
    return '', 204  # Return empty response with 204 status code


@app.context_processor
def inject_total_items():
    # Get the cart from the session
    cart = session.get('cart', [])
    # Count occurrences of each product ID in the cart
    product_counts = Counter(item['pid'] for item in cart)
    # Total number of specific products in the cart
    total_items = len(product_counts)
    return dict(total_items=total_items)



    
@app.route('/cart')
def view_cart():
    cart = session.get('cart', [])
    total_price = sum(float(item['price']) * int(item['quantity']) for item in cart)
    return render_template('cart.html', cart=cart, total_price=total_price)



if __name__ == '__main__':

    app.run(debug=True)
    