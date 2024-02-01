from flask import Flask, request
from flask import jsonify
import json
import uuid
import logging
import mysql.connector
from datetime import datetime

app = Flask(__name__)
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="031201",
  database ="9mclc",
  port=3306
)

def queryResultToList(cursor):
    colums = [desc[0] for desc in cursor.description]
    result = [dict(zip(colums, row)) for row in cursor.fetchall()]

    return result

@app.route('/showUser', methods = ['GET'])
def showAllUser():
    '''
    Get all registered user

    Params:
        - There is no parameters accepted in this endpoint
    
    Example Execute:
        - http://192.168.0.118:5000/showUser

    Example Return:
        {
            "response": [
                {
                    "BirthDate": "Sat, 16 Dec 2023 00:00:00 GMT",
                    "ChineseName": "康",
                    "EnglishName": "Bernard Lim",
                    "UUID": "e8581a7b-9b77-48fa-abab-3c1bd1a55395"
                }
            ],
            "statusCode": 200
        }
    '''
    statusCode = 200

    cursor = mydb.cursor()
    cursor.execute('SELECT * FROM userinfo order by EnglishName')
    result = queryResultToList(cursor)
    returnMsg = {"statusCode":statusCode, "response": result}

    return jsonify(returnMsg), statusCode

@app.route('/validateRegistration', methods =['GET'])
def ValidateRegistration():
    '''
    Checks if input user is new user by details

    Params:
        - englishName
        - chineseName
        - birthDate
    
    Example Execute:
        - http://192.168.0.118:5000/validateRegistration?englishName=Bernard Lim&chineseName=康&birthDate=2023-12-16

    Example Return:
        {
            "isExist": True/False,
            "statusCode": 200
        }
    '''
    statusCode = 200
    args = request.args

    engName = args.get("englishName")
    chiName = args.get("chineseName")
    dob = args.get("birthDate")
    if engName and chiName and dob:
        cursor = mydb.cursor()

        cursor.execute(f"SELECT * FROM userinfo where EnglishName = '{engName}' and ChineseName = '{chiName}' and BirthDate = '{dob}'; ")
        result = queryResultToList(cursor)
        if result:
            returnMsg = {"statusCode":statusCode, "isExist":True}
        else:
            returnMsg = {"statusCode":statusCode, "isExist":False}
    else:
        statusCode = 401
        returnMsg = {"statusCode": statusCode, 'isExist': 'Error', 'message': 'Unauthorized'}

    return jsonify(returnMsg), statusCode

@app.route('/validateUser', methods =['GET'])
def ValidateUser():
    '''
    Checks if input user is new user by UUID

    Params:
        - UUID
    
    Example Execute:
        - http://192.168.0.118:5000/validateUser?UUID=e8581a7b-9b77-48fa-abab-3c1bd1a55395

    Example Return:
        {
            "isExist": True/False,
            "result": [
                {
                    "BirthDate": "Sat, 16 Dec 2023 00:00:00 GMT",
                    "ChineseName": "康",
                    "EnglishName": "Bernard Lim",
                    "UUID": "e8581a7b-9b77-48fa-abab-3c1bd1a55395"
                }
            ]
            "statusCode": 200
        }
    '''
    statusCode = 200
    args = request.args

    User_UUID = args.get("UUID")
    if User_UUID:
        cursor = mydb.cursor()

        cursor.execute(f"SELECT * FROM userinfo where UUID = '{User_UUID}'; ")
        result = queryResultToList(cursor)
        if result:
            returnMsg = {"statusCode":statusCode, "isExist":True, "result":result}
        else:
            returnMsg = {"statusCode":statusCode, "isExist":False}
    else:
        statusCode = 401
        returnMsg = {"statusCode": statusCode, "isExist": "Error", "message": "Unauthorized"}

    return jsonify(returnMsg), statusCode

@app.route('/validateAttendance', methods =['GET'])
def validateAttendance():
    '''
    Checks if input user is already marked attendance

    Params:
        - UUID
    
    Example Execute:
        - http://192.168.0.118:5000/validateAttendance?UUID=e8581a7b-9b77-48fa-abab-3c1bd1a55395

    Example Return:
        {
            "isExist": True/False,
            "statusCode": 200
        }
    '''
    statusCode = 200
    args = request.args

    User_UUID = args.get("UUID")
    Date = datetime.now().strftime("%Y-%m-%d")

    if User_UUID:
        cursor = mydb.cursor()

        cursor.execute(f"SELECT * FROM attendance where UUID = '{User_UUID}' and DateofAttendance = '{Date}'; ")

        result = queryResultToList(cursor)
        if result:
            returnMsg = {"statusCode":statusCode, "isExist":True, "result": result}
        else:
            returnMsg = {"statusCode":statusCode, "isExist":False}
    else:
        statusCode = 401
        returnMsg = {"statusCode": statusCode, "isExist": "Error", "message": "Unauthorized"}

    return jsonify(returnMsg), statusCode

