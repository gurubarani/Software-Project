from flask import Flask, render_template, request, redirect, session, url_for, send_file, Response
import requests
from flask_table import Table, Col, LinkCol
import random
import csv,os
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

#SERVER_URL = "http://localhost:8001"
SERVER_URL = "https://kxt4vjniid.execute-api.us-east-1.amazonaws.com/prod"


class AdminTable(Table):
    Roll_Number = Col('Student Roll Number')
    Computational_Intelligence = Col('Computational Intelligence')
    Design_Patterns = Col('Design Patterns')
    Natural_Language_Processing = Col('Natural Language Processing')
    Parallel_and_Distributed_Computing = Col('Parallel and Distributed Computing')
    Semantic_Web = Col('Semantic Web')
    Wireless_and_Mobile_Computing = Col('Wireless and Mobile Computing')
    Game_Theory = Col('Game Theory')
    Information_Security = Col('Information Security')
    Wireless_Sensor_Networks = Col('Wireless Sensor Networks')


class UserTable(Table):
    cname = Col('Course Name')
    prefs = Col('Preference')

class StatsTable(Table):
    cname = Col('Course Name')
    count = Col('# of Students Opted')

class AttTable(Table):
    roll = Col('Roll Number')
    name = Col('Student Name')


def dupli_locate(lst):
    test_list = lst
    con = [0]*9
    oc_set = set()
    for idx, val in enumerate(test_list):
        if val != '-1':
            if val not in oc_set:
                oc_set.add(val)
            else:
                con[idx] = 1
                con[test_list.index(val)] = 1
    return con


def generate_admintable():
    global cname,atabledata
    res = requests.get(SERVER_URL + "/getallprefs").json()
    myname = []
    for i in cname:
        ns = i.replace(' ', '_')
        myname.append(ns)
    first = []
    for row in res:
        l = []
        vals = list(row.values())
        l.append(str(vals[0]))
        prefs = vals[1].split()
        for i in prefs:
            l.append(i)
        first.append(l)
    second = ['Roll_Number'] + myname
    data = []
    for row in first:
        work = zip(second,row)
        d = {}
        for a,b in work:
            d[a] = b
        data.append(d)
    #print(data)
    atabledata = data


def generate_usertable():
    global cname,prefs,utabledata
    try:
        prefs = requests.post(SERVER_URL + "/getprefs", data={'roll':session["roll"]}).json()[0]['prefs'].split()
        print(session["roll"])
        print("Look",prefs)
        first = zip(cname, prefs)
        res = []
        for a, b in first:
            d = {'cname': a, 'prefs': b}
            res.append(d)
        print("Data is ",res)
        utabledata = res
    except:
        utabledata = []


prefetch = requests.get(SERVER_URL + "/prefetch").json()
cid = []
cname = []
cdesc = []
seats_left = []
pref_assigned = [0]*5


def pref_assign_fetch():
    global pref_assigned
    pref_assigned = [0]*5
    res = requests.get(SERVER_URL + "/getallprefs").json()
    vals = []
    for row in res:
        vals.append(list(row.values()))
    roll = [row[0] for row in vals]
    i=0
    for row in roll:
        print(requests.post(SERVER_URL+"/getprefassigned",data={'roll':row}).json()[0]['exists'])
        pref_assigned[i]=requests.post(SERVER_URL+"/getprefassigned",data={'roll':row}).json()[0]['exists']
        i+=1

errstring = ""
console_err = ''
for row in prefetch:
    cid.append(row['cid'])
    cname.append(row['cname'])
    cdesc.append(row['cdesc'])
print(cname)

def seats_fetch():
    global seats_left
    seats_left = []
    seatsfetch = requests.get(SERVER_URL+"/seatsfetch").json()
    for row in seatsfetch:
        seats_left.append(row['seats_left'])

print(seats_left)
prefs = ['-1']*9
conflict = [0]*9
utabledata = []
atabledata = []
consoletable = None
attendance_for=''

@app.route("/")
def index():
    idx = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    print("__________Computed___________")
    chosen = random.sample(idx, 3)
    idrand = [cid[chosen[0]],cid[chosen[1]],cid[chosen[2]]]
    namerand = [cname[chosen[0]], cname[chosen[1]], cname[chosen[2]]]
    descrand = [cdesc[chosen[0]], cdesc[chosen[1]], cdesc[chosen[2]]]
    seats_fetch()
    seatsrand = [seats_left[chosen[0]], seats_left[chosen[1]], seats_left[chosen[2]]]

    if 'name' in session:
        if session['name'] == 'Administrator':
            admin = 1
            logged = 0
            print("Check")
            generate_admintable()
        elif len(session['name']) !=0:
            print(session['name'])
            admin = 0
            logged = 1
    else:
        logged = 0
        admin = 0
    return render_template("index.html", cid=idrand, cname=namerand, cdesc=descrand, seats_left=seatsrand, logged=logged, admin=admin)


