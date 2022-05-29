Name: Maggie R. Mano
School: Harvard University
Class: Class of '24, first-year

Design Document for Final Project

I used flask and python to create a functional web application. There are two folders in the implementation folder entitled "static" and "templates".
The static folder contains all the css stylesheets as well as any image files used in the web application. Placing these all in one folder made it easier
to refer to them within the html templates. The templates folder contains all the html templates used in the web application. Putting them all in one folder made
the organisation of everything a lot neater. 

The application.py file contains all the python and flask that run the web application. I used a bunch of functions that only returned html templates for the
starter pages of the web application. For the store page the functions were more complex:

- The "view" function queried into the football database and selected certain fields to display in the template that is returned by the function. I did this so
  before user's logged in they could see the available products. 

- The "register" and "login" functions were borrowed from the finance pset. They add users to the users table in football.db and hash their passwords for safety
  purposes. 

- The "logout" function forgets the session and redirects the user to the store main page

- The "buy" function is there to display the products to the users thus queries into the user_items table to display certain fields to the user. 
  A function in helpers.py that converts integers to USD price is used here so that the prices are dsiplayed in USD.

- The "wish(item)" function takes the item_id of the item the user selected when they press the "Add" button in wishlist.html as an argument. 
  The item_id is then used to find the specific row in the user items table and insert it into the wishlist table. I made sure to only insert the item information
  into wishlist if the item does not already exist in the wishlist table so that there are no duplicates in the presented wishlist table. The user_id 
  in the wishlist table is then updated to the user_id of the current user (the session user). I also made sure that a user does not add their own product to the
  wishlist by checking the user_id of the item being added from user items table with the userid of the cuurent user.

- The "wishlist" function is there to display the products the user added thus queries into the wishlist table to display certain fields to the user. 
  A function in helpers.py that converts integers to USD price is used here so that the prices are dsiplayed in USD.

- The "remove(item)" function takes the wishlist_id of the item the user wishes to remove from their wishlist as an argument. This is then used to query into 
  the wishlist table and delete the row that has that wishlist_id thus effectively deleteing the item from the users wishlist. 

- The contact(item) function also takes the item_id of the item the user selected when they press the "Contact Seller" button as an argument. This is then
  used to query into the user items table and identify the row with the unique item_id. It then selects the required fields to be displayed in contact.html.

- The "sell()" function takes methods post and get. It receives information from the user's inputs and enters these inputs into the user_items table. 
  
- The "my_items()" function is there to display the user's uploaded products thus queries into the user items table to display certain fields to the user. 
  A function in helpers.py that converts integers to USD price is used here so that the prices are dsiplayed in USD.

- The "deleting(item)" function takes the item_id of an uploaded product by a user as its argument and uses it to query into the user items table 
  to delete the row that contains that unique item_id.

- The "edit(item)" function is similar to the delete(item) function in the sense that it takes the item_id as its argument and uses it to query into the
  user_items table to select the specific row in the table and siplay it in edit.html

- The "product(item)", "description(item)", "price(item)", "email(item)", "status(item)" and "number(item)" functions all take item_id as their arguments.
  If a user decides to update any of the fields listed they enter the new information and press the update button. This queries into the user_items table for
  row which contains the unique item_id and changes the field being editted to the new information the user provided when submitting the form.
  I made them all seperate forms so that if a user wants to only update the status of a product for example then they can just update that speciic field.

- The trivia, funfacts and unpopularopinions functions are all used to render the respective html templates. These are basic webpages.

- The which function uses methods post and get and depending on what position the user chooses renders the respective template that goes with it.

The store html templates use layouts and thus jinja is used. This made it easier to create these pages as they all contained the same layout so instead of
creating the same basic set up I just used the extend layout jinja tool.