import os

import datetime
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///football.db")

@app.route("/")
def index():
    """Starting page"""

    # Render appropriate html template
    return render_template("index.html")

@app.route("/pick")
def pick():
    """ User picks what they want to do """
    
    # Render appropriate html template
    return render_template("main_page.html")


@app.route("/store")
def store():
    """ Store main page """

    # Render appropriate html template
    return render_template("store.html")


@app.route("/view", methods=["GET", "POST"])
def view():
    """View uploaded items"""

    # Query into database and select certain fields to display
    items = db.execute("SELECT product, description, price, status FROM user_items")

    # Change price to USD format
    for row in items:
        row["price"] = usd(row["price"])
    
    # Render appropriate html template
    return render_template("view.html", items=items)
    
    
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get username, password and confirmation password from form
        Username = request.form.get("username")
        Password = request.form.get("password")
        Confirmation = request.form.get("confirmation")

        # Ensure username was submitted if not return error
        if not Username:
            return apology("must provide username", 400)

        # Ensure password was submitted if not return error
        elif not Password:
            return apology("must provide password", 400)

        # Ensure confirmation password was submitted if not return error
        elif not Confirmation:
            return apology("must provide password confirmation", 400)

        # Ensure both entered passwords match
        elif not Password == Confirmation:
            return apology("passwords must match", 400)

        # Ensure that ther are no duplicate usernames
        username_check = db.execute("SELECT username FROM users WHERE username = :username", username=Username)

        # If username taken put an error message
        if len(username_check) == 1:
            return apology("sorry, username is already taken", 400)

        # If username is not taken do the following
        else:

            # Get hash value for password
            hash_value = generate_password_hash(Password)

            # Insert user and hash of the password into the table
            user = db.execute("INSERT INTO users(username, hash) VALUES (:username, :password)",
                              username=Username, password=hash_value)

            return redirect("/login")
    else:

        # User reached route via GET (as by clicking a link or via redirect)
        return render_template("register.html")
        

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted if not return error
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted if not return error
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/store")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/store")


@app.route("/buy")
@login_required
def buy():
    """Show all uploaded products"""

    # Set current user's id to variable to be used below
    Userid = session["user_id"]

    # Query into database and select certain fields to display
    items = db.execute("SELECT product, description, price, status, item_id FROM user_items")

    # Change price to USD format
    for row in items:
        row["price"] = usd(row["price"])

    # Render appropriate html template
    return render_template("buy.html", items=items)


@app.route("/wishlist/<item>")
@login_required
def wish(item):
    """Enter items into wishlist table"""
    
    # Set current user's id to variable to be used below
    Userid = int(session["user_id"])
    
    # Set the item's id from argument to variable to be used below 
    Itemid = item
    
    # Query into table for user_id where item_id matches the item_id from the arg
    check_item = db.execute("SELECT user_id FROM user_items WHERE item_id=:item_id", item_id=Itemid)
    
    # If the user_id selcted is equal to the user_id of the user do the following 
    if check_item[0]["user_id"] == Userid:
        
        # Flask message to user 
        flash("YOU CAN'T ADD YOUR OWN ITEM TO YOUR WISHLIST!", "error")
        
        # Redirect user back to appropriate page
        return redirect("/buy")
    
    # If the user_id selcted is not equal to the user_id of the user do the following     
    else:
        
        # Add certain fields to the wishlist table provided that item is not already in the wishlist table
        db.execute("INSERT INTO wishlist (user_id, item_id, product, description, price, status) SELECT user_id, item_id, product, description, price, status FROM user_items WHERE item_id=:item_id AND NOT EXISTS(SELECT 1 FROM wishlist WHERE user_id=:user_id AND item_id=:item_id)",
                item_id=Itemid, user_id=Userid)
        
        # Update the user_id in the wishlist table to the current user'd id
        db.execute("UPDATE wishlist SET user_id=:user_id WHERE wishlist_id=(SELECT max(wishlist_id) FROM wishlist)", user_id=Userid)
        
        # Redirect user to appropriate page              
        return redirect("/wishlist")
    
    
@app.route("/wishlist")
@login_required
def wishlist():
    """Show user's wishlist"""
    
    # Set current user's id to variable to be used below
    Userid = session["user_id"]
    
    # Query into database and select certain fields to display
    wishlist = db.execute("SELECT wishlist_id, item_id, product, description, price, status FROM wishlist WHERE user_id=:user_id", user_id=Userid)
        
    # Change price to USD format
    for row in wishlist:
        row["price"] = usd(row["price"])
    
    # Render appropriate html template    
    return render_template("wishlist.html", wishlist=wishlist)
    

