#===========================================================
# YOUR PROJECT TITLE HERE
# YOUR NAME HERE
#-----------------------------------------------------------
# BRIEF DESCRIPTION OF YOUR PROJECT HERE
#===========================================================

from flask import Flask, render_template, request, flash, redirect, session
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
# process person selection
#-----------------------------------------------------------
@app.get("/person/<int:pid>")
def show_person(pid):
    # Save user ID for later
    session['pid'] = pid
    return redirect("/chores")

#-----------------------------------------------------------
# chores page route
#-----------------------------------------------------------
@app.get("/chores")
def show_chores():
    # Get the user from the session
    pid = session.get("pid", None)
    if not pid:
        redirect("/")

    with connect_db() as client:
        # Get all the things from the DB
        sql = "SELECT id, name FROM people WHERE id = ?"
        params = [pid]
        result = client.execute(sql, params)
        person = result.rows[0]

        # Get all the person's chores that are not done
        sql = """
            SELECT id, name, done FROM chores 
            WHERE done=0 AND person_id=?
            ORDER BY name ASC
        """
        params = [pid]
        result = client.execute(sql, params)
        your_chores = result.rows

        # Get all the person's other chores that are not done
        sql = """
            SELECT id, name FROM chores 
            WHERE done=0 AND person_id IS NULL
            ORDER BY name ASC
        """
        params = []
        result = client.execute(sql, params)
        other_chores = result.rows

        # Get all the person's other chores that are not done
        sql = """
            SELECT 
                chores.id, 
                chores.name AS c_name, 
                people.name AS p_name
            FROM chores 
            JOIN people ON chores.person_id = people.id
            WHERE done=1
            ORDER BY c_name ASC
        """
        params = []
        result = client.execute(sql, params)
        done_chores = result.rows

        # And show them on the page
        return render_template(
            "pages/chores.jinja", 
            person=person, 
            your_chores=your_chores,
            other_chores=other_chores,
            done_chores=done_chores    
        )

#-----------------------------------------------------------
# Route for adding a chore, using data posted from a form
#-----------------------------------------------------------
@app.post("/chore")
def add_a_chore():
    # Get the data from the form
    name  = request.form.get("chore")

    # Sanitise the text inputs
    name = html.escape(name)

    with connect_db() as client:
        # Add the thing to the DB
        sql = "INSERT INTO chores (name) VALUES (?)"
        params = [name]
        client.execute(sql, params)

        # Go back to the home page
        flash(f"chore '{name}' added", "success")
        return redirect("/chores")

#-----------------------------------------------------------
# Route for marking a chore done
#-----------------------------------------------------------
@app.get("/chore/<int:id>/done")
def chore_done(id):
    with connect_db() as client:
        # Add the thing to the DB
        sql = "UPDATE chores SET done=1 WHERE id=?"
        params = [id]
        client.execute(sql, params)

        # Go back to the home page
        flash(f"chore #{id} is done!", "success")
        return redirect("/chores")
    

#-----------------------------------------------------------
# Route for picking a chore
#-----------------------------------------------------------
@app.get("/chore/<int:id>/pick")
def chore_pick(id):
    # Get the user from the session
    pid = session.get("pid", None)
    if pid:  
        with connect_db() as client:
            # Add the chore to the "your_chores" table
            sql = "UPDATE chores SET person_id=? WHERE id=?"
            params = [pid, id]
            client.execute(sql, params)

    return redirect("/chores")   


#-----------------------------------------------------------
# Route for resetting the chore
#-----------------------------------------------------------
@app.get("/chore/<int:id>/reset")
def chore_reset(id):
    with connect_db() as client:
        # Add the chore to the "your_chores" table
        sql = "UPDATE chores SET done=0, person_id=NULL WHERE id=?"
        params = [id]
        client.execute(sql, params)
        return redirect("/chores")   


#-----------------------------------------------------------
# Route for adding a person, using data posted from a form
#-----------------------------------------------------------
@app.post("/person")
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
