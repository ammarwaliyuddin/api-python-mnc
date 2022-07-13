from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mysql.connector
import pandas as pd
import smtplib
from datetime import datetime
from datetime import timedelta

import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import rcParams
import numpy as np
sns.set_theme(style="ticks", color_codes=True)
from PIL import Image, ImageDraw, ImageFont

def this_week():
    v_date = datetime.today()
    v_date1 = (v_date + timedelta(days=-6))
    v_date2 = v_date
    if v_date1.strftime('%Y-%m') == v_date2.strftime('%Y-%m'):
        periode = (v_date1).strftime('%d')+" sd "+v_date2.strftime('%d-%b-%Y')
    elif v_date1.strftime('%Y') == v_date2.strftime('%Y'):
        periode = v_date1.strftime('%d-%b')+" sd "+v_date2.strftime('%d-%b-%Y')
    else:
        periode = v_date1.strftime('%d-%b-%Y')+" sd "+v_date2.strftime('%d-%b-%Y')
    return periode



# db = mysql.connector.connect(
#     host='localhost',
#     database='intrasm',
#     user='root',
#     password=''
# )
db = mysql.connector.connect(
    host='172.18.20.42',
    database='intrasm',
    user='it_sales',
    password='S4mDBProjectNginx!'
)
cursor = db.cursor()

# ambil data sales

# AND a.true_email='Y' AND a.POSITION IN ('AM', 'SGM', 'SM', 'GM', 'VP')
# , 'SGM', 'SM', 'GM', 'VP'
# AND a.true_email='Y' AND a.POSITION IN ('AM') and a.USER_ID='adam.khassaugi@mncgroup.com'
sql1 = """SELECT a.USER_ID, a.FIRST_NAME, a.USER_NAME, b.DEPT_NAME, a.POSITION FROM tbl_user a
        LEFT JOIN tbl_user_department b ON b.ID_DEPARTEMENT=a.ID_DEPARTEMENT
        WHERE a.ACTIVE=1 AND b.DEPT_NAME='SLS' AND a.ID_BU in (61, 10, 22)
        AND a.true_email='Y' AND a.POSITION IN ('SGM', 'SM', 'GM', 'VP') and a.USER_ID='allan.bhirawa@mncgroup.com'
        ORDER BY  a.POSITION, a.USER_NAME"""
dataSales = pd.read_sql(sql1, db)
# print(dataSales)


