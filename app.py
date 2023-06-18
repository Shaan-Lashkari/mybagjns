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

def get_from_airtable_record1(table_name,field_name,field_value,field_sort,order):
    
    endpoint = f"https://api.airtable.com/v0/{BASE_ID}/{table_name}?filterByFormula=AND({field_name}='{field_value}')&sort%5B0%5D%5Bfield%5D={field_sort}&sort%5B0%5D%5Bdirection%5D={order}"
    #https://api.airtable.com/v0/appTZGqtLSClGCdCo/subjectMaster
    response = requests.get(endpoint, headers=header)
    print(response)
    data = response.json()
    # returnJson : ReturnJson = ReturnJson(**data)        
    # print("Result New : " , returnJson.records[0].fields)    
    return data['records']





app= Flask(__name__)

app.secret_key = 'yo'
app.permanent_session_lifetime = timedelta(minutes=10)

@app.route('/home')

def single():
    return render_template('home.html')

@app.route('/student',methods=['POST','GET'])
def studentLogin():
    session.permanent = True
    
    grade = request.form['grade']
    division = request.form['division']
    name = request.form['name']
    session["student"] = {'name':name,'grade':grade,'division':division}
    info = session['student']
    return redirect(url_for('studentDb'))
    # info = session["user"]
    # u_name = info['name']
    # return f'Name : { u_name }'
    
@app.route('/studentDb',methods=['POST','GET'])
def studentDb():
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
        teacher_data = session['teacherDashboard']
        grade = teacher_data['gradeData']
        # key = get_from_airtable_record('subjectMaster','subjectKey')
        subjects = get_from_airtable_field('subjectMaster','subject_name') 
        return render_template('timetable.html',credentials=grade,subject = subjects)
    else:
        return redirect(url_for('single'))
   
@app.route('/submitTimetable',methods=['post'])
def submitTimetable():
    if 'teacherDashboard' in session:
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
    else:
        return redirect(url_for('single'))

@app.route('/myBagTeacher')
def myBagTeacher():
    if 'teacherDashboard' in session:
        option = get_from_airtable_record('teacherMaster','teacherMasterKey','15','gradeData','7D')
        # key = get_from_airtable_record('subjectMaster','subjectKey')
        subjects = get_from_airtable_field('subjectMaster','subject_name') 
        print(subjects)
        day = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
        count = 0
        try:
            informationTimeTable = session['timetableUpload']
            print(informationTimeTable[0],'asasasasa')
            # data = []
            # for d in informationTimeTable:
            #     count=count+1
            #     print(d)
            #     string_dict = {int(key): value for key, value in d.items()}
                
            #     data.append(string_dict)
            
            # print('\n \n \n Data : ')
            # print(data)
            
            # merged_dict = {**dict1, **dict2, **dict3}
            # print(merged_dict)
             

            return render_template('mybagteacher.html',credentials=option,subject = subjects,days=day,UploadTimeTable=informationTimeTable[0],day_select=informationTimeTable[1] )
        except:
            print('sorry')
            data = [{'2': '-'}, {'5': '-'}, {'4': '-'}, {'7': '-'}, {'8': '-'}, {'3': '-'}, {'1': '-'}, {'6': '-'}]
            return render_template('mybagteacher.html',credentials=option,subject = subjects,days=day,UploadTimeTable=data)
    else:
        return redirect(url_for('single'))


@app.route('/submitDay',methods=['POST','GET'])
def submitDay():
    if 'teacherDashboard' in session:
        day = request.form['dayselect'].lower()
        date = request.form['dateselect'].lower()
        
        # print(day)
        teacher = session['teacherDashboard']
        grade = teacher['gradeData']
        
        horizontal_data = []

        data = get_from_airtable_record1('timetable','classDivision',grade,'period','asc')
        keys = []
        values = []
        count = -1
        for d in data:
            count = count + 1
            value = data[count]['fields']
            
            if value['classDivision'] == grade:
                key_dict = value['period']
                value_dict = value[f'{day}']
                key_value_pair = {int(key_dict):value_dict}
                
                # print(key_value_pair)
                horizontal_data.append(key_value_pair)
                keys.append(key_dict)
                values.append(value_dict)

        session['timetableUpload'] = [values,day,date]
        # print(horizontal_data)
        # print(json.dumps(horizontal_data, indent = 1))
        return redirect(url_for('myBagTeacher'))
    else:
        return redirect(url_for('single'))


@app.route('/submitMyBag',methods=['POST'])
def submitMyBag():
    if 'teacherDashboard' in session:
        textbook_dict = {}
        notebook_dict = {}
        workbook_dict = {}
        classDivision = session['teacherDashboard']['gradeData']
        subjects = []
        for i in range(0,12):
            subject = request.form[f'period_{i}']
            subjects.append(subject)
            pass    
        
        day = session['timetableUpload'][1]
        date = session['timetableUpload'][2]
        textbook = request.form.getlist('textbook-period')
    
        notebook = request.form.getlist('notebook-period')
    
        workbook = request.form.getlist('workbook-period')
    
        for count in range(0,12):
            #    textbook
            if f'textbook-period_{count}' in textbook:
                textbook_dict[f'textbook-period_{count}'] = True
            else:
                textbook_dict[f'textbook-period_{count}'] = False
            #    notebook
            if f'notebook-period_{count}' in notebook:
                notebook_dict[f'notebook-period_{count}'] = True
            else:
                notebook_dict[f'notebook-period_{count}'] = False
            #   workbook
            if f'workbook-period_{count}' in workbook:
                workbook_dict[f'workbook-period_{count}'] = True
            else:
                workbook_dict[f'workbook-period_{count}'] = False
        
            dict_fields = {
                'classDivision':classDivision,
                'subjectName':subjects[count],
                'day':day,
                'date':date,
                'period':count+1,
                'textbook':textbook_dict[f'textbook-period_{count}'],
                'notebook':notebook_dict[f'notebook-period_{count}'],
                'workbook':workbook_dict[f'workbook-period_{count}'],
                
            }
            add_to_db('myBag',dict_fields)
            
        print(textbook_dict)
        print(notebook_dict)
        print(workbook_dict)
        return redirect(url_for('teacherDb'))
    else:
        return redirect(url_for('single'))

@app.route('/timetableStudent')
def timetableStudent():
    if 'student' in session:
        grade = session['student']['grade']
        division = session['student']['division']
        try:
            timetable_retrieved = get_from_airtable_record1('timeTable','classDivision',grade+division,'period','asc')
            print(timetable_retrieved[1]['fields'])
            
            return render_template('timetable_student.html',timetableData=timetable_retrieved)
        except:
            return redirect(url_for('studentDb'))
    else:
        return redirect(url_for('single'))
    
@app.route('/studentMyBag')
def studentMyBag():

    
    if 'student' in session:
        grade = session['student']['grade']
        division = session['student']['division']
        try:
            timetable_retrieved = get_from_airtable_record1('myBag','classDivision',grade+division,'period','asc')
            
            print(timetable_retrieved)
            
            return render_template('mybagstudent.html',myBagData=timetable_retrieved,credentials='',subject ='',day_select='',UploadTimeTable='')
        except:
            return redirect(url_for('studentDb'))
    else:
        return redirect(url_for('single'))
# @app.route('/sendNotes',methods=['POST'])
# def sendNotes():
#     note=request.form['']
    
# @app.route('/timetable')
# def timetable():

if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')