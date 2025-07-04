# WORLD'S GREATEST EXPENSE TRACKER
#### Video Demo:  [https://youtu.be/jntH3dJw9gE](https://youtu.be/jntH3dJw9gE)
#### Description:
World's Greatest Expense Tracker is as the name suggest, is the world's greatest expense tracker (debatable). This web app can perform a basic CRUD operations to help you track your expenses.

## Features
### 1. Update Balance
You can manually update your balance without having to input your incomes or expenses to match your current bank or wallet balance. Or perhaps you forgot to track your expenses for a few days and can't be bother to add a lot of inputs you can just go straight and change the balance.
### 2. Add Incomes
You can add your income alongside with the date and type of income so you can group what type of income it is.
### 3. Add expenses
You can add your expense alongside with the date and type of expense so you can group what type of expense it is.
### 4. Delete entries
If you ever misinput entries you can always delete them and resubmit it again.
### 5. Choose your currency
You can choose the type of currency you are using, there are 10 currencies available.

## What's Inside?
### 1. app.py
Contains all the main algorithms and logics for the application like the routes and database manipulations. I decided to use SQLAlchemy Core to learn how to use other database library instead relying on CS50 SQL library. A lot of the logics are inspired by CS50 Finance Problem Set 9 but changed and/or refactored to match the function of an expense tracker app.\

Inside app.py there are few routes, to name a few:\
1. Index\
This function contains the logic that will be passed to jinja in the templates. Most of the code here is just compiling all the values from different route to pass to the templates.
2. update_balance\
A route that is not necessarily a new page which update the value of the user's balance in the database.
3. update_currency\
A route which fetch the currency option chosen by the user which later get passed to index to be passed to jinja templates.
4. add_income\
A route which calls the validate_form() function to validate the value of date, amount, type, notes (if any), and to also catch error which is going to be checked by and if statement which later going to flash a message and a category which are going to be fetch by index to display.
5. add_expense\
Basically does the same thing as add_expense which is why is decided to refactor the code to helpers.\
6. other functions like login, log out, and register are inspired by CS50 Finance which are altered accordingly to the app requirements.

### 2. helpers.py
Contains functions that are going to be used multiple times inside **app.py** to save a lot of lines and make the code more readable. For example :\
1. get_balance()\
  A function so that code can just fetch the balance one time and reused in the code. I decide to made this because I notice that I need to get balance in two different routes which need to call for database which is pretty long so I decided to just refactor it to make it a bit nicer.
2. validate_form()\
A function to refactor the validation because I notice that /add_expense and /add_income routes are basically doing the same thing which are checking if each form is filled or not, then checking if the dates, types, and amounts are valid or not, then if not it's going to flash an error message which are also redundant so I decided to hide them behind helpers to make it more concise.
3. login_required()\
Taken from CS50 Finance Problem Set 9 to filter which pages need login. I don't think I can make a similar function with less lines so I decided to use this instead.
### 3. db.py
Just contains the initialization of engine for the database because putting them on app or helpers broke the app because it will create a circling error.
### 4. expense.db
Contains the data for the database. Inside there are two tables which are the users table that contains the login info of the user and their balance, and statement table which contains the history data of the expenses and incomes.
### 5. Templates
Contains .html files for the pages which are taking inspiration from CS50 Finance with a lot of bootstrap stylings because I'm not really good with front-end stuffs, inside there are:\
1. index.html\
Contains all the main elements of the app like balance display, the statements table, expense and income forms, and their respective buttons.
2. layout.html\
Taking inspiration from CS50 Finance but I made it dark mode and also change the title.
3. login.html\
Contains the login form with the message that ask the user if they don't have an account they can click register instead.
4. register.html\
Contains the register form with the message that ask the user if they already have an account they can click Log In instead.

