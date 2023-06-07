from flask import Flask, render_template, url_for, session,request, redirect
from datetime import timedelta
import hashlib
import requests
import airtable
from pydantic import BaseModel
import json
from datetime import datetime as d

sessionActive=""
BASE_ID = "appTZGqtLSClGCdCo"
TABLE_NAME = "notesFromTeacher"
API_KEY = "keyxJJCgmuon6ezwN"

app= Flask(__name__)


endpoint = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"

header = {
        "Authorization":f"Bearer {API_KEY}",
        "Content-Type":"application/json"
}

def delete_records(records):
    """Delete the records."""
    url = f"{AIRTABLE_URL}/golf-scores"
    headers = {
        'Authorization': f'Bearer {AIRTABLE_TOKEN}',
        'Content-Type': 'application/json'
    }

    params = {
        "records[]": records
    }

    response = requests.request("DELETE", url, headers=headers, params=params)

    return response

def get_from_airtable_field(table_name,field):
    endpoint = f"https://api.airtable.com/v0/{BASE_ID}/{table_name}"
    response = requests.get(endpoint, headers=header)
    data = response.json()
    
    count = 0
    subject_names = []

    for d in data['records']:
        name = data['records'][count]['fields'][field]
        
        count = count + 1
        subject_names.append(name)

    
    
    return subject_names

# class teacherMaster(BaseModel):
#     teacherMasterKey : int
#     teacherName : str
#     gradeData : str

# class RecordsItems(BaseModel):
#     id:str
#     fields: teacherMaster

# class ReturnJson(BaseModel):
#     records: list[RecordsItems] = [] 

def get_from_airtable_record(table_name,field_name,field_value,field_name2,field_value2):
    
    endpoint = f"https://api.airtable.com/v0/{BASE_ID}/{table_name}?filterByFormula=AND({field_name2}='{field_value2}',{field_name}='{field_value}')"
    #https://api.airtable.com/v0/appTZGqtLSClGCdCo/subjectMaster
    response = requests.get(endpoint, headers=header)
    data = response.json()
    # returnJson : ReturnJson = ReturnJson(**data)        
    # print("Result New : " , returnJson.records[0].fields)    
    return data['records'][0]['fields']


def add_to_db(table_name,dict_fields):    
    endpoint = f"https://api.airtable.com/v0/{BASE_ID}/{table_name}"
    new_data = {
        "records": [
            {
                "fields": dict_fields
            },
        ]
    }
    r = requests.post(endpoint,json=new_data,headers=header)
   

app= Flask(__name__)

app.secret_key = 'yo'
app.permanent_session_lifetime = timedelta(minutes=10)

@app.route('/home')

def single():
    return render_template('home.html')

@app.route('/studentLogin',methods=['POST','GET'])
def studentLogin():
    session.permanent = True
    
    grade = request.form['grade']
    division = request.form['division']
    name = request.form['name']
    session["student"] = {'name':name,'grade':grade,'division':division}
    info = session['student']
    return redirect(url_for('student'))
    # info = session["user"]
    # u_name = info['name']
    # return f'Name : { u_name }'
    
@app.route('/student',methods=['POST','GET'])
def student():
    if 'student' in session:
        info = session["student"]
        return render_template('student.html',studentData=info)
    else:
        return redirect(url_for('single'))

@app.route('/teacher')
def teacher():
    return render_template('teacher_login.html')

app.secret_key = 'shaanlashkari9898780706'
app.permanent_session_lifetime = timedelta(minutes=10)


@app.route('/teacherSubmitForm',methods=['POST'])

def teacherSubmitForm():
    session.permanent = True
    name = request.form['uid']
    pwd = request.form['password']
    
    pwd_encode = pwd.encode()
    pwd_hash = hashlib.sha256(pwd_encode)
    pwdFinal = pwd_hash.hexdigest()
    print(pwdFinal)
    
    try:
        airtable_data = get_from_airtable_record('teacherMaster','teacherName',name,'password',pwdFinal)
        session['teacherDashboard'] = airtable_data
        print(session['teacherDashboard'])
        
        return redirect(url_for('teacherDb'))
        
    except:
        print('doesnt exist')
        return render_template('teacher_login.html',message='Sorry! Username or Password is wrong!')
    
        
    
    # if name in teacherName:
    #     if pwdFinal in teacherPassword:
    #         grade = teacherGrade
    #         session["teacherDashboard"] = {'name':name,'password':pwdFinal,'grade':grade}
    #         return redirect(url_for('teacherDb'))
    #     else:
    #         return render_template('teacher_login.html',message='Sorry! Username or \
    #             Password is wrong!')

    # else:
    #     return render_template('teacher_login.html',message='Sorry! Username or Password \
    #         is wrong!')
        
        
    
    

@app.route('/teacher-dashboard')
def teacherDb():
    
    if 'teacherDashboard' in session:
        info = session["teacherDashboard"]
       
        return render_template('teacher_dashboard.html',teacherInfo=info)
    else:
        return redirect(url_for('single'))
        
@app.route('/timetable')
def timetable():

    if 'teacherDashboard' in session:
        option = get_from_airtable_record('teacherMaster','teacherMasterKey','15','gradeData','7D')
        # key = get_from_airtable_record('subjectMaster','subjectKey')
        subjects = get_from_airtable_field('subjectMaster','subject_name') 
        return render_template('timetable.html',credentials=option,subject = subjects)
    else:
        return redirect(url_for('single'))
   
@app.route('/submitTimetable',methods=['post'])
def submitTimetable():
    information = session['teacherDashboard']
    grade = information['gradeData']
    name = information['teacherName']

    
    for i in range(1,13):
        i = str(i)
        tue = request.form['tuesday-period_'+i]
        mon = request.form['monday-period_'+i]
        
        print(tue)
        wed = request.form['wednesday-period_'+i]
        thu = request.form['thursday-period_'+i]
        fri = request.form['friday-period_'+i]
        sat = request.form['saturday-period_'+i]
        data_entry= {
            'classDivision':grade,
            'period':int(i),
            'monday':mon,
            'tuesday':tue,
            'wednesday':wed,
            'thursday':thu,
            'friday':fri,
            'saturday':sat,
        }
        print(data_entry)
        add_to_db('timeTable',data_entry)
        i = int(i)
    return redirect(url_for('timetable'))  

@app.route('/myBagTeacher')
def myBagTeacher():
    if 'teacherDashboard' in session:
        option = get_from_airtable_record('teacherMaster','teacherMasterKey','15','gradeData','7D')
        # key = get_from_airtable_record('subjectMaster','subjectKey')
        subjects = get_from_airtable_field('subjectMaster','subject_name') 
        day = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
        return render_template('mybagteacher.html',credentials=option,subject = subjects,days=day )
    else:
        return redirect(url_for('single'))
     
# @app.route('/sendNotes',methods=['POST'])
# def sendNotes():
#     note=request.form['']
    
# @app.route('/timetable')
# def timetable():

if __name__ == '__main__':
    app.run(debug=True)