for index, rowSales in dataSales.iterrows():
    salesRecevier = rowSales['USER_NAME']
    emailsalesRecevier = rowSales['USER_ID']
    link_cam = "https://mncmediakit.com/cam2"
    fileChart = "files/"+this_week()+" "+emailsalesRecevier+".png"

    print('data dari sales:', salesRecevier)
    if rowSales['POSITION'] == 'SGM':
        param = "and a.head='"+emailsalesRecevier+"'"
    elif rowSales['POSITION'] == 'SM':
        param = "and a.manager='"+emailsalesRecevier+"'"
    elif rowSales['POSITION']== 'GM':
        param = "and a.gm='"+emailsalesRecevier+"'"
    elif rowSales['POSITION']== 'VP':
        param = "and a.vp='"+emailsalesRecevier+"'"
        # param = "and a.staff='adam.khassaugi@mncgroup.com'"

    # REPORT CAM AM
    sql21 = """SELECT c.USER_NAME, a.staff, c.POSITION,
            sum(if(b.pic_am IS NOT NULL AND (b.v_date BETWEEN DATE_ADD(CURDATE(), INTERVAL -6 DAY) AND CURDATE()), 1, 0)) jml_tasklist,
            sum(if(b.pic_am IS NOT NULL AND (b.v_date BETWEEN DATE_ADD(CURDATE(), INTERVAL -13 DAY) AND DATE_ADD(CURDATE(), INTERVAL -7 DAY)), 1, 0)) jml_tasklist2
            FROM tbl_user_structure a
            left JOIN cam b ON b.update_user=a.staff AND (b.v_date BETWEEN DATE_ADD(CURDATE(), INTERVAL -13 DAY) AND CURDATE())
            LEFT JOIN tbl_user c ON c.USER_ID=a.staff
            LEFT JOIN tbl_user_department d ON d.ID_DEPARTEMENT=c.ID_DEPARTEMENT
            WHERE c.ACTIVE=1 AND d.DEPT_NAME='SLS' AND c.true_email='Y' """ + param + """
            GROUP BY a.staff
            ORDER BY jml_tasklist, USER_NAME"""
    dataSales21 = pd.read_sql(sql21, db)
    user_update21 = dataSales21[dataSales21.jml_tasklist > 0]
    user_update_lastweek21 = dataSales21[dataSales21.jml_tasklist2 > 0]
    user_tidak_update21 = dataSales21[dataSales21.jml_tasklist == 0]
    jml_user21 = len(dataSales21)
    jml_tidak_update21 = len(user_tidak_update21)
    jml_user_update21 = len(user_update21)
    jml_user_update_lastweek21 = len(user_update_lastweek21)
    
    if jml_user21 == 0 or jml_user_update21 == 0 or jml_user_update_lastweek21 == 0:
        jml_user_update_per21 = 0
        jml_user_lastweek_per21 = 0
    else:
        jml_user_update_per21 = round(jml_user_update21 / jml_user21 * 100)
        jml_user_lastweek_per21 = round((jml_user_update21 / jml_user_update_lastweek21 - 1) * 100)

    tableSummary21 = '<table width="100%">'\
                    '<tr><td style="text-align: center; background-color:white; color: #2c4259; font-size: 40px; border: 1px solid #2c4259; width:25%">'+str(int(jml_user21))+'</td>'\
                    '<td style="text-align: center; background-color:white; color: #2c4259; font-size: 40px; border: 1px solid #2c4259; width:25%">'+str(int(jml_user_update21))+'</td>'\
                    '<td style="text-align: center; background-color:white; color: #2c4259; font-size: 40px; border: 1px solid #2c4259; width:25%">'+str(int(jml_user_update_per21))+'%</td>'\
                    '<td style="text-align: center; background-color:white; color: #2c4259; font-size: 40px; border: 1px solid #2c4259; width:25%">'+str(int(jml_user_lastweek_per21))+'%</td></tr>'\
                    '<tr><th style="text-align: center; background-color:#2c4259; color: white;">Jml Sales</th>'\
                    '<th style="text-align: center; background-color:#2c4259; color: white;">Jml Sales Update</th>'\
                    '<th style="text-align: center; background-color:#2c4259; color: white;">%Jml Sales Update</th>'\
                    '<th style="text-align: center; background-color:#2c4259; color: white;">%Last Week</th></tr>'\
                    '</table>'

    
    if len(user_tidak_update21.index)>0:
        cekUserTidakUpdate21 = 1
        try:
            tableUserTidakUpdate21 = '<table class="data-table textsmall bg-tbl" style="font-family: Arial, Helvetica, sans-serif; border-collapse: collapse; width: 100%">' \
                        '<thead class="bg-tbl-header text-tbl-header">' \
                        '<tr>' \
                        '<th style="text-align: center;background-color: #2c4259;color: white; border: 1px solid #ddd; padding: 12px 8px;">No.</th>' \
                        '<th style="text-align: center;background-color: #2c4259;color: white; border: 1px solid #ddd; padding: 12px 8px;">Sales</th>' \
                        '<th style="text-align: center;background-color: #2c4259;color: white; border: 1px solid #ddd; padding: 12px 8px;">Status</th>' \
                        '</tr>' \
                        '</thead>' \
                        '<tbody>'
            no = 1
            for index, row in user_tidak_update21.iterrows():
                if (no % 2) == 0:
                    tableUserTidakUpdate21 +='<tr style="background-color: #f2f2f2">'
                else:
                    tableUserTidakUpdate21 +='<tr>'
                tableUserTidakUpdate21 +='<td style="border: 1px solid #ddd; padding: 8px;">' + str(no) + '</td>' \
                            '<td style="border: 1px solid #ddd; padding: 8px;">' + row['USER_NAME'] + '</td>' \
                             '<td style="border: 1px solid #ddd; padding: 8px;">Tidak Update</td>' \
                             '</tr>'
                no += 1
            tableUserTidakUpdate21 += '</tbody></table>'
        except:
            print("Error di tabel User Tidak Update :", emailsalesRecevier)
    else:
        cekUserTidakUpdate21 = 0
        tableUserTidakUpdate21 ='<table class="data-table textsmall bg-tbl" style="font-family: Arial, Helvetica, sans-serif; border-collapse: collapse; width: 100%">' \
                    '<thead class="bg-tbl-header text-tbl-header">' \
                    '<tr>' \
                    '<th style="text-align: center;background-color: #2c4259;color: white; border: 1px solid #ddd; padding: 12px 8px;">' \
                    '<b>Congrats!!!</b> semua AM sudah update CAM</th>' \
                    '</tr>' \
                    '</thead></table>' \

    # REPORT CAM SGM
    sql22 = """SELECT c.USER_NAME, a.head, c.POSITION,
                sum(if(b.pic_am IS NOT NULL AND (b.v_date BETWEEN DATE_ADD(CURDATE(), INTERVAL -6 DAY) AND CURDATE()), 1, 0)) jml_tasklist,
                sum(if(b.pic_am IS NOT NULL AND (b.v_date BETWEEN DATE_ADD(CURDATE(), INTERVAL -13 DAY) AND DATE_ADD(CURDATE(), INTERVAL -7 DAY)), 1, 0)) jml_tasklist2
                from
                (SELECT distinct a.head, a.manager, a.gm, a.vp FROM tbl_user_structure a) AS a
                            left JOIN cam b ON b.update_user=a.head AND (b.v_date BETWEEN DATE_ADD(CURDATE(), INTERVAL -13 DAY) AND CURDATE())
                            LEFT JOIN tbl_user c ON c.USER_ID=a.head
                            LEFT JOIN tbl_user_department d ON d.ID_DEPARTEMENT=c.ID_DEPARTEMENT
                            WHERE c.ACTIVE=1 AND d.DEPT_NAME='SLS' AND c.true_email='Y' """ + param + """
                            GROUP BY a.head
                            ORDER BY jml_tasklist, USER_NAME"""
    dataSales22 = pd.read_sql(sql22, db)
    user_update22 = dataSales22[dataSales22.jml_tasklist > 0]
    user_update_lastweek22 = dataSales22[dataSales22.jml_tasklist2 > 0]
    user_tidak_update22 = dataSales22[dataSales22.jml_tasklist == 0]
    jml_user22 = len(dataSales22)
    jml_tidak_update22 = len(user_tidak_update22)
    jml_user_update22 = len(user_update22)
    jml_user_update_lastweek22 = len(user_update_lastweek22)
    
    if jml_user22 == 0 or jml_user_update22 == 0 or jml_user_update_lastweek22 == 0:
        jml_user_update_per22 = 0
        jml_user_lastweek_per22 = 0
    else:
        jml_user_update_per22 = round(jml_user_update22 / jml_user22 * 100)
        jml_user_lastweek_per22 = round((jml_user_update22 / jml_user_update_lastweek22 -1 ) * 100)

    tableSummary22 = '<table width="100%">'\
                    '<tr><td style="text-align: center; background-color:white; color: #2c4259; font-size: 40px; border: 1px solid #2c4259; width:25%">'+str(int(jml_user22))+'</td>'\
                    '<td style="text-align: center; background-color:white; color: #2c4259; font-size: 40px; border: 1px solid #2c4259; width:25%">'+str(int(jml_user_update22))+'</td>'\
                    '<td style="text-align: center; background-color:white; color: #2c4259; font-size: 40px; border: 1px solid #2c4259; width:25%">'+str(int(jml_user_update_per22))+'%</td>'\
                    '<td style="text-align: center; background-color:white; color: #2c4259; font-size: 40px; border: 1px solid #2c4259; width:25%">'+str(int(jml_user_lastweek_per22))+'%</td></tr>'\
                    '<tr><th style="text-align: center; background-color:#2c4259; color: white;">Jml Sales</th>'\
                    '<th style="text-align: center; background-color:#2c4259; color: white;">Jml Sales Update</th>'\
                    '<th style="text-align: center; background-color:#2c4259; color: white;">%Jml Sales Update</th>'\
                    '<th style="text-align: center; background-color:#2c4259; color: white;">%Last Week</th></tr>'\
                    '</table>'

    
    if len(user_tidak_update22.index)>0:
        cekUserTidakUpdate22 = 1
        try:
            tableUserTidakUpdate22 = '<table class="data-table textsmall bg-tbl" style="font-family: Arial, Helvetica, sans-serif; border-collapse: collapse; width: 100%">' \
                        '<thead class="bg-tbl-header text-tbl-header">' \
                        '<tr>' \
                        '<th style="text-align: center;background-color: #2c4259;color: white; border: 1px solid #ddd; padding: 12px 8px;">No.</th>' \
                        '<th style="text-align: center;background-color: #2c4259;color: white; border: 1px solid #ddd; padding: 12px 8px;">Sales</th>' \
                        '<th style="text-align: center;background-color: #2c4259;color: white; border: 1px solid #ddd; padding: 12px 8px;">Status</th>' \
                        '</tr>' \
                        '</thead>' \
                        '<tbody>'
            no = 1
            for index, row in user_tidak_update22.iterrows():
                if (no % 2) == 0:
                    tableUserTidakUpdate22 +='<tr style="background-color: #f2f2f2">'
                else:
                    tableUserTidakUpdate22 +='<tr>'
                tableUserTidakUpdate22 +='<td style="border: 1px solid #ddd; padding: 8px;">' + str(no) + '</td>' \
                            '<td style="border: 1px solid #ddd; padding: 8px;">' + row['USER_NAME'] + '</td>' \
                             '<td style="border: 1px solid #ddd; padding: 8px;">Tidak Update</td>' \
                             '</tr>'
                no += 1
            tableUserTidakUpdate22 += '</tbody></table>'
        except:
            print("Error di tabel User Tidak Update :", emailsalesRecevier)
    else:
        cekUserTidakUpdate22 = 0
        tableUserTidakUpdate22 ='<table class="data-table textsmall bg-tbl" style="font-family: Arial, Helvetica, sans-serif; border-collapse: collapse; width: 100%">' \
                    '<thead class="bg-tbl-header text-tbl-header">' \
                    '<tr>' \
                    '<th style="text-align: center;background-color: #2c4259;color: white; border: 1px solid #ddd; padding: 12px 8px;">' \
                    '<b>Congrats!!!</b> semua SGM sudah update CAM</th>' \
                    '</tr>' \
                    '</thead></table>' \
                        
                        
    # chart
    sqlChart = """SELECT c.USER_NAME, day(b.v_date) v_day, count(b.id_cam) jml FROM cam b
                LEFT JOIN tbl_user_structure a ON a.staff=b.pic_am
                LEFT JOIN tbl_user c ON c.USER_ID=b.insert_user
                WHERE b.v_date BETWEEN DATE_ADD(CURDATE(), INTERVAL -6 DAY) AND CURDATE()
                """ + param + """
                GROUP BY USER_NAME, v_day
                ORDER BY USER_NAME, v_day"""
    dataChart = pd.read_sql(sqlChart, db)
    
    if len(dataChart.index) != 0:
        dataChart = dataChart.pivot("USER_NAME", "v_day", "jml")
        rcParams['figure.figsize'] = 15,2
        fig, ax = plt.subplots()
        ax = sns.heatmap(dataChart, linewidths=.5, cmap="YlGnBu", annot=True, fmt='.0f', cbar=False)
        plt.xlabel("")
        plt.ylabel("")
        plt.rcParams['xtick.bottom'] = plt.rcParams['xtick.labelbottom'] = False
        plt.rcParams['xtick.top'] = plt.rcParams['xtick.labeltop'] = True
        fig.savefig(fileChart, bbox_inches='tight')
    else:
        img = Image.new('RGB', (275, 30), color = (73, 109, 137))
 
        fnt = ImageFont.truetype('fonts/FrozenBlue.otf', 15)
        d = ImageDraw.Draw(img)
        d.text((10,10), "Hmmm, tim kamu tidak ada activity :(", font=fnt, fill=(255, 255, 0))
         
        img.save(fileChart)
    
    
    try:
        strFrom = 'admin.marketing@mncgroup.com'
        to = ['mujib.nashikha@mncgroup.com']
        strTos = to

        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = 'Report CAM Weekly periode: '+ this_week()
        msgRoot['From'] = 'Admin Mediakit'
        msgRoot['To'] = "%s\r\n" % ",".join(to)

        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)


        msgText = MIMEText("""
                <html lang="en-GB"><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"><style type="text/css" nonce="">
                body,td,div,p,a,input {font-family: arial, sans-serif;}
                </style><meta http-equiv="X-UA-Compatible" content="IE=edge"><link rel="shortcut icon" type="image/x-icon"><title>Notif CAM</title><style type="text/css" nonce="">
                body, td {font-size:13px} a:link, a:active {color:#1155CC; text-decoration:none} a:hover {text-decoration:underline; cursor: pointer} a:visited{color:##6611CC} img{border:0px} pre { white-space: pre; white-space: -moz-pre-wrap; white-space: -o-pre-wrap; white-space: pre-wrap; word-wrap: break-word; max-width: 800px; overflow: auto;} .logo { left: -7px; position: relative; }
                </style></head><body><div class="bodycontainer"><div style="padding:0!important;margin:0!important;display:block!important;min-width:100%!important;width:100%!important;background:#d8e0e3">
                <table width="100%" border="0" cellspacing="0" cellpadding="0" bgcolor="#d8e0e3">
                <tbody><tr><td align="center" valign="top" class="m_2408168722463005219container" style="padding:50px 10px">
                <table width="100%" border="0" cellspacing="0" cellpadding="0">
                <tbody><tr><td align="center">
                <table width="650" border="0" cellspacing="0" cellpadding="0" class="m_2408168722463005219mobile-shell">
                <tbody><tr><td class="m_2408168722463005219td" bgcolor="#ffffff" style="width:650px;min-width:650px;font-size:0pt;line-height:0pt;padding:0;margin:0;font-weight:normal">
                <table width="100%" height="7px" border="0" cellspacing="0" cellpadding="0" bgcolor="#d8e0e3">
                <tbody><tr>
                <td bgcolor="#ffb700" width="30%" class="m_2408168722463005219bg-gradient"></td>
                <td class="m_2408168722463005219td" bgcolor="#203C6A" width="70%"></td>
                </tr>
                </tbody></table>
                <table width="100%" border="0" cellspacing="0" cellpadding="0" bgcolor="#ffffff">
                <tbody><tr><td class="m_2408168722463005219p0-15" style="padding:20px 20px">
                <table width="100%" border="0" cellspacing="0" cellpadding="0" class="m_2408168722463005219shadow" style="border-radius:12px">
                <tbody>
                <tr>
                <td style="text-align:left;width:50%"></td>
                <td style="text-align:right;width:50%">
                <img src="cid:image_logo" alt="" border="0" style="height:60px;padding-right:30px">
                </td>
                </tr>
                
                <tr><td class="m_2408168722463005219pt36 m_2408168722463005219fz-18" style="padding:30px" colspan="2">
                <table width="100%" border="0" cellspacing="0" cellpadding="0">
                <tbody>
                
                <tr>
                <td class="m_2408168722463005219pt36 m_2408168722463005219fz-18" style="color:#1f497d;text-align:center;font-weight:bold;font-size:22px;line-height:1;">
                Hai, """+ salesRecevier +"""
                </td>
                </tr>
                <tr><td class="m_2408168722463005219footer m_2408168722463005219center m_2408168722463005219pb8" style="font-size:14px;line-height:20px;color:#404852;padding:35px 0px 0px 0px;">
                <b style="color:#1f497d">Berikut Report CAM dari TIM kamu, periode """+ this_week() +""":</b>
                </td></tr>
                
                <tr><td class="m_2408168722463005219footer m_2408168722463005219center m_2408168722463005219pb8" style="font-size:14px;line-height:20px;color:#404852;padding:35px 0px 0px 0px;">
                <b style="color:#1f497d">Summary update CAM AM:</b>
                </td></tr>
                
                <tr><td class="m_2408168722463005219footer m_2408168722463005219center m_2408168722463005219pb8" style="font-size:14px;line-height:20px;color:#404852;padding:20px 0px;">
                """+ tableSummary21 +"""
                </td></tr>
                <tr><td class="m_2408168722463005219footer m_2408168722463005219center m_2408168722463005219pb8" style="font-size:14px;line-height:20px;color:#404852;padding:35px 0px 0px 0px;">
                <b style="color:#1f497d">Berikut AM yang tidak update CAM:</b>
                </td></tr>
                
                <tr><td class="m_2408168722463005219footer m_2408168722463005219center m_2408168722463005219pb8" style="font-size:14px;line-height:20px;color:#404852;padding:20px 0px">
                """ + tableUserTidakUpdate21 + """</td></tr>
                <tr><td class="m_2408168722463005219center" style="text-align:center;font-size:14px;line-height:1;color:#404852;padding-bottom:20px">
                
                <tr><td class="m_2408168722463005219footer m_2408168722463005219center m_2408168722463005219pb8" style="font-size:14px;line-height:20px;color:#404852;padding:35px 0px 0px 0px;">
                <b style="color:#1f497d">Summary update CAM SGM:</b>
                </td></tr>
                
                <tr><td class="m_2408168722463005219footer m_2408168722463005219center m_2408168722463005219pb8" style="font-size:14px;line-height:20px;color:#404852;padding:20px 0px;">
                """+ tableSummary22 +"""
                </td></tr>
                <tr><td class="m_2408168722463005219footer m_2408168722463005219center m_2408168722463005219pb8" style="font-size:14px;line-height:20px;color:#404852;padding:35px 0px 0px 0px;">
                <b style="color:#1f497d">Berikut SGM yang tidak update CAM:</b>
                </td></tr>
                
                <tr><td class="m_2408168722463005219footer m_2408168722463005219center m_2408168722463005219pb8" style="font-size:14px;line-height:20px;color:#404852;padding:20px 0px">
                """ + tableUserTidakUpdate22 + """</td></tr>
                <tr><td class="m_2408168722463005219center" style="text-align:center;font-size:14px;line-height:1;color:#404852;padding-bottom:20px">
                
                <p style="text-align:justify;font-size:10px">
                *nb: <br/>
                <i>Jml Sales merupakan data yg terdaftar di Mediakit, jika tidak sesuai bisa dikomunikasikan ke Tim Analyst masing2 unit <br/>
                Untuk SGM sebenernya ngga harus update, jika semua AM under dia rajin update, karena jika meeting bersamaan cukup 1 orang yg update di CAM,
                Kecuali memang ada aktifitas yg dia kerjakan sendiri harus diupdate di CAM
                </i>
                </p></td></tr>
                
                <tr><td class="m_2408168722463005219footer m_2408168722463005219center m_2408168722463005219pb8" style="font-size:14px;line-height:20px;color:#404852;padding:35px 0px 0px 0px;">
                <b style="color:#1f497d">Daily Update CAM:</b>
                </td></tr>
                
                <tr><td class="m_2408168722463005219footer m_2408168722463005219center m_2408168722463005219pb8" style="font-size:14px;line-height:20px;color:#404852;padding:20px 0px;">
                <img src="cid:image_chart" alt="" style="display: block;margin-left: auto;margin-right: auto;width: 50%;">
                </td></tr>
                
                
                <tr><td class="m_2408168722463005219center" style="text-align:center;font-size:14px;line-height:1;color:#404852;padding:0px 20px">
                <a class="text-url" href='""" + link_cam + """'>Klik link ini untuk informasi details dari report CAM</a>
                </td></tr>
                
                <tr><td style="font-size:14px;line-height:1.5;color:#404852;padding:35px 0px">
                <p style="text-align:justify">
                Jika report diatas tidak sesuai atau ada kendala dalam menggunakan Aplikasi SAM ataupun CAM, bisa <i>contact</i> Care Center dibawah ini.
                </p>
                </td>
                </tr>
                
                <tr>
                <td style="font-size:14px;text-align:center;line-height:1.5;color:#404852;">
                <p>
                Terima kasih atas partisipasinya turut aktif menggunakan Mediakit
                </p>
                </td>
                </tr>
                <td style="border-bottom:2px solid #dedede;padding:20px 0px">
                </td>
                </tr>
                <tr>
                <td>
                <table width="100%" border="0" cellspacing="0" cellpadding="0" bgcolor="#ffffff">
                <tbody><tr>
                <td width="30%">
                </td>
                <td class="m_2408168722463005219pb8" width="70%" style="font-size:14px;line-height:1.5;color:#404852;padding:20px 0 0 20px">
                <div style="padding:30px 0 15px;font-size:18px">
                <b style="color:#203c6a">Care Center
                </b>
                - Melayani dengan sepenuh hati
                </div>
                <table>
                <tbody>
                <tr style="padding:10px 0px;"><td style="padding-bottom:10px;padding-right:5px">
                <img src="cid:image_ext" alt=""></td>
                <td style="font-size:13px;">
                6477</td>
                </tr>
                <tr>
                <td style="padding-bottom:10px;padding-right:5px">
                <img src="cid:image_mail" alt="">
                </td>
                <td style="font-size:13px;padding-bottom:10px;padding-right:5px">
                systemanalyst.msi@mncgroup.com
                </td>
                </tr>
                <tr>
                <td style="padding-bottom:10px;padding-right:5px">
                <img src="cid:image_loc" alt="">
                </td>
                <td style="font-size:13px;padding-right:5px">
                <b>DMA - System Analyst
                </b>
                </td>
                </tr>
                <tr>
                <td></td>
                <td style="font-size:10px">
                <p>
                MNC Studios Tower 1 Lt. 10, <br/>
                Kebon Jeruk, Jakarta Barat
                </p>
                </td>
                </tr>
                </tbody></table>
                </td>
                </tr>
                </tbody></table>
                </td>
                </tr>
                </tbody></table>
                </td>
                </tr></tbody></table>
                </td>
                </tr></tbody></table>
                </td>
                </tr></tbody></table>
                </td>
                </tr></tbody></table>
                </td>
                </tr></tbody></table></div>
                </font></div></td></tr></tbody></table></td></tr></tbody></table></div></div></body></html>
        """, 'html')
        msgAlternative.attach(msgText)
        # This example assumes the image is in the current directory
        fp1 = open('images/logo.png', 'rb')
        msgImage1 = MIMEImage(fp1.read())
        fp1.close()

        fp2 = open('images/mail.png', 'rb')
        msgImage2 = MIMEImage(fp2.read())
        fp2.close()

        fp3 = open('images/loc.png', 'rb')
        msgImage3 = MIMEImage(fp3.read())
        fp3.close()

        fp4 = open('images/ext.png', 'rb')
        msgImage4 = MIMEImage(fp4.read())
        fp4.close()
        
        fp5 = open(fileChart, 'rb')
        msgImage5 = MIMEImage(fp5.read())
        fp5.close()


        msgImage1.add_header('Content-ID', '<image_logo>')
        msgRoot.attach(msgImage1)
        msgImage2.add_header('Content-ID', '<image_mail>')
        msgRoot.attach(msgImage2)
        msgImage3.add_header('Content-ID', '<image_loc>')
        msgRoot.attach(msgImage3)
        msgImage4.add_header('Content-ID', '<image_ext>')
        msgRoot.attach(msgImage4)
        msgImage5.add_header('Content-ID', '<image_chart>')
        msgRoot.attach(msgImage5)

        smtp = smtplib.SMTP()
        smtp.connect('webmail.mncgroup.com')
        smtp.sendmail(strFrom, strTos, msgRoot.as_string())
        smtp.quit()
        print("email sent")
    except:
        print("Error email:", emailsalesRecevier)






