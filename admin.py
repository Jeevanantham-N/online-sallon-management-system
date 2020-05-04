from flask import Flask,render_template,request,session,g,jsonify,url_for,redirect
import pyrebase
import time,json
import random
import smtplib
from time import gmtime, strftime

app = Flask(__name__)
app.secret_key = "dufhbhjfbj"

config = {
	"apiKey": "AIzaSyAfbocb05wSG_58sWE-8pCsHfMcf4g2sAU",
	"authDomain": "salonshop-28cd4.firebaseapp.com",
	"databaseURL": "https://salonshop-28cd4.firebaseio.com",
	"projectId": "salonshop-28cd4",
	"storageBucket": "salonshop-28cd4.appspot.com",
	"messagingSenderId": "143341249080",
	"appId": "1:143341249080:web:9b3b81537c10fdf08cbccd",
	"measurementId": "G-WKS88K0RJV"
	}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

timeList = []
timeM = '00'
for timeH in range(7,22):
    timeList.append(str(timeH)+str(':')+str(timeM))
    timeList.append(str(timeH)+str(':')+str(int(timeM)+30))

@app.route('/')
def userlogs():
    return render_template("userlogs.html")

@app.route('/dashboard')
def dashboard():
    if "id" in session:
        json_ = db.child("admin").child(session["id"]).get().val()
        return render_template("dashboard.html",json_ =json.dumps(json_))
    else:
        return redirect(url_for('adminlogs'))

@app.route('/salonspot')
def salonspot():
    if "id" in session:
        json_ = db.child("users").child(session["id"]).get().val()
        return render_template("salonspot.html",json_ =json.dumps(json_))
    else:
        return redirect(url_for('userlogs'))

@app.route('/adminlogs')
def adminlogs():
    return render_template("adminlogs.html")

@app.route("/adminregister")
def adminregister():
    name = request.args.get('name', 0, type=str)
    pwd = request.args.get('pwd', 0, type=str)
    phone = request.args.get('phone', 0, type=str)
    address = request.args.get('address', 0, type=str)
    total = request.args.get('total', 0, type=str)
    email = request.args.get('email', 0, type=str)
    admin = {
        "name":name,
        "phone":phone,
        "email":email,
        "pwd":pwd,
        "address":address,
        "chairscount":total,
        "status":[0]
    }
    try:
        val_ = db.child("admin").get().val()
        if str(phone) in val_:
            return jsonify(result = 0)
    except:
        pass

    db.child("admin").child(phone).set(admin)
    json = {
        "total":int(total),
        "booked":0
    }
    for i in timeList:
        db.child("booking").child(phone).child(i).set(json)
    return jsonify(result = "Log in")

@app.route("/adminlogin",methods = ["POST","GET"])
def adminlogin():
    form = request.form
    ids = db.child("admin").get().val()
    try:
        if str(form["phone"]) in ids:
            verifypass = db.child("admin").child(form["phone"]).get().val()["pwd"]
            if verifypass == str(form["pwd"]):
                session["id"] = form["phone"]
                return redirect(url_for('dashboard'))
            else:
                return render_template("adminlogs.html",error = "password wrong")
        else:
            return render_template("adminlogs.html",error = "not yet registered")
    except:
        return render_template("adminlogs.html",error = "not yet registered")

@app.route("/forgot")
def forgot():
    phone = str(request.args.get('phone', 0, type=str))
    admin = db.child("admin").get().val()

    if str(phone) in admin:
        pwd = db.child("admin").child(phone).get().val()["pwd"]
        otp = ""
        for i in range(0,3):
            otp +=str(random.randint(0, 9))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        emailid = db.child("admin").child(phone).get().val()["email"]
        server.login("jevvjeeva001@gmail.com", "yjlo vmor dsgv mlmf")
        server.sendmail("jevvjeeva001@gmail.com", emailid,"your pwd is..."+pwd)
        server.quit()
        return jsonify(json=1)
    else:
        return jsonify(json = 0)

@app.route("/adminstatus")
def adminstatus():
    oid = request.args.get('oid', 0, type=str)
    present_ = db.child("admin").child(oid).get().val()["status"]
    present_.pop(0)
    for i in present_:
        if None == i:
            present_.remove(i)
    present_ = present_[::-1]
    if len(present_) == 0:
        return jsonify(json="false")
    return jsonify(result=present_)

@app.route("/userregister")
def userregister():
    name = request.args.get('name', 0, type=str)
    pwd = request.args.get('pwd', 0, type=str)
    phone = request.args.get('phone', 0, type=str)
    email = request.args.get('email', 0, type=str)
    
    user = {
        "name":name,
        "email":email,
        "phone":phone,
        "pwd":pwd,
        "status":[0]
    }
    try:
        val_ = db.child("users").get().val()
        if str(phone) in val_:
            return jsonify(result = 0)
    except:
        pass
    db.child("users").child(phone).set(user)
    return jsonify(result = "Log in")

@app.route("/userlogin",methods = ["POST","GET"])
def userlogin():
    session.pop("id",None)
    form = request.form
    ids = db.child("users").get().val()
    try:
        if str(form["phone"]) in ids:
            verifypass = db.child("users").child(form["phone"]).get().val()["pwd"]
            if verifypass == str(form["pwd"]):
                session["id"] = form["phone"]
                return redirect(url_for('salonspot'))
            else:
                return render_template("userlogs.html",error = "password wrong")
        else:
            return render_template("userlogs.html",error = "not yet registered")
    except:
        return render_template("userlogs.html",error = "not yet registered")

