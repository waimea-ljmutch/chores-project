#===========================================================
# YOUR PROJECT TITLE HERE
# YOUR NAME HERE
#-----------------------------------------------------------
# BRIEF DESCRIPTION OF YOUR PROJECT HERE
#===========================================================

from flask import Flask, render_template, request, flash, redirect
import html

from app.helpers.session import init_session
from app.helpers.db      import connect_db
from app.helpers.errors  import init_error, not_found_error
from app.helpers.logging import init_logging
from app.helpers.time    import init_datetime, utc_timestamp, utc_timestamp_now


# Create the app
app = Flask(__name__)

# Configure app
init_session(app)   # Setup a session for messages, etc.
init_logging(app)   # Log requests
init_error(app)     # Handle errors and exceptions
init_datetime(app)  # Handle UTC dates in timestamps


#-----------------------------------------------------------
# Home page route
#-----------------------------------------------------------
@app.get("/")
def index():
    with connect_db() as client:
        # Get all the things from the DB
        sql = "SELECT id, name FROM people ORDER BY name ASC"
        params = []
        result = client.execute(sql, params)
        people = result.rows

        # And show them on the page
        return render_template("pages/home.jinja", people=people)


#-----------------------------------------------------------
# chores page route
#-----------------------------------------------------------
@app.get("/chores/<int:pid>")
def show_chores(pid):
    with connect_db() as client:
        # Get all the things from the DB
        sql = "SELECT id, name FROM people WHERE id = ?"
        params = [pid]
        result = client.execute(sql, params)
        person = result.rows[0]

        # Get all the things from the DB
        sql = """
            SELECT id, name, done FROM chores 
            WHERE done=0
            ORDER BY done ASC, name ASC
        """
        params = []
        result = client.execute(sql, params)
        chores = result.rows

        # And show them on the page
        return render_template("pages/chores.jinja", person=person, chores=chores, pid=pid)

#-----------------------------------------------------------
# Thing page route - Show details of a single thing
#-----------------------------------------------------------
@app.get("/thing/<int:id>")
def show_one_thing(id):
    with connect_db() as client:
        # Get the thing details from the DB
        sql = "SELECT id, name, price FROM things WHERE id=?"
        params = [id]
        result = client.execute(sql, params)

        # Did we get a result?
        if result.rows:
            # yes, so show it on the page
            thing = result.rows[0]
            return render_template("pages/thing.jinja", thing=thing)

        else:
            # No, so show error
            return not_found_error()

#-----------------------------------------------------------
# Route for adding a thing, using data posted from a form
#-----------------------------------------------------------
@app.post("/addchore/<int:pid>")
def add_a_chore(pid):
    # Get the data from the form
    name  = request.form.get("chore")

    # Sanitise the text inputs
    name = html.escape(name)

    with connect_db() as client:
        # Add the thing to the DB
        sql = "INSERT INTO chores (name, pid) VALUES (?, ?)"
        params = [name, pid]
        client.execute(sql, params)

        # Go back to the home page
        flash(f"chore '{name}' added", "success")
        return redirect("/chores/<int:pid>")

#-----------------------------------------------------------
# Route for adding a thing, using data posted from a form
#-----------------------------------------------------------
@app.post("/addperson")
def add_a_person():
    # Get the data from the form
    name  = request.form.get("name")

    # Sanitise the text inputs
    name = html.escape(name)

    with connect_db() as client:
        # Add the thing to the DB
        sql = "INSERT INTO people (name) VALUES (?)"
        params = [name]
        client.execute(sql, params)

        # Go back to the home page
        flash(f"person '{name}' added", "success")
        return redirect("/")


#-----------------------------------------------------------
# Route for deleting a thing, Id given in the route
#-----------------------------------------------------------
@app.get("/delete/<int:id>")
def delete_a_thing(pid):
    with connect_db() as client:
        # Delete the thing from the DB
        sql = "DELETE FROM chores WHERE id=?"
        params = [id]
        client.execute(sql, params)

        # Go back to the home page
        flash("chore deleted", "success")
        return redirect("/chores")