@app.route("/remove/<item>")
@login_required
def remove(item):
    """Remove an item from user's wishlist"""
    
    # Set the item's wishlist id from argument to variable to be used below 
    Wishlistid = item
    
    # Delet row from table with unique wishlist_id
    db.execute("DELETE FROM wishlist WHERE wishlist_id=:wishlist_id", wishlist_id=Wishlistid)
    
    # Redirect user to appropriate page 
    return redirect("/buy")


@app.route("/contact/<item>")
@login_required
def contact(item):
    """Display contact page"""
    
    # Set the item's id from argument to variable to be used below 
    Itemid = item
    
    # Set current user's id to variable to be used below
    Userid = session["user_id"]
    
    # Query into table for user_id where item_id matches the item_id from the arg
    check_item = db.execute("SELECT user_id FROM user_items WHERE item_id=:item_id", item_id=Itemid)
    
    # If the user_id selcted is equal to the user_id of the user do the following
    if check_item[0]["user_id"] == Userid:
        
        # Flask message to user
        flash("THIS IS YOUR ITEM!", "error")
        
        # Redirect user to appropriate page 
        return redirect("/buy")
    
    # If the user_id selcted is not equal to the user_id of the user do the following     
    else:
        
        # Query into database and select certain fields to display
        contact = db.execute("SELECT name, product, price, email, number FROM user_items WHERE item_id=:item_id", item_id=Itemid)
        
        # Render appropriate html template             
        return render_template("contact.html", contact=contact)


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell apparel of your own"""

    # Set current user's id to variable to be used below
    Userid = session["user_id"]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get username, password and confirmation password from form
        Name = request.form.get("name")
        Product = request.form.get("product")
        Description = request.form.get("description")
        Price = request.form.get("price")
        Status = request.form.get("status")
        Email = request.form.get("email")
        Number = request.form.get("number")

        # Insert the information into user_items table
        user_item = db.execute("INSERT INTO user_items (user_id, name, product, description, price, status, email, number) VALUES (:user_id, :name, :product, :description, :price, :status, :email, :number)",
                                 user_id=Userid, name=Name, product=Product, description=Description, price=Price, status=Status, email=Email, number=Number)
        
        # Redirect user to appropriate page
        return redirect("/my_items")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        
        # Render appropriate html template  
        return render_template("sell.html")
    
    
@app.route("/my_items")
@login_required
def my_items():
    """ Table of user's items """

    # Set current user's id to variable to be used below
    Userid = session["user_id"]

    # Set my_items table using the following fields
    my_items = db.execute("SELECT product, description, price, status, item_id FROM user_items WHERE user_id=:user_id", user_id=Userid)

    # Change price to USD format
    for row in my_items:
        row["price"] = usd(row["price"])
    
    # Render appropriate html template
    return render_template("my_items.html", my_items=my_items)
    

@app.route("/delete/<item>")
@login_required
def deleting(item):
    """ Delete item from table """
    
    # Set the item's id from argument to variable to be used below
    Itemid = item
    
    # Delete row from user_items table that matches the item_id
    db.execute("DELETE FROM user_items WHERE item_id=:item_id", item_id=Itemid)
    
    # Redirect user to appropriate page
    return redirect("/delete")
    
    
@app.route("/delete")
@login_required
def delete():
    """ Page after item has been deleted """
    
    # Render appropriate html template
    return render_template("delete.html")


@app.route("/edit/<item>")
@login_required
def edit(item):
    """ Display edit page """
    
    # Set the item's id from argument to variable to be used below
    Itemid = item
    
    # Set edit table using the following fields   
    edit = db.execute("SELECT item_id, product, description, price, status, email, number FROM user_items WHERE item_id=:item_id", item_id=Itemid)
    
    # Change price to USD format
    for row in edit:
        row["price"] = usd(row["price"])
    
    # Render appropriate html template       
    return render_template("edit.html", edit=edit)


@app.route("/product/<item>", methods=["GET", "POST"])
@login_required
def product(item):
    """ Update product """
    
    # Set the item's id from argument to variable to be used below
    Itemid = item
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # Get product from form
        Product = request.form.get("product")
        
        # Update user_items table with new product name
        db.execute("UPDATE user_items SET product=:product WHERE item_id=:item_id",
                   product=Product, item_id=Itemid)
        
        # Redirect user to appropriate page                   
        return redirect("/my_items")
    
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        
        # Set edit table using the following fields
        edit = db.execute("SELECT item_id, product, description, price, status FROM user_items WHERE item_id=:item_id", item_id=Itemid)
        
        # Change price to USD format
        for row in edit:
            row["price"] = usd(row["price"])
        
        # Render appropriate html template        
        return render_template("edit.html", edit=edit)
        

