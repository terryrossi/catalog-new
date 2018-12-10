from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Product, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"

engine = create_engine('sqlite:///Amazonwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

# Create anti-forgery state token


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = '''https://graph.facebook.com/oauth/access_token?grant_type=
fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s'''
    % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
# Due to the formatting for the result from the server token exchange we
# have to split the token first on commas and select the first index which give
# us the key : value for the server access token then we split it on colons to
# pull out the actual token value and replace the remaining quotes with nothing
# so that it can be used directly in the graph api calls
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = '''https://graph.facebook.com/v2.8/me?access_token=%s&fields=
    name,id,email''' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = '''https://graph.facebook.com/v2.8/me/picture?access_token=
%s&redirect=0&height=200&width=200''' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ''' " style = "width: 300px; height: 300px;border-radius: 150px;
-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '''

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = '''https://graph.facebook.com/%s/permissions?access_token=%s'''
    % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('''Current user is already
 connected'''), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ''' " style = "width: 300px; height: 300px;border-radius: 150px;
-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '''
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    session = DBSession()
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    session.close()
    return user.id


def getUserInfo(user_id):
    session = DBSession()
    user = session.query(User).filter_by(id=user_id).one()
    session.close()
    return user


def getUserID(email):
    try:
        session = DBSession()
        user = session.query(User).filter_by(email=email).one()
        session.close()
        return user.id
    except:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('''Failed to revoke token for
 given user.''', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/category/<int:category_id>/JSON')
def categoryMenuJSON(category_id):
    session = DBSession()

    category = session.query(Category).filter_by(id=category_id).one()
    products = session.query(Product).filter_by(
        category_id=category_id).all()

    session.close()
    return jsonify(Category=category.serialize,
                   Products=[i.serialize for i in products])


@app.route('/category/<int:category_id>/<int:product_id>/JSON')
def categoryProductJSON(category_id, product_id):
    session = DBSession()

    category = session.query(Category).filter_by(id=category_id).one()
    print ('CATEGORY ET PRODUIT', category_id, product_id)
    try:
        product = session.query(Product).filter_by(
            category_id=category_id, id=product_id).one()
        if product:
            session.close()
            return jsonify(Category=category.serialize,
                           Product=product.serialize)
        else:
            errormessage == "No Product: "
            errormessage += product_id
            errormessage += " for Category: "
            errormessage += category_id
            session.close()
            return jsonify(errormessage)
    except IOError:
        self.send_error(404, 'File Not Found: %s' % self.path)

# Show all Categories


@app.route('/')
@app.route('/category')
def category():
    session = DBSession()
    categories = session.query(Category).order_by(asc(Category.name)).all()
    session.close()
    if 'username' not in login_session:
        return render_template('publicmenucategories.html',
                               categories=categories)
    else:
        return render_template('menucategories.html', categories=categories)

# Create a new Category


@app.route('/category/new', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        print ('ENTERING newCategory (POST)')
        session = DBSession()
        newCategory = Category(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newCategory)
        session.commit()
        print ("new category created!")
        print ("new category name", newCategory.name)
        print ("new category user_id", newCategory.user_id)
        flash("New Category Created!")
        session.close()
        return redirect(url_for('category'))
    else:
        return render_template('newcategory.html')

# Edit Category


@app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
def editCategory(category_id):
    print ('*************** Entering editcategory *****************')
    session = DBSession()
    changedCategory = session.query(Category).filter_by(id=category_id).one()
    if 'username' not in login_session:
        session.close()
        return redirect('/login')
    if changedCategory.user_id != login_session['user_id']:
        session.close()
        return '''<script>function myFunction() {alert('You are not authorized
to edit this category. Please create your own category in order to edit.');}
</script><body onload='myFunction()'>'''

    if request.method == 'POST':
        if request.form['name']:
            changedCategory.name = request.form['name']

        print ('CHANGED CATEGORY = ', changedCategory.name)
        session.add(changedCategory)
        session.commit()
        flash("Category Updated!")
        session.close()
        return redirect(url_for('category'))
    else:
        print ('going to editcategory.html')
        session.close()
        return render_template('editcategory.html', category=changedCategory)

# Delete CATEGORY


@app.route('/category/<int:category_id>/delete', methods=['GET', 'POST'])
def deleteCategory(category_id):

    if 'username' not in login_session:
        return redirect('/login')

    session = DBSession()
    categoryToDelete = session.query(Category).filter_by(id=category_id).one()

    if categoryToDelete.user_id != login_session['user_id']:
        session.close()
        return '''<script>function myFunction() {alert('You are not authorized
to delete this category. Please create your own category in order to delete.');
}</script><body onload='myFunction()'>'''

    if request.method == 'POST':
        session.delete(categoryToDelete)
        session.commit()
        flash("Category Deleted!")
        print ('CATEGORY DELETED = ', categoryToDelete.name)
        session.close()
        return redirect(url_for('category'))
    else:
        print ('going to deletecategory.html')
        session.close()
        return render_template('deletecategory.html',
                               category=categoryToDelete)

# Show all products for selected Category


@app.route('/category/<int:category_id>/menu/', methods=['GET', 'POST'])
@app.route('/category/<int:category_id>/', methods=['GET', 'POST'])
def categoryMenu(category_id):
    session = DBSession()
    category = session.query(Category).filter_by(id=category_id).one()
    creator = getUserInfo(category.user_id)
    products = session.query(Product).filter_by(category_id=category.id).all()
    session.close()

    if 'username' not in login_session
    or creator.id != login_session.get('user_id', False):
        return render_template('publicmenu.html', category=category,
                               products=products, creator=creator)
    else:
        return render_template('menu.html', category=category,
                               products=products, creator=creator)

# Create a new Product


@app.route('/product/<int:category_id>/new', methods=['GET', 'POST'])
def newProduct(category_id):

    if 'username' not in login_session:
        return redirect('/login')

    session = DBSession()
    category = session.query(Category).filter_by(id=category_id).one()

    if login_session['user_id'] != category.user_id:
        session.close()
        return '''<script>function myFunction() {alert('You are not authorized
to add menu items to this category. Please create your own category in order to
 add items.');}</script><body onload='myFunction()'>'''

    if request.method == 'POST':
        newProduct = Product(
            name=request.form['name'], category_id=category_id,
            user_id=category.user_id)
        newProduct.description = request.form['description']
        newProduct.price = request.form['price']

        session.add(newProduct)
        session.commit()
        print ("new product created!")
        flash("New Product Created!")
        session.close()
        return redirect(url_for('categoryMenu', category_id=category_id))
    else:
        session.close()
        return render_template('newproduct.html', category=category)


@app.route('/product/<int:category_id>/<int:product_id>/show',
           methods=['GET', 'POST'])
def showProduct(category_id, product_id):
    session = DBSession()
    category = session.query(Category).filter_by(id=category_id).one()
    creator = getUserInfo(category.user_id)
    showProduct = session.query(Product).filter_by(id=product_id).one()

    if 'username' not in login_session
    or creator.id != login_session.get('user_id', False):
        session.close()
        return render_template('publicshowproduct.html', category=category,
                               product=showProduct, creator=creator)
    else:
        session.close()
        return render_template('showproduct.html',
                               category=category,
                               product=showProduct,
                               creator=creator)

# Edit a Product


@app.route('/product/<int:category_id>/<int:product_id>/edit',
           methods=['GET', 'POST'])
def editProduct(category_id, product_id):

    if 'username' not in login_session:
        return redirect('/login')

    session = DBSession()
    category = session.query(Category).filter_by(id=category_id).one()
    changedProduct = session.query(Product).filter_by(id=product_id).one()

    if login_session['user_id'] != category.user_id:
        session.close()
        return '''<script>function myFunction() {alert('You are not authorized
to edit products to this category. Please create your own category in order to
 edit products.');}</script><body onload='myFunction()'>'''

    if request.method == 'POST':
        if request.form['name']:
            changedProduct.name = request.form['name']
        if request.form['description']:
            changedProduct.description = request.form['description']
        if request.form['price']:
            changedProduct.price = request.form['price']

        session.add(changedProduct)
        session.commit()
        flash("Product Updated!")
        session.close()
        return redirect(url_for('categoryMenu', category_id=category_id))
    else:
        print ('going to editproduct.html')
        session.close()
        return render_template('editproduct.html', category=category,
                               product=changedProduct)


# Delete a product


@app.route('/product/<int:category_id>/<int:product_id>/delete',
           methods=['GET', 'POST'])
def deleteProduct(category_id, product_id):

    if 'username' not in login_session:
        return redirect('/login')

    session = DBSession()
    category = session.query(Category).filter_by(id=category_id).one()
    productToDelete = session.query(Product).filter_by(id=product_id).one()

    if login_session['user_id'] != category.user_id:
        session.close()
        return '''<script>function myFunction() {alert('You are not authorized
 to delete products to this category. Please create your own category in order
  to delete products.');}</script><body onload='myFunction()'>'''

    if request.method == 'POST':
        session.delete(productToDelete)
        session.commit()
        print ('finished commit, going to categoryMenu')
        flash("Product Deleted!")
        session.close()
        return redirect(url_for('categoryMenu', category_id=category_id))
    else:
        print ('going to deleteproduct.html')
        session.close()
        return render_template('deleteproduct.html', category=category,
                               product=productToDelete)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('category'))
    else:
        flash("You were not logged in")
        return redirect(url_for('category'))


if __name__ == '__main__':
    app.secret_key = 'secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