@app.route("/forgotuser")
def forgotuser():
    phone = str(request.args.get('phone', 0, type=str))
    users = db.child("users").get().val()

    if str(phone) in users:
        pwd = db.child("users").child(phone).get().val()["pwd"]
        otp = ""
        for i in range(0,3):
            otp +=str(random.randint(0, 9))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        emailid = db.child("users").child(phone).get().val()["email"]
        server.login("jevvjeeva001@gmail.com", "yjlo vmor dsgv mlmf")
        server.sendmail("jevvjeeva001@gmail.com", emailid,"your pwd is..."+pwd)
        server.quit()
        return jsonify(json=1)
    else:
        return jsonify(json = 0)

@app.route('/background_process')
def background_process():
    time_ = request.args.get('time', 0, type=str)
    seats_ = request.args.get('seats', 0, type=int)
    uid = request.args.get('uid', 0, type=str)
    seats_ = int(seats_)
    uid = str(uid)
    if time_[0] == '0':
        time_ = time_[1:len(time_)+1]
    booking = db.child("booking").get().val()
    available = []
    for no in booking:
        booked = db.child("booking").child(no).child(time_).get().val()["booked"]
        total = db.child("booking").child(no).child(time_).get().val()["total"]
        if booked <= total and (total-booked)>=seats_:
            admin = db.child("admin").child(no).get().val()
            json = {
                "name":admin["name"],
                "address":admin["address"],
                "email":admin["email"],
                "mobile":no
                }
            available.append(json)
    print(available)
    return jsonify(json=available)

@app.route('/booking')
def booking():
    uid = request.args.get('uid', 0, type=str)
    oid = request.args.get('oid', 0, type=str)
    time_ = request.args.get('time', 0, type=str)
    seats_ = request.args.get('seats', 0, type=int)
    seats_ = int(seats_)

    if time_[0] == '0':
        time_ = time_[1:len(time_)+1]

    getBookval = db.child("booking").child(oid).child(time_).get().val()["booked"]
    getTotalval = db.child("booking").child(oid).child(time_).get().val()["total"]

    if getTotalval >= getBookval+seats_ :
        book = db.child("booking").child(oid).child(time_).update({"booked":getBookval+seats_})
        opast_ = db.child("admin").child(oid).get().val()["status"]
        upast_ = db.child("users").child(uid).get().val()["status"]
        dt_ = strftime("%Y-%m-%d %H:%M", gmtime())
        otp = ""
        for i in range(0,3):
            otp +=str(random.randint(1, 9))
        json_ = {
            "oid":oid,
            "uid":uid,
            "time":time_,
            "booked":seats_,
            "otp":otp
        }
        upast_.append(json_)
        opast_.append(json_)
        update_ = db.child("admin").child(oid).update({"status":opast_})
        update_ = db.child("users").child(uid).update({"status":upast_})
        result = "seats is booked ... in "+oid
        return jsonify(json=result,otp=str(otp))
    else:
        result = "Seats are filled... in " + oid
        return jsonify(json=1)

@app.route('/cancelling')
def cancelling():
    uid = request.args.get('uid', 0, type=str)
    oid = request.args.get('oid', 0, type=str)
    time_ = request.args.get('time', 0, type=str)
    seats_ = request.args.get('seats', 0, type=int)
    otp = request.args.get('otp', 0, type=str)
    print(uid,oid,time_,seats_,otp)
    seats_ = int(seats_)
    if time_[0] == '0':
        time_ = time_[1:len(time_)+1]

    getBookval = db.child("booking").child(oid).child(time_).get().val()["booked"]
    book = db.child("booking").child(oid).child(time_).update({"booked":getBookval-seats_})
    upast_ = db.child("users").child(uid).get().val()["status"]
    opast_ = db.child("admin").child(oid).get().val()["status"]
    print(upast_)
    print(opast_)
    for i in range(0,len(upast_)):
        try:
            if upast_[i]["otp"] == str(otp):
                db.child("users").child(uid).child("status").child(i).remove()
                break
        except:
            pass
    for i in range(0,len(opast_)):
        try:
            if opast_[i]["otp"] == str(otp):
                db.child("admin").child(oid).child("status").child(i).remove()
                break
        except:
            pass
    result = "seats is cancelled... in " + oid
    return jsonify(json=result)

@app.route("/userstatus")
def userstatus():
    uid = request.args.get('uid', 0, type=str)
    present_ = db.child("users").child(uid).get().val()["status"]
    present_.pop(0)
    for i in present_:
        if None == i:
            present_.remove(i)
    present_ = present_[::-1]
    if len(present_) == 0:
        return jsonify(json="false")
    return jsonify(json=present_)

@app.route("/deleteuser")
def deleteuser():
    uid = request.args.get('uid', 0, type=str)
    session.pop("id",None)
    db.child("users").child(uid).remove()
    return jsonify(json = 1)

@app.route("/deleteadmin")
def deleteadmin():
    oid = request.args.get('oid', 0, type=str)
    session.pop("id",None)
    db.child("admin").child(oid).remove()
    return jsonify(json = 1)

@app.route("/userlogout")
def userlogout():
    session.pop("id",None)
    return redirect(url_for('userlogs'))

@app.route("/adminlogout")
def adminlogout():
    session.pop("id",None)
    return redirect(url_for('adminlogs'))

if __name__ == "__main__":
    app.run(debug=True,port=5001)