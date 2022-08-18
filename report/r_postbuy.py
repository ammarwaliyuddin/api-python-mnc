from services import config

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import datetime
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import rcParams
sns.set_theme(style="ticks", color_codes=True)
import random

import warnings
warnings.filterwarnings("ignore")

def postbuy(data):

    print(data)
    ### FILTERING
    periodenya = "'"+ data['year'] +"-" + config.clrDataMonth(data['month']) +"'"  #year-month
    advertisernya = data['advertiser']
    po_no_nya = "'"+ config.base64_decode(data['no_po']) +"'"
    type_ordernya = data['type_order'] 
    
    sql_adv = """SELECT a.nama_adv FROM db_m_advertiser a
    WHERE a.id_adv = """ + advertisernya + """ """
    adv = pd.read_sql(sql_adv,config.db)

    ora_periode = """SELECT DISTINCT to_char(a.AIR_DATE,'MONTH YYYY') PERIOD FROM DB_GEN21_CLEAN_DETAIL a
    where to_char(a.AIR_DATE,'YYYY-MM') = """+periodenya+""" """
    periode = pd.read_sql(ora_periode,config.dbo)
    # periode = periode.iloc[index]['PERIOD'].str.strip()
    print(periode)
    
    ### periode
    rand = random.randint(0,100)

    ## ambil data sam 1
    ora1 ="""SELECT to_char(a.AIR_DATE,'DD') tanggal, a.DAYPART_V1 DAYPART, to_char(a.AIR_DATE,'DAY') DAY, a.FLAG_RATE, a.DUR, a.NETT, a.TVR FROM DB_GEN21_CLEAN_DETAIL a
    where to_char(a.AIR_DATE,'YYYY-MM') = """ + periodenya + """ AND a.ID_adv = """ + advertisernya + """ AND a.PO_NO = """+po_no_nya+""" """
    
    data1 = pd.read_sql(ora1, config.dbo)
    # print(data1)
    intra1 ="""SELECT * FROM dim_spot30"""
    dim_spot = pd.read_sql(intra1, config.db)

    intra_type = """SELECT a.code_kombinasi_flagrate, d.`group` keyOrder
                FROM gen_mapping_flagrate a
                LEFT JOIN gen_code_platform b ON b.code=a.code_platform
                LEFT JOIN gen_code_platform_group c ON c.id=b.id_group
                LEFT JOIN gen_code_typeorder d ON d.code=a.code_type_order
                LEFT JOIN gen_code_unitorder e ON e.code=a.code_unit_revenue"""             
    dim_type = pd.read_sql(intra_type, config.db)

    merged1 =  pd.merge(data1, dim_spot, left_on="DUR", right_on="duration", how="left")
    merged1 =  pd.merge(merged1, dim_type, left_on="FLAG_RATE", right_on="code_kombinasi_flagrate", how="left")
    merged1["grp"]=merged1["TVR"]*merged1["spot_30"]
   
    # print(merged1['keyOrder'] == type_ordernya)

    merged1 = merged1.loc[(merged1['keyOrder'] == type_ordernya)]
    grafik = merged1.groupby('TANGGAL').agg({'spot_30': ['sum'],'grp':['sum']}).reset_index()
    grafik.columns = ['date', 'spot', 'grp']
    # plot grafik
    fig,ax= plt.subplots(1,1,figsize=(9,4))
    ax.plot(grafik.date, grafik.spot, label="SPOT",marker="o")
    lns1= ax.plot(grafik.date, grafik.spot, color="brown", label="SPOT",marker="o")
    ax.set_ylabel("SPOT", color="brown", fontsize=14)
    # twin object for two different y-axis on the sample plot
    ax2=ax.twinx()
    # make a plot with different y-axis using second axis object
    lns2= ax2.plot(grafik.date, grafik.grp, color="blue", label="GRP",marker="o")
    ax2.set_ylabel("GRP",color="blue",fontsize=14)
    # plt.show()
    plt.title("GRP Daily", loc="center", color="blue", weight="bold", pad=15, fontsize=16)
    lns = lns1+lns2
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc=0)
    fig = ax2.get_figure()
    fig.savefig('grafik/grpdaily.png', bbox_inches='tight')
    # plt.show()
    plt.close()

    grafik2 = merged1.groupby(['DAYPART','DAY']).agg({'grp': ['sum']}).reset_index()
    grafik2.columns = ['daypart', 'day', 'grp']
    grafik2['day'] = grafik2['day'].str.strip()
    day = pd.DataFrame({
    'days': ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY','SUNDAY'],
    'days_num': [1, 2, 3, 4, 5, 6, 7]
    })
    day['days'] = day['days'].str.strip()

    daypart = pd.DataFrame({
    'dayparts': ['NPT(00-06)','NPT(06-18)', 'PT(18-22)', 'NPT(22-24)'],
    'dayparts_num': [1, 2, 3, 4]
    })


    grafik2 = pd.merge(grafik2, day, left_on="day", right_on="days", how="left")
    grafik2 = pd.merge(grafik2, daypart, left_on="daypart", right_on="dayparts", how="left")
    
    grafik2 = grafik2.sort_values(['dayparts_num', 'days_num'], ascending=[True, True])
    uniqueValues = grafik2['dayparts'].unique()
    uniqueday = grafik2['day'].unique()

    grafik2 = grafik2.pivot(index="dayparts_num", columns="days_num", values="grp")
    lebar = len(grafik2)
    rcParams['figure.figsize'] = 9, 1.2*lebar
    ax = sns.heatmap(grafik2, linewidths=.5, cmap="YlGnBu", annot=True, fmt='.2f', cbar=False)
    # Show all ticks and label them with the respective list entries

    # ax.set_xticklabels(day.days, rotation=0)
    ax.set_xticklabels(uniqueday, rotation=0)
    ax.set_yticklabels(uniqueValues, rotation=90)

    plt.xlabel("")
    plt.ylabel("")
    fig = ax.get_figure()
    fig.savefig('grafik/daypart.png', bbox_inches='tight')
    # plt.show()
    plt.close()


    ### TABLE 1
    ora2 ="""SELECT a.ID_BRAND,a.FLAG_RATE, a.ID_CHANNEL, CONCAT(a.ID_CHANNEL,CONCAT('|', a.CODE_BANNER)) AS KEY, a.DUR, a.NETT, a.TVR FROM DB_GEN21_CLEAN_DETAIL a
    where  to_char(a.AIR_DATE,'YYYY-MM') = """ + periodenya + """ AND a.ID_adv = """ + advertisernya + """ AND a.PO_NO = """+ po_no_nya +""" """

    data2 = pd.read_sql(ora2,config.dbo)

    intra2 = """SELECT DISTINCT a.id_brand, a.nama_brand FROM db_m_brand a"""
    dim_brand = pd.read_sql(intra2,config.db)

    intra_channel = """SELECT a.id_channel, a.name_channel from db_m_channel a"""
    dim_channel = pd.read_sql(intra_channel, config.db)

    merged2 = pd.merge(data2, dim_spot, left_on="DUR", right_on="duration", how="left")
    merged2["grp"]=merged2["TVR"]*merged2["spot_30"]
    merged2 = pd.merge(merged2, dim_type, left_on="FLAG_RATE", right_on="code_kombinasi_flagrate", how="left")
    merged3 = pd.merge(merged2, dim_brand, left_on="ID_BRAND", right_on="id_brand", how="left")
    merged3 = pd.merge(merged3, dim_channel, left_on="ID_CHANNEL", right_on="id_channel", how="left")

    merged3 = merged3.loc[(merged3['keyOrder'] == type_ordernya)]
    table1 = merged3.groupby(['nama_brand','name_channel']).agg({'NETT': ['sum'],'spot_30': ['sum'],'grp':['sum']}).reset_index()
    table1.columns = ['nama_brand', 'name_channel', 'nett','spot', 'grp']
    table1['nett']=table1['nett']/1000000
    table1['lvlcprp']=table1['nett']/table1['grp']

    # print(table1)

    ## TABLE TOP 10 PROGRAM RCTI
    if len(table1.index)>0 :
        try:
            tableBrand = '<table style="font-family: Arial, Helvetica, sans-serif; border-collapse: collapse; width: 100%"><td class="m_2408168722463005219footer m_2408168722463005219center m_2408168722463005219pb8" style="font-size:14px;line-height:20px;color:#404852;text-align:center;padding:0px 0px 0px 0px;"> \
                                <b style="color:#1f497d">Brand Review</b> \
                                </td></table> <br>'
            tableBrand += '<table class="data-table textsmall bg-tbl" style="font-family: Arial, Helvetica, sans-serif; border-collapse: collapse; width: 100%">' \
                        '<thead class="bg-tbl-header text-tbl-header">' \
                        '<tr>' \
                        '<th style="text-align: center;background-color: #2c4259;color: white; border: 1px solid #ddd; padding: 12px 8px;">No.</th>' \
                        '<th style="text-align: center;background-color: #2c4259;color: white; border: 1px solid #ddd; padding: 12px 8px;">Nama Brand</th>' \
                        '<th style="text-align: center;background-color: #2c4259;color: white; border: 1px solid #ddd; padding: 12px 8px;">Channel</th>' \
                        '<th style="text-align: center;background-color: #2c4259;color: white; border: 1px solid #ddd; padding: 12px 8px;">NETT</th>' \
                        '<th style="text-align: center;background-color: #2c4259;color: white; border: 1px solid #ddd; padding: 12px 8px;">SPOT</th>' \
                        '<th style="text-align: center;background-color: #2c4259;color: white; border: 1px solid #ddd; padding: 12px 8px;">GRP</th>' \
                        '<th style="text-align: center;background-color: #2c4259;color: white; border: 1px solid #ddd; padding: 12px 8px;">LVLCPRP</th>' \
                        '</tr>' \
                        '</thead>' \
                        '<tbody>'
            no = 1
            for index, row in table1.iterrows():
                if (no % 2) == 0:
                    tableBrand +='<tr style="background-color: #f2f2f2">'
                else:
                    tableBrand +='<tr>'
                tableBrand +='<td style="border: 1px solid #ddd;font-size: 12px; padding: 8px;">' + str(no) + '</td>' \
                            '<td style="border: 1px solid #ddd;font-size: 12px; padding: 8px;">' + str(table1.iloc[index]['nama_brand']) + '</td>' \
                            '<td style="border: 1px solid #ddd;font-size: 12px; padding: 8px;">' + str(table1.iloc[index]['name_channel']) + '</td>' \
                            '<td style="border: 1px solid #ddd;font-size: 12px; padding: 8px; text-align: right">' +  str("{:.0f}".format(table1.iloc[index]['nett'])) + '</td>' \
                            '<td style="border: 1px solid #ddd;font-size: 12px; padding: 8px; text-align: right">' +  str("{:.0f}".format(table1.iloc[index]['spot'])) + '</td>' \
                            '<td style="border: 1px solid #ddd;font-size: 12px; padding: 8px; text-align: right">' +  str("{:.0f}".format(table1.iloc[index]['grp'])) + '</td>' \
                            '<td style="border: 1px solid #ddd;font-size: 12px; padding: 8px; text-align: right">' +  str("{:.0f}".format(table1.iloc[index]['lvlcprp'])) + '</td>' \
                            '</tr>'
                no += 1
            tableBrand += '</tbody></table>'

        except:
            print("Error di tabel User Tidak Update : brand")
    else:
        tableBrand = '<table class="data-table textsmall bg-tbl" style="font-family: Arial, Helvetica, sans-serif; border-collapse: collapse; width: 100%">' \
                '<thead class="bg-tbl-header text-tbl-header">' \
                '<tr>' \
                '<th style="text-align: center;background-color: #2c4259;color: white; border: 1px solid #ddd; padding: 12px 8px;">' \
                '<b>Data Planner belum Update</b></th>' \
                '</tr>' \
                '</thead></table>' 

    intra3 = """SELECT distinct a.key_program, a.program FROM program_gen a"""
    dim_program = pd.read_sql(intra3,config.db)
    merged4 = pd.merge(merged2, dim_program, left_on="KEY", right_on="key_program", how="left")
    merged4 = pd.merge(merged4, dim_channel, left_on="ID_CHANNEL", right_on="id_channel", how="left")
    merged4["grp"]=merged4["TVR"]*merged4["spot_30"]
    # print(merged4)
    merged4 = merged4.loc[(merged4['keyOrder'] == type_ordernya)]
    table2 = merged4.groupby(['program','name_channel']).agg({'NETT': ['sum'],'spot_30': ['sum'],'grp':['sum']}).reset_index()
    table2.columns = ['program', 'name_channel', 'nett','spot', 'grp']
    table2['nett']=table2['nett']/1000000
    table2['lvlcprp']=table2['nett']/table2['grp']

    ## TABLE TOP 10 PROGRAM MNCTV
    if len(table2.index)>0 :
        try:
            tableProgram = '<table style="font-family: Arial, Helvetica, sans-serif; border-collapse: collapse; width: 100%"><td class="m_2408168722463005219footer m_2408168722463005219center m_2408168722463005219pb8" style="font-size:14px;line-height:20px;color:#404852;text-align:center;padding:0px 0px 0px 0px;"> \
                                <b style="color:#1f497d">Program Review</b> \
                                </td></table> <br>'
            tableProgram += '<table class="data-table textsmall bg-tbl" style="font-family: Arial, Helvetica, sans-serif; border-collapse: collapse; width: 100%">' \
                        '<thead class="bg-tbl-header text-tbl-header">' \
                        '<tr>' \
                        '<th style="text-align: center;background-color: #2c4259;color: white; border: 1px solid #ddd; padding: 12px 8px;">No.</th>' \
                        '<th style="text-align: center;background-color: #2c4259;color: white; border: 1px solid #ddd; padding: 12px 8px;">Nama Program</th>' \
                        '<th style="text-align: center;background-color: #2c4259;color: white; border: 1px solid #ddd; padding: 12px 8px;">Channel</th>' \
                        '<th style="text-align: center;background-color: #2c4259;color: white; border: 1px solid #ddd; padding: 12px 8px;">NETT</th>' \
                        '<th style="text-align: center;background-color: #2c4259;color: white; border: 1px solid #ddd; padding: 12px 8px;">SPOT</th>' \
                        '<th style="text-align: center;background-color: #2c4259;color: white; border: 1px solid #ddd; padding: 12px 8px;">GRP</th>' \
                        '<th style="text-align: center;background-color: #2c4259;color: white; border: 1px solid #ddd; padding: 12px 8px;">LVLCPRP</th>' \
                        '</tr>' \
                        '</thead>' \
                        '<tbody>'
            no = 1
            for index, row in table2.iterrows():
                if (no % 2) == 0:
                    tableProgram +='<tr style="background-color: #f2f2f2">'
                else:
                    tableProgram +='<tr>'
                tableProgram +='<td style="border: 1px solid #ddd;font-size: 12px; padding: 8px;">' + str(no) + '</td>' \
                            '<td style="border: 1px solid #ddd;font-size: 12px; padding: 8px;">' + str(table2.iloc[index]['program']) + '</td>' \
                                        '<td style="border: 1px solid #ddd;font-size: 12px; padding: 8px;">' + str(table2.iloc[index]['name_channel']) + '</td>' \
                            '<td style="border: 1px solid #ddd;font-size: 12px; padding: 8px; text-align: right">' + str("{:.0f}".format(table2.iloc[index]['nett'])) + '</td>' \
                            '<td style="border: 1px solid #ddd;font-size: 12px; padding: 8px; text-align: right">' + str("{:.0f}".format(table2.iloc[index]['spot'])) + '</td>' \
                            '<td style="border: 1px solid #ddd;font-size: 12px; padding: 8px; text-align: right">' + str("{:.0f}".format(table2.iloc[index]['grp'])) + '</td>' \
                            '<td style="border: 1px solid #ddd;font-size: 12px; padding: 8px; text-align: right">' + str("{:.0f}".format(table2.iloc[index]['lvlcprp'])) + '</td>' \
                            '</tr>'
                no += 1
            tableProgram += '</tbody></table>'

        except:
            print("Error di tabel User Tidak Update : program")
    else:
        tableProgram = '<table class="data-table textsmall bg-tbl" style="font-family: Arial, Helvetica, sans-serif; border-collapse: collapse; width: 100%">' \
                '<thead class="bg-tbl-header text-tbl-header">' \
                '<tr>' \
                '<th style="text-align: center;background-color: #2c4259;color: white; border: 1px solid #ddd; padding: 12px 8px;">' \
                '<b>Data Planner belum Update</b></th>' \
                '</tr>' \
                '</thead></table>' 

    print("sampai sini")
    orantc ="""SELECT a.FLAG_RATE, SUM(a.NETT)/1000000 NETT_NTC FROM DB_GEN21_CLEAN_DETAIL a
            where  to_char(a.AIR_DATE,'YYYY-MM') = """ + periodenya + """ AND a.ID_adv = """ + advertisernya + """ AND a.PO_NO = """+ po_no_nya +""" AND a.KET_INVENTORY='N'
            GROUP BY a.FLAG_RATE"""
    data_ntc = pd.read_sql(orantc, config.dbo)
    merged_ntc = pd.merge(data_ntc, dim_type, left_on="FLAG_RATE", right_on="code_kombinasi_flagrate", how="left")
    merged_ntc = merged_ntc.loc[(merged_ntc['keyOrder'] == type_ordernya)]
    nett_total = table1['nett'].sum()
    ntc_total = merged_ntc['NETT_NTC'].sum()
    grp_total = table1['grp'].sum()
    cprp_total = nett_total/grp_total
    tableSummary1 ='<table class="data-table textsmall bg-tbl" style="font-family: Arial, Helvetica, sans-serif; border-collapse: collapse; width: 100%">' \
        '<thead class="bg-tbl-header text-tbl-header">' \
        '<tr>' \
        '<th style="text-align: center;background-color: #2c4259;color: white; border: 1px solid #ddd; height: 27px; padding: 12px 8px;">NETT</th>' \
        '<th style="text-align: center;background-color: #2c4259;color: white; border: 1px solid #ddd; height: 27px; padding: 12px 8px;">NETT NTC</th>' \
        '<th style="text-align: center;background-color: #2c4259;color: white; border: 1px solid #ddd; height: 27px; padding: 12px 8px;">GRP</th>' \
        '<th style="text-align: center;background-color: #2c4259;color: white; border: 1px solid #ddd; height: 27px; padding: 12px 8px;">LVL CPRP</th>' \
        '</tr>' \
        '</thead>' \
        '<tbody>'\
        '<td style="text-align: center; background-color:white; color: #2c4259; font-size: 18px;font-weight:bold; height: 27px; border: 1px solid  #ddd; width:25%">'+str("{:.0f}".format(nett_total))+'</td>' \
        '<td style="text-align: center; background-color:white; color: #2c4259; font-size: 18px;font-weight:bold; height: 27px; border: 1px solid  #ddd; width:25%">'+str("{:.0f}".format(ntc_total))+'</td>' \
        '<td style="text-align: center; background-color:white; color: #2c4259; font-size: 18px;font-weight:bold; height: 27px; border: 1px solid #ddd; width:25%">'+str("{:.0f}".format(grp_total))+'</td>' \
        '<td style="text-align: center; background-color:white; color: #2c4259; font-size: 18px;font-weight:bold; height: 27px; border: 1px solid #ddd; width:25%">'+str("{:.0f}".format(cprp_total))+'</td>' \
        '</tbody></table>'

    tableHeader ='<table class="data-table textsmall bg-tbl" style="font-family: Arial, Helvetica, sans-serif; border-collapse: collapse; width: 100%">' \
        '<tbody>'\
        '<tr>' \
        '<td style="text-align: left; background-color:white; color: #2c4259; font-size: 14px;font-weight:bold; border: 1px ; width:25%">ADVERTISER</td>' \
        '<td style="text-align: left; background-color:white; color: #2c4259; font-size: 14px;font-weight:bold; border: 1px ; width:5%">:</td>' \
        '<td style="text-align: left; background-color:white; color: #2c4259; font-size: 14px;font-weight:bold; border: 1px ; width:65%">'+ str(adv.iloc[0]['nama_adv'])+'</td>' \
        '</tr>' \
        '<tr>' \
        '<td style="text-align: left; background-color:white; color: #2c4259; font-size: 14px;font-weight:bold; border: 1px; width:25%">PO NO</td>' \
        '<td style="text-align: left; background-color:white; color: #2c4259; font-size: 14px;font-weight:bold; border: 1px; width:5%">:</td>' \
        '<td style="text-align: left; background-color:white; color: #2c4259; font-size: 14px;font-weight:bold; border: 1px; width:65%">'+po_no_nya[1:-1]+'</td>' \
        '</tr>' \
        '<tr>' \
        '<td style="text-align: left; background-color:white; color: #2c4259; font-size: 14px;font-weight:bold; border: 1px; width:25%">Tipe Order</td>' \
        '<td style="text-align: left; background-color:white; color: #2c4259; font-size: 14px;font-weight:bold; border: 1px; width:5%">:</td>' \
        '<td style="text-align: left; background-color:white; color: #2c4259; font-size: 14px;font-weight:bold; border: 1px; width:65%">'+type_ordernya+'</td>' \
        '</tr>' \
        '<tr>' \
        '<td style="text-align: left; background-color:white; color: #2c4259; font-size: 14px;font-weight:bold; border: 1px; width:25%">Periode</td>' \
        '<td style="text-align: left; background-color:white; color: #2c4259; font-size: 14px;font-weight:bold; border: 1px; width:5%">:</td>' \
        '<td style="text-align: left; background-color:white; color: #2c4259; font-size: 14px;font-weight:bold; border: 1px; width:65%">'+ str(periode.iloc[0]['PERIOD']).title() +'</td>' \
        '</tr>' \
        '</tbody></table>'


    ###
    sqlcoba ="""SELECT a.USER_ID, a.USER_NAME FROM tbl_user a
            WHERE a.ACTIVE=1 AND a.ID_BU=61 AND a.ID_SECTION IN (496,513,497)
            AND a.POSITION IN ('HEAD','MNG') limit 1"""
    dataSales = pd.read_sql(sqlcoba, config.db)

    for index, rowSales in dataSales.iterrows():
        salesRecevier = rowSales['USER_NAME']
        emailsalesRecevier = rowSales['USER_ID']

        print('data untuk sales:', salesRecevier)


    try:
        strFrom = 'admin.marketing@mncgroup.com'
        to = ['khoerul.fatihin@mncgroup.com']
        # to = ['jaenudin.fawwaz@mncgroup.com']
        # to = ['mujib.nashikha@mncgroup.com']
        strTos = to

        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = 'Report Postbuy '+str(periode.iloc[0]['PERIOD']).title()
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
                <td bgcolor="#186997" width="30%" class="m_2408168722463005219bg-gradient"></td>
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
                <td class="m_2408168722463005219pt36 m_2408168722463005219fz-18" style="color:#1f497d;text-align:center;font-weight:bold;font-size:22px;line-height:1;margin-bottom:10px;">
                Hai, """+salesRecevier+"""
                </td>
                </tr>
                <br>
                <tr><td class="header" style="font-size:14px;line-height:10px;color:#404852;padding: 6px;border: 2px solid #1f497d; margin: 5px;">
                <h4 class="m_2408168722463005219pt36 m_2408168722463005219fz-18" style="color:#1f497d;text-align:center;font-weight:bold;font-size:18px;line-height:1;margin-bottom:8px;">
                REPORT POSTBUY
                </h4>""" + tableHeader + """</td></tr>
                
                <tr><td class="m_2408168722463005219footer m_2408168722463005219center m_2408168722463005219pb8" style="font-size:14px;line-height:20px;color:#404852;padding:20px 0px 20px 0px;">
                <b style="color:#1f497d">Summary :</b>
                </td></tr>
        
                <tr><td class="m_2408168722463005219footer m_2408168722463005219center m_2408168722463005219pb8" style="font-size:14px;line-height:20px;color:#404852;padding:10px 0px">
                """ + tableSummary1 + """</td></tr>
                
                <tr><td class="m_2408168722463005219center" style="text-align:center;font-size:14px;line-height:1;color:#404852;padding-bottom:20px">         
                <p style="text-align:justify;font-size:10px">
                *nb: <br/>
                <i>Uang dalam satuan juta
                </i>
                </p></td></tr>
                
                <tr><td class="m_2408168722463005219footer m_2408168722463005219center m_2408168722463005219pb8" style="font-size:14px;line-height:20px;color:#404852;padding:20px 0px 20px 0px;">
                <b style="color:#1f497d">Berikut Report GRP Daily, periode """+ str(periode.iloc[index]['PERIOD']).title() +""":</b>
                </td></tr>
            
                <tr><td class="m_2408168722463005219pt36 m_2408168722463005219fz-18" style="color:#1f497d;text-align:center;font-weight:bold;font-size:22px;line-height:1;">
                <img src="cid:image"""+str(rand)+"""grp" alt="" style="padding:30px 0px"></td></tr>
                
                <tr><td class="m_2408168722463005219footer m_2408168722463005219center m_2408168722463005219pb8" style="font-size:14px;line-height:20px;color:#404852;padding:20px 0px 20px 0px;">
                <b style="color:#1f497d">Berikut GRP berdasarkan Day x Daypart, periode """+ str(periode.iloc[index]['PERIOD']).title() +""":</b>
                </td></tr>
            
                <tr><td class="m_2408168722463005219pt36 m_2408168722463005219fz-18" style="color:#1f497d;text-align:center;font-weight:bold;font-size:22px;line-height:1;">
                <img src="cid:image"""+str(rand)+"""daypart" alt="" style="padding:30px 0px"></td></tr>
            
                            
                <tr><td class="m_2408168722463005219footer m_2408168722463005219center m_2408168722463005219pb8" style="font-size:14px;line-height:20px;color:#404852;padding:30px 0px 20px 0px;">
                <b style="color:#1f497d">Berikut Brand dan Program Review, periode """+str(periode.iloc[index]['PERIOD']).title()+""":</b>
                </td></tr>

                <tr><td class="m_2408168722463005219footer m_2408168722463005219center m_2408168722463005219pb8" style="font-size:14px;line-height:20px;color:#404852;padding:10px 0px">
                """ + tableBrand + """</td></tr>
                
                <tr><td class="m_2408168722463005219center" style="text-align:center;font-size:14px;line-height:1;color:#404852;padding-bottom:20px">         
                <p style="text-align:justify;font-size:10px">
                *nb: <br/>
                <i>Uang dalam satuan juta
                </i>
                </p></td></tr>
                
                <tr><td class="m_2408168722463005219footer m_2408168722463005219center m_2408168722463005219pb8" style="font-size:14px;line-height:20px;color:#404852;padding:10px 0px">
                """ + tableProgram + """</td></tr>
                
                <tr><td class="m_2408168722463005219center" style="text-align:center;font-size:14px;line-height:1;color:#404852;padding-bottom:20px">         
                <p style="text-align:justify;font-size:10px">
                *nb: <br/>
                <i>Uang dalam satuan juta
                </i>
                </p></td></tr>

                <tr>
                <th style="text-align: center;background-color: white;color: #2c4259; border: 4px #ddd; padding: 12px 8px; font-weight:bold;font-size:22px;line-height:1;">
                <font face="Segoe Script" >
                <b>Have A Nice Day  &#128522; </b></font></th>
                </tr>
            
            
                <tr><td style="font-size:14px;line-height:1.5;color:#404852;padding:20px 0px">
                <p style="text-align:center;">
                Jika report diatas tidak sesuai mohon bisa menghubungi Sales PIC masing-masing.
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

                </tbody></table>
                </td>
                </tr></tbody></table>
                </td>
                </tr></tbody></table>
                </td>
                <tr>
                    <td style="background-color:#186997;">
                        <img src="cid:image_footer" style="max-width:100%" alt="">
                    </td>                            
                </tr>
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

        fp5 = open('grafik/grpdaily.png', 'rb')
        msgImage5 = MIMEImage(fp5.read())
        fp5.close()
        
        fp6 = open('grafik/daypart.png', 'rb')
        msgImage6 = MIMEImage(fp6.read())
        fp6.close()

        fp11 = open('images/foot_fix.png', 'rb')
        msgImage11 = MIMEImage(fp11.read())
        fp11.close()


        msgImage1.add_header('Content-ID', '<image_logo>')
        msgRoot.attach(msgImage1)
        msgImage5.add_header('Content-ID', '<image'+str(rand)+'grp>')
        msgRoot.attach(msgImage5)
        msgImage6.add_header('Content-ID', '<image'+str(rand)+'daypart>')
        msgRoot.attach(msgImage6)
        msgImage11.add_header('Content-ID', '<image_footer>')
        msgRoot.attach(msgImage11)


        smtp = smtplib.SMTP()
        smtp.connect('webmail.mncgroup.com')
        smtp.sendmail(strFrom, strTos, msgRoot.as_string())
        # kodingan cek directory
        # cek file yang ada di directory
        # jika ada hapus file 
        smtp.close()
        #smtp.quit()
        print("email sent")
        return True
    except Exception as e:
        print(e)
        print("Error email:", emailsalesRecevier)
        return False