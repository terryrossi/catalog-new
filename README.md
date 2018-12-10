# ** Catalog Project. **

 The purpose of this project is to create a full CRUD web application available on Localhost:5000.
 - This Web App is a Python program using SqlAlchemy to connect to the database.
 - This app allows registered users to create Categories and populate them with products a bit similar to Amazon except there's no purchasing aspect.
 - Each user can edit or delete the categories or products he/she has created but can only 'browse' other people's categories and products.
 - unregistered users can only browse categories and products.
 - Authentication is done through Facebook or Google.

 _The 2 Json files required for this process are not been sent to Github for security purposes. I will send them separately through the Udacity loading page._

- Here are the 2 required file names:

  1. client_secrets.json
  2. fb_client.secrets.json

## **The Script**

The script is written in Python 3.

##### To execute the script, run: `python application.py`

## **The Environment**

### Vagrant Virtual Machine:

  - If you need to bring the virtual machine back online, use `vagrant up`
  - To log in use `vagrant ssh`

### SqlAlchemy Database

  - to create the database run `python database_setup.py`.

  - It will create 3 tables in the database `Amazonwithusers.db`:

    - `User`
    - `Category`
    - `Product`

  - To load the sample data into the new database, run `python categories.py`.
    This will create few Categories with products associated to them.

### JSON Files      

  - There are 2 options to create JSON files:

        1. `/category/<int:category_id>/JSON` _Creates a Json file with:_

            - Category name
            - Category id
            - userId of the creator of the category

        2. `/category/<int:category_id>/<int:product_id>/JSON` _Creates a Json file with:_

            - Product id
            - Product name
            - userId of the creator of the category
            - Product description
            - Product price


## Code Quality

The code quality has been validated using The PEP8 style guide. You can do a quick check using the pep8 command-line tool.

Please check it out and don't hesitate to let me know if these's anything I could have done better.

Regards.

Terry
