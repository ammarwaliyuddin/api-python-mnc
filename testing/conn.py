import mysql.connector
import cx_Oracle
import pandas as pd


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

sql_adv = """SELECT a.nama_adv FROM db_m_advertiser a
    WHERE a.id_adv =3718"""
adv = pd.read_sql(sql_adv,db)
ora_periode = """SELECT DISTINCT to_char(a.AIR_DATE,'MONTH YYYY') PERIOD FROM DB_GEN21_CLEAN_DETAIL a
where to_char(a.AIR_DATE,'YYYY-MM') = '2021-11'"""
periode = pd.read_sql(ora_periode,dbo)

print (adv)
print (periode)
