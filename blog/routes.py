from flask import render_template, request, session, flash, redirect, url_for
from blog import app
from faker import Faker
from blog.models import Entry, db
from blog.forms import EntryForm
from blog.forms import LoginForm
import functools


@app.route("/")
def index():
   all_posts = Entry.query.filter_by(is_published=True).order_by(Entry.pub_date.desc())
   return render_template("homepage.html", all_posts=all_posts)

# #функція для створення фейкових публікацій
# def generate_entries(how_many=10):
#    fake = Faker()

#    for i in range(how_many):
#        post = Entry(
#            title=fake.sentence(),
#            body='\n'.join(fake.paragraphs(15)),
#            is_published=True
#        )
#        db.session.add(post)
#        db.session.commit()
   
def login_required(view_func):
   @functools.wraps(view_func)
   def check_permissions(*args, **kwargs):
       if session.get('logged_in'):
           return view_func(*args, **kwargs)
       return redirect(url_for('login', next=request.path))
   return check_permissions   


@app.route("/login/", methods=['GET', 'POST'])
def login():
   form = LoginForm()
   errors = None
   next_url = request.args.get('next')
   if request.method == 'POST':
       if form.validate_on_submit():
           session['logged_in'] = True
           session.permanent = True  # Use cookie to store session.
           flash('You are now logged in.', 'success')
           return redirect(next_url or url_for('index'))
       else:
           errors = form.errors
   return render_template("login_form.html", form=form, errors=errors)


@app.route('/logout/', methods=['GET', 'POST'])
def logout():
   if request.method == 'POST':
       session.clear()
       flash('You are now logged out.', 'success')
   return redirect(url_for('index'))


#функція для створення нових публікацій
@app.route("/new-post/", methods=["GET", "POST"])
@login_required
def create_entry():
   form = EntryForm()
   errors = None
   if request.method == 'POST':
       if form.validate_on_submit():
           entry = Entry(
               title=form.title.data,
               body=form.body.data,
               is_published=form.is_published.data
           )
           db.session.add(entry)
           db.session.commit()
       else:
           errors = form.errors
   return render_template("entry_form.html", form=form, errors=errors)

#функція для редагування публікацій
@app.route("/edit-post/<int:entry_id>", methods=["GET", "POST"])
@login_required
def edit_entry(entry_id):
   entry = Entry.query.filter_by(id=entry_id).first_or_404()
   form = EntryForm(obj=entry)
   errors = None
   if request.method == 'POST':
       if form.validate_on_submit():
           form.populate_obj(entry)
           db.session.commit()
       else:
           errors = form.errors
   return render_template("entry_form.html", form=form, errors=errors)


# #функція створення/редагування публікації
# @app.route("/post/<int:entry_id>", methods=["GET", "POST"])
# @login_required
# def create_edit_entry(entry_id):
#    errors = None
#    if entry_id==0:    
#     form = EntryForm()
#     if request.method == 'POST':
#        if form.validate_on_submit():
#            entry = Entry(
#                title=form.title.data,
#                body=form.body.data,
#                is_published=form.is_published.data
#            )
#            db.session.add(entry)
#            db.session.commit()
#        else:
#            errors = form.errors
#     else:  
#        entry = Entry.query.filter_by(id=entry_id).first_or_404()
#        form = EntryForm(obj=entry)
#        errors = None
#        if request.method == 'POST':
#             if form.validate_on_submit():
#                 form.populate_obj(entry)
#                 db.session.commit()
#             else:
#                 errors = form.errors
#    return render_template("entry_form.html", form=form, errors=errors)


# #видалення публікації
# @app.route("/post/<int:entry_id>", methods=["POST"])
# @login_required
# def delete_entry(entry_id):
#     entry = Entry.query.filter_by(id=entry_id).first_or_404()
#     db.session.delete(entry)
#     db.session.commit()
#     flash('Видалити публікацію', 'success')
#     return redirect(url_for('index'))


@app.route("/drafts/", methods=['GET'])
@login_required
def list_drafts():
   drafts = Entry.query.filter_by(is_published=False).order_by(Entry.pub_date.desc())
   return render_template("drafts.html", drafts=drafts)