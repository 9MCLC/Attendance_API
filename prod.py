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

@app.route('/getUser', methods = ['GET'])
def showUser():
    '''
    Get Users

    Params:
        - UUID
        - name
        - phoneNumber
    * These Params are optional, if not given, all users will be returned
    
    Example Execute:
        - http://192.168.0.119:5001/getUser?UUID=e8581a7b-9b77-48fa-abab-3c1bd1a55395

    Example Return:
        {
            "users": [
                {
                    "Name": "Bernard Lim",
                    "UUID": "e8581a7b-9b77-48fa-abab-3c1bd1a55395",
                    "PhoneNumber": "011-10869155"
                }
            ],
            "rowCount": 1,
            "statusCode": 200
        }
    '''
    statusCode = 200
    args = request.args

    uuid_value = args.get("UUID", None)
    name = args.get("name", None)
    phNo = args.get("phoneNumber", None)

    cursor = mydb.cursor()

    # Use placeholders in the SQL query and pass values as parameters
    query = ('SELECT * FROM userinfo WHERE (%s IS NULL OR UUID = %s) AND (%s IS NULL OR Name = %s) AND (%s IS NULL OR PhoneNumber = %s)')

    # Execute the query with parameters
    cursor.execute(query, (uuid_value, uuid_value, name, name, phNo, phNo))

    result = queryResultToList(cursor)
    returnMsg = {"statusCode": statusCode, "users": result, "rowCount": len(result)}

    return jsonify(returnMsg), statusCode

@app.route('/addUser', methods = ['POST'])
def addUser():
    '''
    Add New Users

    Params:
        - name
        - phoneNumber
    * These Params are required, if not given, will return error 401
    * Will return UUID as response
    
    Example Execute:
        - http://192.168.0.119:5001/addUser

    body:
        {
            "name": "Yew Hong Yin",
            "phoneNumber": "011-10869155"
        }

    Example Return:
        {
            "UUID": "e8581a7b-9b77-48fa-abab-3c1bd1a55395",
            "statusCode": 200
        }
    '''
    statusCode = 200
    args = json.loads(request.data)

    name = args.get("name", None)
    phNo = args.get("phoneNumber", None)
    uuid_value = str(uuid.uuid4())

    cursor = mydb.cursor()
    # Use placeholders in the SQL query and pass values as parameters
    query = ('INSERT INTO userinfo (UUID, Name, PhoneNumber) VALUES (%s, %s, %s)')

    # Execute the query with parameters
    if all([name, uuid_value, phNo]):
        cursor.execute(query, (uuid_value, name, phNo))
        if cursor.rowcount == 1:
            mydb.commit()
            statusCode = 200
            returnMsg = {"statusCode": statusCode, "UUID": uuid_value}
        else:
            mydb.rollback()
            statusCode = 422
            returnMsg = {"statusCode": statusCode, "message": "Error occured, please check the input format or contact admin."}
    else:
        statusCode = 401
        returnMsg = {"statusCode": statusCode, "message": "Unauthorized, please input all values"}

    return jsonify(returnMsg), statusCode

@app.route('/removeUser', methods = ['DELETE'])
def removeUser():
    '''
    Remove Existing Users

    Params:
        - UUID
    * These Params are required, if not given, will return error 401
    * Will return UUID as response
    
    Example Execute:
        - http://192.168.0.119:5001/removeUser

    body:
        {
            "UUID": "e8581a7b-9b77-48fa-abab-3c1bd1a55395"
        }

    Example Return:
        {
            "status": "Success",
            "statusCode": 200
        }
    '''
    statusCode = 200
    args = json.loads(request.data)

    uuid_value = args.get("UUID")

    cursor = mydb.cursor()

    # Use placeholders in the SQL query and pass values as parameters
    query = ('DELETE FROM userinfo WHERE UUID = %s')

    if uuid_value:
    # Execute the query with parameters
        cursor.execute(query, ([uuid_value]))
        if cursor.rowcount == 1:
            mydb.commit()
            statusCode = 200
            returnMsg = {"statusCode": statusCode, "Status": "Success"}
        else:
            mydb.rollback()
            statusCode = 404
            returnMsg = {"statusCode": statusCode, "message": "uuid is not a valid user"}
    else:
        statusCode = 401
        returnMsg = {"statusCode": statusCode, "message": "Unauthorized, check for all input value"}

    return jsonify(returnMsg), statusCode

