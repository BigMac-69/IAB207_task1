from flask import Blueprint, render_template, redirect, url_for
from .models import Destination, Comment
from .forms import DestinationForm, CommentForm
from . import db
import os
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user

destbp = Blueprint('destinations', __name__, url_prefix='/destinations')

@destbp.route('<id>')
def show(id):
    #pass an example objet until our DB is ready
    destination = db.session.scalar(db.select(Destination).where(Destination.id==id))
    #destination = db.session.scalar(db.select(Destination.where(Destination.id==id)))
    cform = CommentForm()    
    return render_template('destinations/show.html', destination=destination, form=cform)



@destbp.route('/<id>/comment', methods = ['GET', 'POST'])
@login_required
def comment(id):
  # here the form is created  form = CommentForm()
  form = CommentForm()
  if form.validate_on_submit():	#this is true only in case of POST method
    destination = db.session.scalar(db.select(Destination).where(Destination.id==id))
    comment = Comment(text=form.text.data, destination=destination, user=current_user)
    db.session.add(comment)
    db.session.commit()
    print(f"The following comment has been posted: {form.text.data}")
  # notice the signature of url_for
  return redirect(url_for('destinations.show', id=1))



@destbp.route('/create', methods = ['GET', 'POST'])
@login_required
def create():
  #print('Method type: ', request.method)
  form = DestinationForm()
  if form.validate_on_submit():
    db_file_path = check_upload_file(form)
    # call the function that checks and returns image
    #db_file_path = check_upload_file(form)
    destination = Destination(name=form.name.data,
    description=form.description.data, 
    image =db_file_path,
    currency=form.currency.data)
    # add the object to the db session
    db.session.add(destination)
    # commit to the database
    db.session.commit()
    print('Successfully created new travel destination', 'success')
    return redirect(url_for('destinations.create'))
  return render_template('destinations/create.html', form=form)

def check_upload_file(form):
  # get file data from form  
  fp = form.image.data
  filename = fp.filename
  # get the current path of the module file… store image file relative to this path  
  BASE_PATH = os.path.dirname(__file__)
  # upload file location – directory of this file/static/image
  upload_path = os.path.join(BASE_PATH,'static/image',secure_filename(filename))
  # store relative path in DB as image location in HTML is relative
  db_upload_path = '/static/image/' + secure_filename(filename)
  # save the file and return the db upload path  
  fp.save(upload_path)
  return db_upload_path