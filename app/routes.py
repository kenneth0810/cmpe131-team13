from flask import render_template
from flask import redirect, request, session, url_for
from flask import flash
from app import myapp_obj, db
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from datetime import datetime

from wtforms.validators import Email
#from flask_mail import Mail, Message
#from app import mail
from app.send_emails import sendEmails
from app.register import registerUser 
from app.models import User, Emails, Todo, Profile, Message
from app.login import LoginForm
from app.todo import TodoForm
from app.profile import BioForm, PasswordForm, DeleteForm
from app.chat import ChatForm

#Yue Ying Lee
# index page is the page user see before registering or logging in
@myapp_obj.route("/")
def index():
    return render_template('index.html' )

#Yue Ying Lee
@myapp_obj.route("/homepage")
@login_required
def homepage():
    user = current_user
    user_fullname = user.fullname
    return render_template('homepage.html', user_fullname = user_fullname)

#Yue Ying Lee
@myapp_obj.route("/login", methods=['GET', 'POST'])
def login():
    # create form
    form = LoginForm()
    if form.validate_on_submit():
        valid_user = User.query.filter_by(username = form.username.data).first()
        if valid_user != None:
          if valid_user.check_password(form.password.data)== True:
             print("valid username, and valid password")
             login_user(valid_user)
             flash(f'Here are the input {form.username.data} and {form.password.data}')
             return redirect(url_for('homepage'))
          else :
             flash(f'Invalid password. Try again')
        else: 
             flash(f'Invalid username. Try again or register an account')  

    return render_template('login.html', form=form)

@myapp_obj.route("/members/<string:name>/")
def getMember(name):
    return escape(name)

#Yue Ying Lee
@myapp_obj.route("/logout", methods = ['GET', 'POST'])
@login_required
def logout():
       logout_user()
       return redirect(url_for('login'))

#Yue Ying Lee
@myapp_obj.route("/register", methods =['GET', 'POST'])
def register():
        #create registration form
        registerForm  = registerUser()
        if registerForm.validate_on_submit():
          same_Username = User.query.filter_by(username = registerForm.username.data).first()
          print("starting to find user")
          if same_Username == None:
            user = User(fullname = registerForm.fullname.data, username= registerForm.username.data)
            user.set_password(registerForm.password.data)
            print("Created user, adding user to db")
            db.session.add(user)
            db.session.commit()
            #redirect user to login page to log in with their new account
            flash(f'Here are the input {registerForm.username.data}, {registerForm.fullname.data} and {registerForm.password.data}')
            return redirect('/login')
          else :
             flash('The username is not available. Please choose another username')
        return render_template('register.html', registerForm=registerForm)

#Yue Ying Lee
@myapp_obj.route("/send_emails", methods = ['GET', 'POST'])
@login_required
def send_emails():
   send_emails_form = sendEmails()
   if send_emails_form.validate_on_submit():
    sender_id = current_user.id
    valid_recipients =  User.query.filter_by(username = send_emails_form.recipients.data).first()
    if (valid_recipients):
        flash(f' Valid recipients.')
        recipients_id = valid_recipients.id
        email = Emails (sender_id = sender_id, recipients_id = recipients_id, subject_line=send_emails_form.subject_line.data, email_body= send_emails_form.email_body.data)
        db.session.add(email)
        db.session.commit()
        flash(f'Email successfully sent!')
        return redirect('/homepage')
    else:
     flash(f' Invalid recipients. Retype username or go back to homepage.')

   return render_template('send_emails.html', send_emails_form = send_emails_form)


@myapp_obj.route("/todo", methods = ['GET', 'POST'])
@login_required
def add_todo():
    form = TodoForm()
    if form.validate_on_submit():
        todo = Todo(user = current_user, task = form.task.data)
        db.session.add(todo)
        db.session.commit()
        flash('Successfully added a new task.')
        return redirect(url_for('add_todo'))

    user = current_user
    all_tasks = Todo.query.all()
    task_list = [] #a list to append all exisiting tasks for current user to be passed into the html file
    for t in all_tasks:
        if t.user_id == user.id:
            task_list.append(t)
    return render_template("todo.html", form=form, tasks=task_list, user=user)

@myapp_obj.route('/delete-task/<int:id>', methods=['GET','POST'])
@login_required
def delete_task(id):
    task = Todo.query.filter(Todo.id == id).first()
    if task:
        db.session.delete(task) 
        db.session.commit()
        flash('Task deleted')
    else:
        flash('There is no task to be deleted.')
    return redirect(url_for('add_todo'))

@myapp_obj.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    bio_form = BioForm()
    if bio_form.validate_on_submit():
        #if a current bio exists and a new bio is submitted, delete the current bio and replace it with the new bio
        curr_bio = Profile.query.filter_by(user=current_user).first()
        if curr_bio:
            db.session.delete(curr_bio)
        new_bio = Profile(user=current_user, bio=bio_form.bio.data)
        db.session.add(new_bio)
        db.session.commit()
        flash('Successfully updated a new bio.')
    else:
        #if nothing is submitted, the bio form will be empty, so assign the form.bio to the current bio
        curr_bio = Profile.query.filter_by(user=current_user).first()
        if curr_bio:
            bio_form.bio.data = curr_bio.bio
    
    pw_form = PasswordForm()
    if pw_form.validate_on_submit():
        user = current_user
        if user.check_password(pw_form.old_password.data):
            if not user.check_password(pw_form.new_password.data):
                user.set_password(pw_form.new_password.data)
                db.session.commit()
                flash('Successfully updated password.')
            else:
                flash('New password and old password are the same. Please try again.')
        else:
            flash('Wrong password entered. Please try again.')
    return render_template('profile.html', bform=bio_form, pform=pw_form, user=current_user)

@myapp_obj.route('/delete-bio/<int:id>', methods=['GET','POST'])
@login_required
def delete_bio(id):
    b = Profile.query.filter(Profile.user_id == id).first()
    if b:
        db.session.delete(b) 
        db.session.commit()
        flash('Bio deleted')
    else:
        flash('There is no bio to be deleted.')
    return redirect(url_for('profile'))

@myapp_obj.route('/delete_accoutn', methods=['GET', 'POST'])
@login_required
def delete_account():
    form = DeleteForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            db.session.delete(current_user)
            db.session.commit()
            logout_user()
            flash('Account was successfully deleted.')
            return redirect(url_for('/login'))
    else:
        flash('Incorrect password.')
        return redirect(url_for('homepage'))
    
@myapp_obj.route('/chat', methods=['GET', 'POST'])
@login_required
def start_chat():
    form = ChatForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.recipient_name.data).first() is not None:
            dateAndTime = datetime.now()
            message = Message(username=current_user.username, subject=form.subject.data, message=form.message.data, sending_user=current_user.id, 
            receiving_user=User.query.filter_by(username=form.recipient_name.data).first().id, timestamp=dateAndTime)
            db.session.add(message)
            db.session.commit()
            return redirect(url_for('start_chat'))
        else:
            flash('Invalid recipient', 'danger')
    messages = Message.query.filter_by(receiving_user=current_user.id).all()
    return render_template('chat.html', user=current_user, form=form, messages=messages)
