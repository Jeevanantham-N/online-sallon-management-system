from flask import Flask, request,render_template,json,Response,request,jsonify,redirect
import pyrebase,json
import time
import schedule
import random
import smtplib
from time import gmtime, strftime

app = Flask(__name__)

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

def loop():
	def job():
		admin_ = db.child("booking").get().val()
		for a in admin_:
			time_ = db.child("booking").child(a).get().val()
			for t in time_:
				booked_ = db.child("booking").child(a).child(t).update({"booked":0})

	schedule.every().day.at("12:00").do(job)
	while True:
		schedule.run_pending()
		time.sleep(1)


@app.route('/')
def index():
	return render_template("index.html")

@app.route('/adminregister')
def rootadminRegister():
	return render_template("adminRegisterForm.html")

@app.route('/userregister')
def userregister():
	return render_template("userRegisterForm.html")

@app.route('/adminregisterdb',methods=['POST','GET'])
def adminRegisterdb():
	adminDet = request.form
	if str(adminDet['pwd']) == str(adminDet['repwd']):
		admin = {
			"name":adminDet["name"],
			"phone":adminDet["phone"],
			"email":adminDet["email"],
			"password":adminDet["pwd"],
			"latitude":adminDet["latitude"],
			"longitude":adminDet["longitude"],
			"chairscount":adminDet["total"],
			"status":[0]
		}
		try:
			val_ = db.child("admin").get().val()
			if str(adminDet["phone"]) in val_:
				return render_template("adminRegisterForm.html",error = "number already exists")
		except:
			pass
		db.child("admin").child(adminDet["phone"]).set(admin)
		timeList = []
		timeM = '00'
		for timeH in range(7,22):
			timeList.append(str(timeH)+str(':')+str(timeM))
			timeList.append(str(timeH)+str(':')+str(int(timeM)+30))
		json = {
			"total":int(adminDet["total"]),
			"booked":0
		}
		for i in timeList:
			db.child("booking").child(adminDet["phone"]).child(i).set(json)
		return render_template("index.html")
	else:
		return render_template("adminRegisterForm.html",error = "password mismatch")

@app.route('/userregisterdb',methods=['POST','GET'])
def userregisterdb():
	adminDet = request.form
	if str(adminDet['pwd']) == str(adminDet['repwd']):
		admin = {
			"name":adminDet["name"],
			"phone":adminDet["phone"],
			"password":adminDet["pwd"],
			"email":adminDet["email"],
			"status":[0]
		}
		try:
			val_ = db.child("users").get().val()
			if str(adminDet["phone"]) in val_:     
				return render_template("userRegisterForm.html",error = "number already exists")
		except:
			pass

		db.child("users").child(adminDet["phone"]).set(admin)
		return render_template("index.html")
	return render_template("userRegisterForm.html",error = "password mismatch")

@app.route('/background_process')
def background_process():
	time_ = request.args.get('time', 0, type=str)
	seats_ = request.args.get('seats', 0, type=int)
	uid = request.args.get('uid', 0, type=str)
	pwd = request.args.get('pwd', 0, type=str)
	isvalid = db.child("users").get().val()
	seats_ = int(seats_)
	uid = str(uid)
	pwd = str(pwd)
	if time_[0] == '0':
		time_ = time_[1:len(time_)+1]

	if uid in isvalid:
		verifypass = db.child("users").child(uid).get().val()["password"]
		if verifypass == pwd:
			refdb2 = db.child("booking").get().val()   
			available = []
			for no in refdb2:
				booked = db.child("booking").child(no).child(time_).get().val()["booked"]
				total = db.child("booking").child(no).child(time_).get().val()["total"]
				if booked <= total and (total-booked)>=seats_:
					admin = db.child("admin").child(no).get().val()
					json = {
						"name":admin["name"],
						"address":{
							"lat":admin["latitude"],
							"long":admin["longitude"]
								},
						"email":admin["email"],
						"mobile":no
						}
					available.append(json)
			return jsonify(json=available)
		else:
			return jsonify(json = "1")
	else:
		return jsonify(json ="0")

@app.route('/booking')
def booking():
	uid = request.args.get('uid', 0, type=str)
	oid = request.args.get('phone', 0, type=str)
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
			otp +=str(random.randint(0, 9))
		json_ = {
			"oid":oid,
			"uid":uid,
			"time":dt_,
			"booked":seats_,
			"otp":otp
		}
		upast_.append(json_)
		opast_.append(json_)
		update_ = db.child("admin").child(oid).update({"status":opast_})
		update_ = db.child("users").child(uid).update({"status":upast_})
		result = "seats is booked ... in "+oid
		return jsonify(json=result,otp=otp)
	else:
		result = "Seats are filled... in " + oid
		return jsonify(json=result)

@app.route('/isvaliddata')
def isvaliddata():
	uid = request.args.get('uid', 0, type=str)
	pwd = request.args.get('pwd', 0, type=str)
	isvalid = db.child("users").get().val()
	uid = str(uid)
	pwd = str(pwd)
	if uid in isvalid:
		verifypass = db.child("users").child(uid).get().val()["password"]
		if verifypass == pwd:
			return jsonify(json="true")
		else:
			return jsonify(json = "1")
	else:
		return jsonify(json ="0")

