import mysql.connector
import cx_Oracle
import base64

db = mysql.connector.connect(
    host='172.18.20.42',
    database='intrasm',
    user='it_sales',
    password='S4mDBProjectNginx!'
)
cursor = db.cursor()

dbo = cx_Oracle.connect("ADMINDWS/test1ng@172.18.11.18:1521/POWERBI")
cursor = dbo.cursor()
print("Succesfully connect")

def base64_decode(data):
  base64_string = data
  base64_bytes = base64_string.encode("ascii")

  sample_string_bytes = base64.b64decode(base64_bytes)
  sample_string = sample_string_bytes.decode("ascii")
  return sample_string