@app.route('/getAttendance', methods = ['GET'])
def showAttendance():
    '''
    Get Attendance

    Params:
        - UUID
        - name
        - toa
    * These Params are optional, if not given, all attendance will be returned
    
    Example Execute:
        - http://192.168.0.119:5001/getUser?UUID=e8581a7b-9b77-48fa-abab-3c1bd1a55395&ToA=2023-02-01

    Example Return:
        {
            "result": [
                {
                    "Name": "Yew Hong Yin",
                    "UUID": "e8581a7b-9b77-48fa-abab-3c1bd1a55395",
                    "ToA": "2022-03-01 Time"
                }
            ],
            "rowCount": 1,
            "statusCode": 200
        }
    '''
    statusCode = 200
    args = request.args

    uuid_value = args.get("UUID", None)
    name = args.get("name", None)
    ToA = args.get("toa", datetime.now().date())

    cursor = mydb.cursor()

    # Use placeholders in the SQL query and pass values as parameters
    query = ('SELECT * FROM attendance WHERE (%s IS NULL OR UUID = %s) AND (%s IS NULL OR Name = %s) AND (%s IS NULL OR TimeOfAttendance > %s)')

    # Execute the query with parameters
    cursor.execute(query, (uuid_value, uuid_value, name, name, ToA, ToA))

    result = queryResultToList(cursor)
    returnMsg = {"statusCode": statusCode, "result": result, "rowCount": len(result)}

    return jsonify(returnMsg), statusCode

@app.route('/addAttendance', methods = ['POST'])
def addAttendance():
    '''
    Add New Attendance

    Params:
        - UUID
        - name
        - toa *Optional
    * Other Params are required, if not given, will return error 401
    
    Example Execute:
        - http://192.168.0.119:5001/addAttendance

    body:
        {
            "name": "Yew Hong Yin",
            "UUID": "844574bc-7694-4835-8b00-f52f6a839c83",
            "toa": "2003-12-01"
        }

    Example Return:
        {
            "status": "Success",
            "statusCode": 200
        }
    '''
    statusCode = 200
    args = json.loads(request.data)

    name = args.get("name", None)
    ToA = args.get("toa", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    uuid_value = args.get("UUID", None)

    cursor = mydb.cursor()
    # Use placeholders in the SQL query and pass values as parameters
    query = ('INSERT INTO attendance (UUID, Name, TimeOfAttendance) VALUES (%s, %s, %s)')

    # Execute the query with parameters
    if all([name, ToA, uuid_value]):
        cursor.execute(query, (uuid_value, name, ToA))
        if cursor.rowcount == 1:
            mydb.commit()
            statusCode = 200
            returnMsg = {"statusCode": statusCode, "status": "Success"}
        else:
            mydb.rollback()
            statusCode = 422
            returnMsg = {"statusCode": statusCode, "message": "Error occured, please check the input format or contact admin."}
    else:
        statusCode = 401
        returnMsg = {"statusCode": statusCode, "message": "Unauthorized, please input all values"}

    return jsonify(returnMsg), statusCode

@app.route('/removeAttendance', methods = ['DELETE'])
def removeAttendance():
    '''
    Remove Existing Attendance

    Params:
        - UUID
        - ToA *Optional
    * These Params are required, if not given, will return error 401
    
    Example Execute:
        - http://192.168.0.119:5001/removeAttendance

    body:
        {
            "UUID": "e8581a7b-9b77-48fa-abab-3c1bd1a55395",
            "ToA": "2023-12-01 Time"
        }

    Example Return:
        {
            "status": "Success",
            "statusCode": 200
        }
    '''
    statusCode = 200
    args = json.loads(request.data)

    uuid_value = args.get("UUID", None)
    ToA = args.get("toa", datetime.now().strftime("%Y-%m-%d 00:00:00"))

    cursor = mydb.cursor()

    # Use placeholders in the SQL query and pass values as parameters
    query = ('DELETE FROM attendance WHERE UUID = %s AND TimeOfAttendance > %s')

    if uuid_value:
    # Execute the query with parameters
        cursor.execute(query, (uuid_value, ToA))
        if cursor.rowcount == 1:
            mydb.commit()
            statusCode = 200
            returnMsg = {"statusCode": statusCode, "status": "Success"}
        else:
            mydb.rollback()
            statusCode = 404
            returnMsg = {"statusCode": statusCode, "message": "uuid is not a valid user"}
    else:
        statusCode = 401
        returnMsg = {"statusCode": statusCode, "message": "Unauthorized, check for all input value"}

    return jsonify(returnMsg), statusCode

@app.route('/getTableData', methods = ['GET'])
def getTableData():
    '''
    Get Table Data

    Params:
        - name
    * These Params are optional, if not given, all attendance will be returned
    
    Example Execute:
        - http://192.168.0.119:5001/getTableData

    Example Return:
        {
            "result": [
                {
                    "Name": "Yew Hong Yin",
                    "UUID": "e8581a7b-9b77-48fa-abab-3c1bd1a55395",
                    "ToA": "2022-03-01 Time"
                }
            ],
            "rowCount": 1,
            "statusCode": 200
        }
    '''
    statusCode = 200
    args = request.args
    name = args.get("name", None)
    likeName = None
    if name:
        likeName = name+'%'

    cursor = mydb.cursor()

    # Use placeholders in the SQL query and pass values as parameters
    query = ('SELECT * FROM user_attendance_view WHERE (%s IS NULL OR Name LIKE %s)')

    # Execute the query with parameters
    cursor.execute(query, (name, likeName))

    result = queryResultToList(cursor)
    returnMsg = {"statusCode": statusCode, "users": result, "rowCount": len(result)}

    return jsonify(returnMsg), statusCode

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)