@app.route('/cancelling')
def cancelling():
	uid = request.args.get('uid', 0, type=str)
	phone = request.args.get('phone', 0, type=str)
	time_ = request.args.get('time', 0, type=str)
	seats_ = request.args.get('seats', 0, type=int)
	otp = request.args.get('otp', 0, type=str)

	seats_ = int(seats_)
	if time_[0] == '0':
		time_ = time_[1:len(time_)+1]
	
	getBookval = db.child("booking").child(phone).child(time_).get().val()["booked"]
	book = db.child("booking").child(phone).child(time_).update({"booked":getBookval-seats_})
	upast_ = db.child("users").child(uid).get().val()["status"]
	opast_ = db.child("admin").child(phone).get().val()["status"]
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
				db.child("admin").child(phone).child("status").child(i).remove()
				break
		except:
			pass
	result = "seats is cancelled... in " + phone
	return jsonify(json=result)

@app.route("/login")
def login():
	user = request.args.get('user', 0, type=str)
	if user=="admin":
		return redirect("view.html")
	else:
		return render_template("adminLoginForm.html")

@app.route("/userstatus")
def userstatus():
	uid = request.args.get('uid', 0, type=str)
	pwd = request.args.get('pwd', 0, type=str)
	isvalid = db.child("users").get().val()
	uid = str(uid)
	pwd = str(pwd)
	if uid in isvalid:
		verifypass = db.child("users").child(uid).get().val()["password"]
		if verifypass == pwd:
			present_ = db.child("users").child(uid).get().val()["status"]
			present_.pop(0)
			for i in present_:
				if None == i:
					present_.remove(i)
			present_ = present_[::-1]
			if len(present_) == 0:
				return jsonify(json="false")
			return jsonify(json=present_)
		else:
			return jsonify(json = "1")
	else:
		return jsonify(json ="0")

@app.route("/adminstatus")
def adminstatus():
	oid = request.args.get('oid', 0, type=str)
	pwd = request.args.get('pwd', 0, type=str)
	isvalid = db.child("admin").get().val()
	oid = str(oid)
	pwd = str(pwd)

	if oid in isvalid:
		verifypass = db.child("admin").child(oid).get().val()["password"]
		if verifypass == pwd:
			present_ = db.child("admin").child(oid).get().val()["status"]
			present_.pop(0)
			for i in present_:
				if None == i:
					present_.remove(i)
			present_ = present_[::-1]
			if len(present_) == 0:
				return jsonify(json="false")

			return jsonify(json=present_)
		else:
			return jsonify(json = "1")
	else:
		return jsonify(json ="0")

@app.route("/userupdate")
def userupdate():
	uid = request.args.get('uid', 0, type=str)
	isvalid = db.child("users").get().val()
	uid = str(uid)
	
	if uid in isvalid:
		fetch = db.child("users").child(uid).get().val()
		return jsonify(json=fetch)
	else:
		return jsonify(json="false")

@app.route("/adminupdate")
def adminupdate():
	oid = request.args.get('oid', 0, type=str)
	pwd = request.args.get('pwd', 0, type=str)
	isvalid = db.child("admin").get().val()
	oid = str(oid)
	pwd = str(pwd)
	
	if oid in isvalid:
		verifypass = db.child("admin").child(oid).get().val()["password"]
		if verifypass == pwd:
			fetch = db.child("admin").child(oid).get().val()
			return jsonify(json=fetch)
		else:
			return jsonify(json="1")
	else:
		return jsonify(json="0")

@app.route("/otpadmin")
def otpadmin():
	oid = request.args.get('oid', 0, type=str)
	pwd = request.args.get('pwd', 0, type=str)
	isvalid = db.child("admin").get().val()
	oid = str(oid)
	pwd = str(pwd)
	if oid in isvalid:
		verifypass = db.child("admin").child(oid).get().val()["password"]
		if verifypass == pwd:
			otp = ""
			for i in range(0,3):
				otp +=str(random.randint(0, 9))
			server = smtplib.SMTP('smtp.gmail.com', 587)
			server.starttls()
			emailid = db.child("admin").child(oid).get().val()["email"]
			server.login("jevvjeeva001@gmail.com", "yjlo vmor dsgv mlmf")
			server.sendmail("jevvjeeva001@gmail.com", emailid,otp)
			server.quit()
			return jsonify(json=otp)
		else:
			return jsonify(json="1")
	else:
		return jsonify(json="0")

@app.route("/otpuser")
def otpuser():
	uid = request.args.get('uid', 0, type=str)
	pwd = request.args.get('pwd', 0, type=str)
	isvalid = db.child("users").get().val()
	uid = str(uid)
	pwd = str(pwd)
	if uid in isvalid:
		verifypass = db.child("users").child(uid).get().val()["password"]
		if verifypass == pwd:
			otp = ""
			for i in range(0,3):
				otp +=str(random.randint(0, 9))
			server = smtplib.SMTP('smtp.gmail.com', 587)
			server.starttls()
			emailid = db.child("users").child(uid).get().val()["email"]
			server.login("jevvjeeva001@gmail.com", "yjlo vmor dsgv mlmf")
			server.sendmail("jevvjeeva001@gmail.com", emailid,"your otp is..."+otp)
			server.quit()
			return jsonify(json=otp)
		else:
			return jsonify(json="1")
	else:
		return jsonify(json="0")

@app.route("/deleteuser")
def deleteuser():
	uid = request.args.get('uid', 0, type=str)
	db.child("users").child(uid).remove()
	return jsonify(json="0")

@app.route("/deleteadmin")
def deleteadmin():
	oid = request.args.get('oid', 0, type=str)
	db.child("admin").child(oid).remove()
	db.child("booking").child(oid).remove()
	return jsonify(json="0")

if __name__ == '__main__':
	app.run(debug = True,port=5000)