@app.route("/admindownload")
def admindownload():
    try:
        keys = atabledata[0].keys()
        csv = ''
        for key in keys:
            csv+=key+','
        csv = csv[:-1]
        csv+='\n'
        for i in range(len(atabledata)):
            val = list(atabledata[i].values())
            csv += val[0] + ',' + val[1] + ',' + val[2] + ',' + val[3] + ',' + val[4] + ',' + val[5] + ',' + val[6] + ',' + val[7] + ',' + val[8] + ',' + val[9] + '\n'
        return Response(
            csv,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=AllPrefs.csv"}
        )

    except:
        return redirect(url_for('admin_console'))

@app.route("/userdownload")
def userdownload():
    keys = utabledata[0].keys()
    csv = ''
    for key in keys:
        csv+=key+','
    csv = csv[:-1]
    csv+='\n'
    for i in range(len(utabledata)):
        val = list(utabledata[i].values())
        csv+=val[0]+','+val[1]+'\n'
    return Response(
        csv,
        mimetype="text/csv",
        headers = {"Content-disposition":"attachment; filename=MyPrefs.csv"}
    )

@app.route("/regular_page")
def regular_page():
    if 'name' in session:
        if session['name'] == "Administrator":
            generate_admintable()
            admintable = AdminTable(atabledata, no_items="Nobody has filled prefs yet!")
            return render_template("regular-page.html", table=admintable, admin=1, logged=0)
        generate_usertable()
        usertable = UserTable(utabledata, no_items="You haven't filled prefs yet!")
        check = requests.post(SERVER_URL+"/getprefname", data={'roll': session["roll"]}).json()
        if len(check)!=0:
            text = "You have been assigned " + check[0]['cname'] + " as your elective!"
            return render_template("regular-page.html", table=usertable, admin=0, logged=1, assigned=text)
        else:
            check = requests.post(SERVER_URL+"/getprefsubmitted", data={'roll': session["roll"]}).json()[0]['exists']
            if check == 1:
                text = "You have committed your preferences. Wait for admin to assign"
                return render_template("regular-page.html", table=usertable, admin=0, logged=1, assigned=text)
            else:
                return render_template("regular-page.html", table=usertable, admin=0, logged=1, assigned='0')
    else:
        return redirect(url_for("index"))


@app.route("/courses")
def courses():
    if 'name' in session:
        logged = 1
        if session['name'] == 'Administrator':
            admin = 1
            logged=0
        else:
            admin = 0
            generate_usertable()
    else:
        logged = 0
        admin = 0
    seats_fetch()
    if 'name' in session:
        check = requests.post(SERVER_URL+"/getprefname", data={'roll': session["roll"]}).json()
        if len(check) != 0:
            text = "You have been assigned " + check[0]['cname'] + " as your elective!"
            return render_template("courses.html", cid=cid, cname=cname, cdesc=cdesc, seats_left=seats_left, logged=logged,
                                   prefs=prefs, conflict=conflict, admin=admin, errstring=errstring, assigned=text)
        else:
            check = requests.post(SERVER_URL+"/getprefsubmitted", data={'roll': session["roll"]}).json()[0][
                'exists']
            if check == 1:
                text = "You have committed your preferences. Wait for admin to assign"
                return render_template("courses.html", cid=cid, cname=cname, cdesc=cdesc, seats_left=seats_left,
                                       logged=logged, prefs=prefs, conflict=conflict, admin=admin, errstring=errstring, assigned=text)
    return render_template("courses.html", cid=cid, cname=cname, cdesc=cdesc, seats_left=seats_left,
                           logged=logged, prefs=prefs, conflict=conflict, admin=admin, errstring=errstring,
                           assigned='0')

@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/logout")
def logout():
    global prefs
    global conflict
    session.pop('name')
    session.pop('roll')
    prefs = ['-1']*9
    conflict = [0]*9
    return redirect(url_for('index'))


@app.route("/verify_user", methods=["POST"])
def verify_user():
    global prefs, utabledata, errstring, console_err
    errstring = ""
    console_err = ""
    payload = {'roll': request.form['roll'], 'spass': request.form['spass']}
    res = requests.post(SERVER_URL+"/verify", data=payload).json()
    print(res['name'])
    print(len(res['name']))
    if len(res['name']) != 0:
        session["name"] = res['name']
        session["roll"] = request.form['roll']
        payload = {'roll':session['roll']}
        preferences = requests.post(SERVER_URL+"/getprefs", data=payload).json()
        try:
            preferences = preferences[0]['prefs'].split()
            print(preferences)
            prefs = preferences
            generate_usertable()
        except:
            prefs = ['-1']*9
        return redirect(url_for('regular_page'))
    else:
        print("Elsed out!")
        return redirect(url_for("login"))


@app.route("/process_prefs", methods=["POST"])
def process_prefs():
    global errstring
    errstring = ""
    __import__("time").sleep(0.5)
    key = [i for i in request.form.keys()][0]
    idx = int(key[-1]) - 1
    prefs[idx] = request.form[key]
    print(prefs)
    global conflict
    conflict = dupli_locate(prefs)
    print(conflict)
    return redirect(url_for('courses'))

