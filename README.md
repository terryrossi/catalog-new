# ** Catalog Project. **

 The purpose of this project is to create a full CRUD web application available on Localhost:5000.
 - This Web App is a Python program using SqlAlchemy to connect to the database.
 - This app allows registered users to create Categories and populate them with products a bit similar to Amazon except there's no purchasing aspect.
 - Each user can edit or delete the categories or products he/she has created but can only 'browse' other people's categories and products.
 - unregistered users can only browse categories and products.
 - Authentication is done through Facebook or Google.

 _The 2 Json files required for this process are not being sent to Github for security purposes._

- Here are the 2 required file names:

  1. client_secrets.json
  2. fb_client.secrets.json

_You can create your own secret files through Google and Facebook. Here are the steps to follow:_

  - Google Authentication:

    1. Create a new project at: `https://console.developers.google.com`
    2. Under APIs&Services select `Credentials`
    3. `Create Credentials`
    4. `OAuth client ID`
    5. To create an OAuth client ID, you must first set a product name on the consent screen so click on `Configure consent screen`
    6. enter an application name and press `Save`
    7. for application type, select `web application` and `Create`
    8. a window is showing your Client ID and Client Secret
    9. Click `ok` then select the application you just create for details
    10. click on the `DOWNLOAD JSON` button on top to create the file
    11. copy the content of that file and paste it into the empty client_secrets.json that I provided
    12. Authorized JavaScript origins = `http://localhost:5000/`
    13. Authorized redirect URIs = `http://localhost:5000/category`
    14. IMPORTANT! don't forget to enter your Google Client ID (`data-clientid`)in `login.html`

  - Facebook Authentication:

    1. Got to `https://developers.facebook.com/` and create a new Application
    2. Configure the URL site as: http://localhost:5000/
    3. Create a Test Application from the button in the apps dropdown.
    4. Don't change the default values.
    5. enter the Test Application Application Id and App Secret in the empty fb_client_secrets.json file I provided
    6. IMPORTANT! Don't forget to enter your FB App ID (`appId`) in `login.html`


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