@app.route("/description/<item>", methods=["GET", "POST"])
@login_required
def description(item):
    """ Update description """
    
    Itemid = item
    if request.method == "POST":
        Description = request.form.get("description")
        db.execute("UPDATE user_items SET description=:description WHERE item_id=:item_id",
                   description=Description, item_id=Itemid)
                            
        return redirect("/my_items")

    else:
        edit = db.execute("SELECT item_id, product, description, price, status FROM user_items WHERE item_id=:item_id", item_id=Itemid)
        
        for row in edit:
            row["price"] = usd(row["price"])
                
        return render_template("edit.html", edit=edit)


@app.route("/price/<item>", methods=["GET", "POST"])
@login_required
def price(item):
    """ Update price """
    
    Itemid = item
    if request.method == "POST":
        Price = request.form.get("price")
        db.execute("UPDATE user_items SET price=:price WHERE item_id=:item_id",
                   price=Price, item_id=Itemid)
                   
        return redirect("/my_items")

    else:
        edit = db.execute("SELECT item_id, product, description, price, status FROM user_items WHERE item_id=:item_id", item_id=Itemid)
        
        for row in edit:
            row["price"] = usd(row["price"])
                
        return render_template("edit.html", edit=edit)


@app.route("/email/<item>", methods=["GET", "POST"])
@login_required
def email(item):
    """ Update email """
    
    Itemid = item
    if request.method == "POST":
        Email = request.form.get("email")
        db.execute("UPDATE user_items SET email=:email WHERE item_id=:item_id",
                   email=Email, item_id=Itemid)
                            
        return redirect("/my_items")

    else:
        edit = db.execute("SELECT item_id, product, description, price, status FROM user_items WHERE item_id=:item_id", item_id=Itemid)
        
        for row in edit:
            row["price"] = usd(row["price"])
                
        return render_template("edit.html", edit=edit)


@app.route("/status/<item>", methods=["GET", "POST"])
@login_required
def status(item):
    """ Update status """
    
    Itemid = item
    if request.method == "POST":
        Status = request.form.get("status")
        db.execute("UPDATE user_items SET status=:status WHERE item_id=:item_id",
                   status=Status, item_id=Itemid)
                            
        return redirect("/my_items")

    else:
        edit = db.execute("SELECT item_id, product, description, price, status FROM user_items WHERE item_id=:item_id", item_id=Itemid)
        for row in edit:
            row["price"] = usd(row["price"])
                
        return render_template("edit.html", edit=edit)
        

@app.route("/number/<item>", methods=["GET", "POST"])
@login_required
def number(item):
    """ Update number """
    
    Itemid = item
    if request.method == "POST":
        Number = request.form.get("number")
        db.execute("UPDATE user_items SET number=:number WHERE item_id=:item_id",
                   number=Number, item_id=Itemid)
                            
        return redirect("/my_items")

    else:
        edit = db.execute("SELECT item_id, product, description, price, status FROM user_items WHERE item_id=:item_id", item_id=Itemid)
        for row in edit:
            row["price"] = usd(row["price"])
                
        return render_template("edit.html", edit=edit)
        

@app.route("/trivia")
def trivia():
    """ Trivia page """
    
    # Render appropriate html template
    return render_template("trivia.html")
    
    
@app.route("/funfacts")
def funfacts():
    """ Fun facts page """
    
    # Render appropriate html template
    return render_template("funfacts.html")
    
    
@app.route("/unpopularopinions")
def unpopularopinions():
    """ Unpopular opinions page """
    
    # Render appropriate html template
    return render_template("unpopularopinions.html")
    
    
@app.route("/which", methods=["GET", "POST"])
def which():
    """ Which footballer are you? page """
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # Get position from form
        Position = request.form.get("position")
        
        # If position is the following render respective html templates:
        
        if Position == "Goalkeeper":
            return render_template("goalkeeper.html")
        
        elif Position == "Center-back":
            return render_template("center-back.html")
            
        elif Position == "Full-back":
            return render_template("full-back.html")
        
        elif Position == "Defensive Midfielder":
            return render_template("defensive_midfielder.html")
            
        elif Position == "Central Midfielder":
            return render_template("central_midfielder.html")
            
        elif Position == "Attacking Midfielder":
            return render_template("attacking_midfielder.html")
            
        elif Position == "Winger":
            return render_template("winger.html")
            
        elif Position == "Striker":
            return render_template("striker.html")
            
        elif Position == "Forward":
            return render_template("forward.html")
            
    # User reached route via GET (as by clicking a link or via redirect)        
    else:
        
        # Render appropriate html template
        return render_template("which.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