@app.route("/attendance")
def attendance_page():
    if "name" in session and session["name"] == 'Administrator':
        return render_template("attendance-page.html")
    else:
        return redirect(url_for('index'))

@app.route("/generate_attendance", methods=['POST'])
def generate_attendance():
    global attendance_for
    attendance_for = request.form['sub']
    report = requests.post(SERVER_URL + "/genattendance", data={'sub':request.form['sub']}).json()
    attable = AttTable(report)
    return render_template("attendance-page.html", report=attable, subname=request.form['sub'])

@app.route("/attdownload")
def attdownload():
    attable = requests.post(SERVER_URL + "/genattendance", data={'sub': attendance_for}).json()
    keys = attable[0].keys()
    csv = ''
    for key in keys:
        csv+=key + ','
    csv = csv[:-1]
    csv+='\n'
    for i in range(len(attable)):
        val = attable[i].values()
        for v in val:
            csv+=v + ','
        csv = csv[:-1]
        csv +='\n'
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename="+attendance_for.replace(' ','_')+"_Attendance.csv"}
    )

@app.route("/statsdownload")
def statsdownload():
    statstable = requests.get(SERVER_URL + "/getstats").json()

    keys = statstable[0].keys()
    csv = ''
    for key in keys:
        csv += key + ','
    csv = csv[:-1]
    csv += '\n'
    for i in range(len(statstable)):
        val = statstable[i].values()
        for v in val:
            csv += str(v) + ','
        csv = csv[:-1]
        csv += '\n'
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=StudentStats.csv"}
    )


@app.route("/stats_page")
def stats_page():
    if "name" in session and session["name"] == 'Administrator':
        stats = requests.get(SERVER_URL + "/getstats").json()
        print(stats)
        stats_table = StatsTable(stats)
        return render_template("stats-page.html", table=stats_table)
    else:
        return redirect(url_for('index'))

@app.route("/add_course")
def add_course():
    if "name" in session and session["name"] == 'Administrator':
        return render_template("add-course.html")
    else:
        return redirect(url_for('index'))

@app.route("/add_course_proc", methods=["POST"])
def add_course_proc():
    return render_template("submitted.html",cname=request.form['cname'])


@app.route("/assignpref")
def assignpref():
    global console_err
    payload = {'roll': request.args.get('roll')}
    check = requests.post(SERVER_URL+"/getprefassigned", data={'roll': payload['roll']}).json()[0]['exists']
    if check != 1:
        preferences = requests.post(SERVER_URL+"/getprefs", data=payload).json()
        try:
            preferences = preferences[0]['prefs'].split()
            i = 1
            idx = preferences.index(str(i))
            seats_fetch()
            print(idx,seats_left)
            while seats_left[idx] == 0:
                i+=1
                idx = preferences.index(str(i))

            print("assigning",payload['roll'],"preference",cname[idx])
            payload = {'roll':payload['roll'],'cname':cname[idx]}
            requests.post(SERVER_URL+"/assignpref", data=payload)
            seats_fetch()
            pref_assign_fetch()
        except:
            print("Nobody gave prefs!")
        console_err = ""
        return redirect(url_for('admin_console'))
    else:
        global consoletable
        console_err="Preference Already assigned for that student!"
        return redirect(url_for('admin_console'))


class ConsoleTable(Table):
    roll = Col('Roll No')
    assign = LinkCol('Auto Assign Preference', 'assignpref', url_kwargs=dict(roll='roll'))

@app.route("/admin_console")
def admin_console():
    global consoletable,console_err
    res = requests.get(SERVER_URL+"/getallprefs").json()
    vals = []
    for row in res:
        vals.append(list(row.values()))
    roll = [row[0] for row in vals]
    data = []
    for row in roll:
        d = {'roll': row}
        data.append(d)
    print(data)
    i=0
    consoletable = ConsoleTable(data,no_items="Nobody has filled prefs yet!")
    return render_template("admin-console.html", table=consoletable, console_err=console_err)



@app.route("/commit_prefs")
def commit_prefs():
    if 'name' in session:
        check = requests.post(SERVER_URL+"/getprefsubmitted", data={'roll': session["roll"]}).json()[0][
            'exists']
        if check == 0:
            global errstring
            if sum(conflict) == 0:
                string = ''
                flag = 0
                for i in prefs:
                    if i == '-1':
                        flag = 1
                        break
                    string += i
                    string += ' '
                if flag == 1:
                    errstring = "Please select preferences for all electives"
                    print(errstring)
                else:
                    roll = session["roll"]
                    payload = {'srno':roll, 'prefs':string}
                    requests.post(SERVER_URL+"/commit_prefs", data=payload)
                    generate_usertable()
                    errstring = ""
            else:
                errstring = "Please resolve all conflicts before committing preferences!"
                print(errstring)
        else:
            errstring = "You have already committed your preferences!"

    return redirect(url_for('courses'))


if __name__ == "__main__":
    app.run(debug=True)