@app.route('/register', methods = ['POST'])
def RegisterUser():
    '''
    Registers a new user to the system

    Body:
        - englishName
        - chineseName
        - birthDate
    
    Example Execute:
        - http://192.168.0.118:5000/register
    
        Body:
            {
                "englishName": "Bernard Lim",
                "chineseName": "康",
                "birthDate": "2003-12-01"
            }

    Example Return:
        {
            "status": 'Success',
            "UUID": "e8581a7b-9b77-48fa-abab-3c1bd1a55395",
            "statusCode": 200
        }
    '''
    statusCode = 200
    body = json.loads(request.data)

    englishName = body.get("englishName")
    chineseName = body.get("chineseName")
    birthDate = body.get("birthDate")
    UserID = str(uuid.uuid4())
    if englishName and chineseName and birthDate:

        cursor = mydb.cursor()
        cursor.execute(f"INSERT INTO userinfo (UUID, EnglishName, ChineseName, BirthDate) VALUES ('{UserID}', '{englishName}', '{chineseName}', '{birthDate}');")
        mydb.commit()
        returnMsg = {"statusCode":statusCode, "isSuccess":True, "UUID":UserID}

        logging.basicConfig(filename=f'.\\Logs\\API-{datetime.now().strftime("%m-%d-%Y")}.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info(f'{englishName} is now registered to the System')
    
    else:
        statusCode = 401
        returnMsg = {"statusCode":statusCode, "isSuccess":False, "message":'Unauthorized'}
    return jsonify(returnMsg), statusCode

@app.route('/attendance', methods = ['POST'])
def markAttendance():
    '''
    Registers the attendance to the system

    Body:
        - UUID
        - englishName
        - chineseName
        - birthDate
    
    Example Execute:
        - http://192.168.0.118:5000/attendance
    
        Body:
            {
                "UUID": "e8581a7b-9b77-48fa-abab-3c1bd1a55395"
                "englishName": "Bernard Lim",
                "chineseName": "康",
                "birthDate": "2003-12-01"
            }

    Example Return:
        {
            "isSuccess": True,
            "statusCode": 200
        }
    '''
    statusCode = 200
    body = json.loads(request.data)

    User_UUID = body.get("UUID")
    engName = body.get("englishName")
    chiName = body.get("chineseName")
    dob = body.get("birthDate")
    
    if User_UUID and engName and chiName and dob:
        cursor = mydb.cursor()
        cursor.execute(f"INSERT INTO attendance (UUID, EnglishName, ChineseName, BirthDate, DateOfAttendance, TimeOfAttendance) VALUES ('{User_UUID}', '{engName}', '{chiName}', '{dob}', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);")
        mydb.commit()
        returnMsg = {"statusCode":statusCode, "isSuccess":True}
    else:
        statusCode = 401
        returnMsg = {"statusCode":statusCode, "isSuccess":False, 'Message': "Unauthorized"}
    return jsonify(returnMsg), statusCode

@app.route('/showAllAttendance', methods = ['GET'])
def showAllAttendance():
    '''
    show all attendance for the current date

    Params:
        - There is no parameters accepted in this endpoint
    
    Example Execute:
        - http://192.168.0.118:5000/showAllAttendance

    Example Return:
        {
            "isSuccess": True,
            "result":[
                {
                    "BirthDate": "Fri, 01 Dec 2023 00:00:00 GMT",
                    "ChineseName": "康",
                    "DateOfAttendance": "Mon, 18 Dec 2023 00:00:00 GMT",
                    "EnglishName": "Bernard Lim",
                    "TimeOfAttendance": "Mon, 18 Dec 2023 08:33:05 GMT",
                    "UUID": "e8581a7b-9b77-48fa-abab-3c1bd1a55395"
                }
            ],
            "statusCode": 200
        }
    '''
    statusCode = 200

    DateOfAttendance = datetime.now().strftime("%Y-%m-%d")

    cursor = mydb.cursor()
    cursor.execute(f"SELECT * FROM attendance where DateOfAttendance = '{DateOfAttendance}'; ")
    result = queryResultToList(cursor)

    returnMsg = {"statusCode":statusCode, "isSuccess":True, 'result': result}
    return jsonify(returnMsg), statusCode

@app.route('/unmarkAttendance', methods = ['DELETE'])
def unmarkAttendance():
    '''
    Remove an attendance for the current date

    Body:
        - UUID
    
    Example Execute:
        - http://192.168.0.118:5000/unmarkattendance
        Body:
        {
            "UUID":"e8581a7b-9b77-48fa-abab-3c1bd1a55395"
        }

    Example Return:
        {
            "isSuccess": True,
            "statusCode": 200
        }
    '''
    statusCode = 200
    body = json.loads(request.data)

    User_UUID = body.get("UUID")
    if User_UUID:
        cursor = mydb.cursor()
        cursor.execute(f"DELETE FROM attendance where UUID = '{User_UUID}' and DateOfAttendance = CURRENT_DATE(); ")
        mydb.commit()
        returnMsg = {"statusCode":statusCode, "isSuccess":True}
    else:
        statusCode = 401
        returnMsg = {"statusCode":statusCode, "isSuccess":False, "message": "Unauthorized"}

    return jsonify(returnMsg), statusCode

@app.route('/removeUser', methods = ['DELETE'])
def removeUser():
    '''
    Remove an attendance for the current date

    Body:
        - UUID
    
    Example Execute:
        - http://192.168.0.118:5000/removeUser
        Body:
        {
            "UUID":"e8581a7b-9b77-48fa-abab-3c1bd1a55395"
        }

    Example Return:
        {
            "isSuccess": True,
            "statusCode": 200
        }
    '''
    statusCode = 200
    body = json.loads(request.data)

    User_UUID = body.get("UUID")
    if User_UUID:
        cursor = mydb.cursor()
        cursor.execute(f"DELETE FROM userinfo where UUID = '{User_UUID}'")
        mydb.commit()
        returnMsg = {"statusCode":statusCode, "isSuccess":True}
    else:
        statusCode = 401
        returnMsg = {"statusCode":statusCode, "isSuccess":False, "message": "Unauthorized"}

    return jsonify(returnMsg), statusCode

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)