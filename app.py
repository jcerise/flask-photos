from __future__ import with_statement
import sys
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash
from werkzeug import utils
from flask.ext.dropbox import Dropbox, DropboxBlueprint

import dbsettings


app = Flask(__name__)
app.config.from_object(dbsettings)

dropbox = Dropbox(app)
dropbox.register_blueprint(url_prefix='/dropbox')


@app.route('/')
def home():
    loginUrl = ''
    userInfo = ''
    metadata = ''

    linked = dropbox.session.is_linked()
    sys.stdout.write(str(linked))
    if not linked:
        loginUrl = dropbox.login_url
    else:
        client = dropbox.client
        userInfo = client.account_info()['display_name']
        sys.stdout.write(userInfo[1])
        metadata = client.metadata('/')

    return render_template('list_galleries.html', linked=linked, loginUrl=loginUrl, userInfo=userInfo, metadata=metadata)


@app.route('/success/<path:filename>')
def success(filename):
    return u'File successfully uploaded as /%s' % filename


@app.route('/upload', methods=('GET', 'POST'))
def upload():
    if not dropbox.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        file_obj = request.files['file']

        if file_obj:
            client = dropbox.client
            filename = utils.secure_filename(file_obj.filename)

            # Actual uploading process
            result = client.put_file('/' + filename, file_obj.read())

            path = result['path'].lstrip('/')
            return redirect(url_for('success', filename=path))

    return u'<form action="" method="post" enctype="multipart/form-data">' \
           u'<input name="file" type="file">' \
           u'<input type="submit" value="Upload">' \
           u'</form>'

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('home'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run()