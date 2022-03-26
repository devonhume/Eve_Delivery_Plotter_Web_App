from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap4
from flask_modals import Modal, render_template_modal
from forms import LoginForm, RegisterForm, CommentForm, CurrentSystem, AddAgent, ConvertAgent, GetCharacter, ChooseCharacter, DataCarrier
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_gravatar import Gravatar
from functools import wraps
import os
from plotter import Plotter
from init import app, modal, login_manager, db
from db_handler import User, DbHandler, Character

# Create Database Handler and Plotter Objects

db_handler = DbHandler(db)
my_plotter = Plotter(db_handler)
my_data = DataCarrier()


# ------------------ Routes --------------------------

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# Test Route, to be removed
@app.route('/test/<pars>')
def test(pars):
    print(pars)
    return redirect(url_for('plotter'))




# Home
@app.route('/', methods=['GET', 'POST'])
def home():
    '''Home page currently exists only to either log in user or register a new user. Once a user is logged in, it will
    automatically redirect to /plotter'''

    # If Logged In, redirect to /plotter
    if current_user.is_authenticated:
        return redirect(url_for('plotter', conf=None))

    # If not logged in, render page
    else:

        # Login Form
        login_form = LoginForm()
        if login_form.login.data and login_form.validate_on_submit():
            auth = db_handler.authenticate_user(login_form.email.data, login_form.password.data)
            if auth == 'email_fail':
                flash('Email not found -- Correct Email or Register New Account.', 'danger')
                return redirect(url_for('home'))
            elif auth == 'pass_fail':
                flash('Password Incorrect', 'danger')
                return redirect(url_for('home'))
            else:
                db_handler.log_in_user(auth)
                flash('Login Successful.', 'success')
                return redirect(url_for('home'))

        # Register Form
        reg_form = RegisterForm()
        if reg_form.register.data and reg_form.validate_on_submit():
            user_id = db_handler.register_user(
                name=reg_form.name.data,
                email=reg_form.email.data,
                password=reg_form.password.data
            )
            db_handler.log_in_user(user_id)
            flash('You have been registered!', 'success')
            return redirect(url_for('home'))

        # Page Render
        return render_template(
            'index.html',
            login_form=login_form,
            register_form=reg_form,
            logged_in=current_user.is_authenticated,
            username=None
        )


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')

# Plotter - Main App
@app.route('/plotter', methods=['GET', 'POST'])
@login_required
def plotter():
    '''The plotter route function handles the modal forms for getting game information from the user and passes them to
    the plotter object.'''

    global my_plotter
    if my_plotter.character:
        print(f"Character: {my_plotter.character.name}")
        my_plotter.set_current_system(db_handler.get_char_system(my_plotter.character.name))
    # Pull possible characters for user
    my_data.char = current_user.characters
    # Tell the page how many characters there are
    my_data.flag = len(char)
    # Form for adding a new character
    my_data.char_form = GetCharacter()
    # Form for choosing among multiple characters
    my_data.choose_char_form = ChooseCharacter()
    # Form to change current system
    my_data.current_system_form = CurrentSystem()
    # Form to add agent
    my_data.add_agent_form = AddAgent()

    # If Character not confirmed, flag add/choose/confirm modals

    # If multiple characters, populate form with them
    if my_data.flag > 1:
        my_data.choose_char_form.char.choices = [(g.name, g.name) for g in char]

    # Add new character to Database
    if my_data.char_form.submit_char.data and my_data.char_form.validate_on_submit():
        new_char = Character(
            name=my_data.char_form.name.data,
            current_system=my_data.char_form.system.data,
            users_id=current_user.id
        )
        db.session.add(new_char)
        db.session.commit()

        # Reload page - will confirm choice

    # If user chooses from multiple characters, pass character to app and reload
    if my_data.choose_char_form.submit_choice.data and my_data.choose_char_form.validate_on_submit():
        my_plotter.character = Character.query.filter_by(name=my_data.choose_char_form.char.data).first()
        return redirect(url_for('plotter'))


    # If Character Confirmed
    # Get Agents and Missions to Display
    my_data.agents_list = my_plotter.refresh_agents()
    my_data.missions_list = my_plotter.refresh_missions()
    my_data.character = my_plotter.character
    my_data.current_destination = my_plotter.current_goal

    # Change Current System
    if my_data.current_system_form.submit_cs.data and my_data.current_system_form.validate_on_submit():
        db_handler.set_char_system(my_plotter.character, my_data.current_system_form.system.data)
        return redirect(url_for('process', pars='change_cs,' + my_data.current_system_form.system.data))

    # Add Agent
    if my_data.add_agent_form.submit_agent.data and my_data.add_agent_form.validate_on_submit():
        if not db_handler.check_agent(my_data.add_agent_form.agent_name.data):
            agent = db_handler.create_agent(my_data.add_agent_form.agent_name.data, my_data.add_agent_form.system.data)
        else:
            agent = db_handler.get_agent(my_data.add_agent_form.agent_name.data)
        print(f"Player System: {my_plotter.player.system}")
        my_plotter.add_agent(agent.name, my_data.add_agent_form.jumps.data)
        return redirect(url_for('plotter'))

    #
    print(f"agents: {my_data.agents_list}")
    print(f"missions: {my_data.missions_list}")
    return render_template(
        'plotter.html',
        logged_in=current_user.is_authenticated,
        username=current_user.username,
        data=my_data
    )

@app.route('/process/<pars>')
def process(pars):

    print(pars)
    parms = pars.split(',')
    print(parms)

    # Set Character
    if parms[0] == 'set_char':
        print("Set-Char True")
        my_plotter.set_character(parms[1])
        print(my_plotter.character.name)

    # Change Current System
    if parms[0] == 'change_cs':
        my_plotter.set_current_system(parms[1])

    # Add Agent
    if parms[0] == 'add_agent':
        result = my_plotter.add_agent(parms[1])
        if result:
            flash(result, 'error')

    # Remove Agent
    if parms[0] == 'remove_agent':
        my_plotter.remove_agent(parms[1])

    # Convert Agent
    if parms[0] == 'convert_agent':
        result = my_plotter.add_mission(parms[1])
        if result:
            flash(result, 'error')

    # Complete Mission
    if parms[0] == 'complete_mission':
        my_plotter.complete_mission(parms[1])

    return redirect(url_for('plotter'))


@app.route('/agent-modal/<agent>')
def agent_modal(agent):
    return render_template(
        'agent-modal.html',
        logged_in=current_user.is_authenticated,
        username=current_user.username,
        data=my_data,
        agent=agent
    )


@app.route('/mission-modal/<mission>')
def mission_modal(mission):
    return render_template(
        'mission-modal.html',
        logged_in=current_user.is_authenticated,
        username=current_user.username,
        data=my_data,
        mission=mission
    )


@app.route('/logout')
def logout():
    my_plotter.reset()
    logout_user()
    flash('You have logged out.', 'success')
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)