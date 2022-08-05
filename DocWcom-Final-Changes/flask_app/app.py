from io import BytesIO

from flask import Flask, flash, render_template, request, send_file,  redirect, session

from flask_sqlalchemy import SQLAlchemy 
import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb
import mysql.connector


app = Flask(__name__)
connection= MySQLdb.connect(host="fra1.hostarmada.net", user="boutitne_admin", password="ZNwmdsyZZQq3", db="boutitne_docwcom")
app.config['SECRET_KEY'] = 'MYcqbd4SECRETfy327b8KEY'

def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           

@app.route('/',methods=['GET', 'POST'])
def index():
    #print("hi")
    if session.get('logged_in') == True:
        
       # print("hi2")
        if session['role'] == "manager":
            change = session['role']

            if request.method == 'POST':
                name = request.form['select1']
                if name == "tax":
                    cur = connection.cursor()
                    cur.execute("""SELECT doc_id, Name, Date_added, class FROM document WHERE class = "tax" """)
                    data = cur.fetchall()
                    #print(data)
                    return render_template('index.html', data=data, change=change)
                if name == "private":
                    cur = connection.cursor()
                    cur.execute("""SELECT doc_id, Name, Date_added, class FROM document WHERE class = "private" """)
                    data = cur.fetchall()
                    #print(data)
                    return render_template('index.html', data=data, change=change)
            cur = connection.cursor()
            cur.execute("""SELECT doc_id, Name, Date_added, class FROM document""")
            data = cur.fetchall()
            #print(data)
            return render_template('index.html', data=data, change=change) 
        if session['role'] == "ca":
            if request.method == 'POST':
                name = request.form['select1']
                if name == "tax":
                    cur = connection.cursor()
                    cur.execute("""SELECT doc_id, Name, Date_added, class FROM document WHERE class = "tax" """)
                    data = cur.fetchall()
                    #print(data)
                    return render_template('index.html', data=data)
            cur = connection.cursor()
            cur.execute("""SELECT doc_id, Name, Date_added, class FROM document WHERE class = "tax" """)
            data = cur.fetchall()
            #print(data)
            return render_template('index.html', data=data) 
        if session['role'] == "general":
            if request.method == 'POST':
                name = request.form['select1']
                if name == "tax":
                    cur = connection.cursor()
                    cur.execute("""SELECT doc_id, Name, Date_added, class FROM document WHERE class = "tax" """)
                    data = cur.fetchall()
                    #print(data)
                    return render_template('index.html', data=data)
            cur = connection.cursor()
            cur.execute("""SELECT doc_id, Name, Date_added, class FROM document WHERE class = "tax" OR  class = "general" """)
            data = cur.fetchall()
            #print(data)
            return render_template('index.html', data=data) 
    return render_template('index.html')
        


@app.route('/upload',methods=['POST'])
def upload():
    if request.method == 'POST':
        cls = request.form['teamDropdown']
        name = request.form['fname']
        content = request.files['file'].read()
        fname = request.files['file'].filename
        print(fname)
        cursor = connection.cursor()
        sql_insert_blob_query = """ INSERT INTO document
                          (name, file, class, fname) VALUES (%s,%s,%s,%s)"""
       
        # Convert data into tuple format
        insert_blob_tuple = (name, content, cls, fname)
        result = cursor.execute(sql_insert_blob_query, insert_blob_tuple)
        connection.commit()
        flash('File uploaded Successfully!')
        print("Image and file inserted successfully as a BLOB into python_employee table")

        return redirect('/')
    return render_template('index.html')


    
@app.route('/download/<upload_id>')
def download(upload_id):
  cursor = connection.cursor()
  sql_fetch_blob_query = """SELECT * from document where doc_id = %s"""

  cursor.execute(sql_fetch_blob_query, (upload_id,))
  record = cursor.fetchall()
  for row in record:
    file = row[3]
    name = row[5]

  return send_file(BytesIO(file), attachment_filename=name, as_attachment=True)

   
@app.route('/change_class/<upload_id>', methods=['GET', 'POST'])
def change_class(upload_id):
  print("hi")
  name = request.form['select2']
  cursor = connection.cursor()
  cursor.execute ("""UPDATE document SET class=%s where doc_id=%s""" , (name, upload_id))
  connection.commit()
  flash('Class changed!')
  return redirect('/')  

@app.route('/name_class/<upload_id>', methods=['GET', 'POST'])
def name_class(upload_id):
  print("hi")
  name = request.form['namechange']
  print(name)
  print(upload_id)
  cursor = connection.cursor()
  cursor.execute ("""UPDATE document SET Name=%s where doc_id=%s""" , (name, upload_id))
  connection.commit()
  flash('Name changed!')
  return redirect('/') 

@app.route("/login", methods=["POST", "GET"])
def login():
    msg = ''
    if request.method == "POST":
        #session["email"] = request.form.get("email")
        email = request.form.get("email") 
        sql_fetch_blob_query = """SELECT role,email from role where email = %s"""
        cursor = connection.cursor()        
        cursor.execute(sql_fetch_blob_query, (email,))
        record = cursor.fetchone()
        #print(record)
        
        if record:
            # Create session data, we can access this data in other routes
            session['logged_in'] = True
            session['role'] = record[0]
            session['email'] = record[1]
            # Redirect to home page
            r = session['role']
            e = session['email']
           # print(e)
            #print(r)
            flash('Login Success!')

            return redirect("/")
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
            flash('Incorrect credentials')
    return render_template("index.html", msg=msg)
 
 
@app.route("/logout", methods=["POST", "GET"])
def logout():
    
    session.pop('role', None)
    session.pop('email', None)
    session.pop('logged_in', None)
    flash("Successfully Logged out!")
    return redirect("/")

@app.route("/home", methods=["POST", "GET"])
def home():
    return render_template('index.html')
