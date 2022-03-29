"""
Views related to the handling and presentation of favourites companies
"""
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for, jsonify,
    Blueprint)

from flask_login import login_required
from bson.objectid import ObjectId

from app import mongo

from app.models.user import User

favourites = Blueprint("favourites", __name__, template_folder='templates')


@favourites.route("/", methods=["GET", "POST"])
@login_required
def view_favourites():
    """
    Function to view companies as favourite by a user
    - require user to be logged in
    - retrieve user in session
    - find organisations in list of user's favourites
    """
    user = User.find_one_user(session["_user_id"].lower())
    favourites = list(mongo.db.organisations.find({"_id": {
                                                    "$in": user["favourites"]}
                                                   }))
    return render_template('favourites/my_favourites.html',
                           favourites=favourites)


@favourites.route("/add_to_favourites", methods=["GET", "POST"])
@login_required
def add_to_favourites():
    """
    Function to add a company to a user's favourite, requiring user to be
    logged-in
    - Post request received from script.js / organisation.html
    - Retrieve the company ID from the data
    - Check if company has been added to favourites
    - Add company id to favourites field in user collection in MongoDB
    - Return success message
    """
    # Retrieve company id from post request
    resp = request.form.to_dict(flat=False)
    company_id = resp["companyId"][0]
    # Retrieve user in session
    user = User.find_one_user(session["_user_id"].lower())
    if "favourites" in user and company_id in user["favourites"]:
        flash("Company already added to favourites")
        return redirect(url_for('organisations.get_organisations'))
    else:
        # Add company ID to user's favourite
        User.append_favourite(user['_id'], company_id)
        message = "success"

    return jsonify(message)
