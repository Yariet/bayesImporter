from glob import glob
import json
from concurrent.futures import ThreadPoolExecutor
import os
import pygsheets
import leaguepedia_parser
import gspread
import pandas
import datetime
from gspread_pandas import Spread, Client
from riotwatcher import LolWatcher
import matplotlib.pyplot as plt
from PIL import Image


def getBayesWardssss(gsheet_key, sheet_name, BASEDIR):
    sa = gspread.service_account("client_secret.json")
    sh = sa.open_by_key(gsheet_key)
    wks = sh.worksheet(sheet_name)

    row = []
    count = 0

    files = sorted(os.listdir(BASEDIR))

    # Get All Players Informations
    bayesFile = open(BASEDIR + "\\" + files[0])
    bayesJson = json.load(bayesFile)

    players = bayesJson["payload"]["payload"]["payload"]["teams"] #import the data of both teams

    # Get All Wards Placement
    for f in files:
        if f.endswith(".json"):
            bayesFile = open(BASEDIR + "\\" + f)
            bayesJson = json.load(bayesFile)

            if bayesJson["payload"]["payload"]["action"] == "PLACED_WARD":
                check = 1  # 0 = True | 1 = False
                row.append([])
                row[count].append(bayesJson["payload"]["payload"]["additionalProperties"]["esportsGameID"])
                row[count].append(round(bayesJson["payload"]["payload"]["payload"]["gameTime"] / 1000))  # Game Time in Seconds
                row[count].append(bayesJson["payload"]["payload"]["payload"]["position"][0])  # xWard
                row[count].append(bayesJson["payload"]["payload"]["payload"]["position"][1])  # yWard
                row[count].append(bayesJson["payload"]["payload"]["payload"]["wardType"])
                for player in players[0]["participants"]: #Check Blue Team
                    if player["urn"] == bayesJson["payload"]["payload"]["payload"]["placerUrn"]:
                        row[count].append(player["summonerName"])
                        row[count].append(str(player["summonerName"]).split()[0])
                        row[count].append("Blue")
                        check = 0
                        break
                if check == 1:
                    for player in players[1]["participants"]:  # Check Red Team
                        if player["urn"] == bayesJson["payload"]["payload"]["payload"]["placerUrn"]:
                            row[count].append(player["summonerName"])
                            row[count].append(str(player["summonerName"]).split()[0])
                            row[count].append("Red")
                            break
                count += 1

            # Closing file
            bayesFile.close()
    wks.append_rows(row)

#gameTime è il minuto massimo che voglio controllare per le ward (in secondi)
#Team inserire il team tag se si vuole prendere un singolo team
def plotWardsssss(gsheet_key, sheet_name, gameTime=9999999, Team=""):
    sa = gspread.service_account("client_secret.json")
    sh = sa.open_by_key(gsheet_key)
    wks = sh.worksheet(sheet_name)

    #get all values from spreadsheet
    bayes = pandas.DataFrame(wks.get_all_values())
    bayes.columns = bayes.iloc[0]
    bayes = bayes[1:]
    teams = []
    teams.append(getUnique(bayes["Team"]))
    teams.append(getUnique(bayes["Side"]))
    xTeam1, xTeam2,yTeam1,yTeam2, colorTeam1, colorTeam2 = [],[],[],[],[],[]
    colors = {teams[0][0]:teams[1][0],teams[0][1]:teams[1][1]}
    i=1

    for x in bayes["gameTime"]:
        if int(x) > gameTime:
            pass
        elif bayes["Team"][i] == teams[0][0] :
            xTeam1.append(512*int(bayes["xWard"][i])/14980) # per plottarli sulla S/R devo fare 512*x/14980, uguale per la y
            yTeam1.append(512*int(bayes["yWard"][i])/14980)
            colorTeam1.append(bayes["Team"][i])
        else:
            xTeam2.append(512*int(bayes["xWard"][i])/14980) # per plottarli sulla S/R devo fare 512*x/14980, uguale per la y
            yTeam2.append(512*int(bayes["yWard"][i])/14980)
            colorTeam2.append(bayes["Team"][i])
        i += 1

    if Team == "":
        df1 = pandas.DataFrame(dict(xWards=xTeam1,yWards=yTeam1,teamColor=colorTeam1))
        df2 = pandas.DataFrame(dict(xWards=xTeam2,yWards=yTeam2,teamColor=colorTeam2))
        fig, ax = plt.subplots()
        ax.scatter(df1["xWards"],df1["yWards"], c=df1["teamColor"].map(colors), label=df1["teamColor"][0], zorder=1)
        ax.scatter(df2["xWards"],df2["yWards"], c=df2["teamColor"].map(colors), label=df2["teamColor"][0], zorder=1)
    elif Team == colorTeam1[0]:
        df1 = pandas.DataFrame(dict(xWards=xTeam1, yWards=yTeam1, teamColor=colorTeam1))
        fig, ax = plt.subplots()
        ax.scatter(df1["xWards"], df1["yWards"], c=df1["teamColor"].map(colors), label=df1["teamColor"][0], zorder=1)
    else:
        df2 = pandas.DataFrame(dict(xWards=xTeam2, yWards=yTeam2, teamColor=colorTeam2))
        fig, ax = plt.subplots()
        ax.scatter(df2["xWards"], df2["yWards"], c=df2["teamColor"].map(colors), label=df2["teamColor"][0], zorder=1)
    img = Image.open("Summoners Rift Minimap.png")
    plt.imshow(img,zorder=0, extent=[0,512,0,512])
    plt.axis("off")
    plt.legend(loc="upper right")
    plt.show()

def getUnique(array):
    output = []
    for x in array:
        if x not in output:
            output.append(x)
    return output

def getJsonFromFile(filename="dump.json"):
    # Get All Players Informations
    bayesFile = open(filename)
    bayesJson = json.load(bayesFile)
    bayesFile.close()
    return bayesJson

def gsheetImportWards(gsheet_key, sheet_name, rows):
    sa = gspread.service_account("client_secret.json")
    sh = sa.open_by_key(gsheet_key)
    wks = sh.worksheet(sheet_name)
    wks.append_rows(rows)

def getWards(bayesJson):
    row = []
    count = 0

    # Get All Players Informations
    players = bayesJson["events"][0]["payload"]["payload"]["payload"]["teams"] #import the data of both teams

    # Get All Wards Placement
    for event in bayesJson["events"]:
        if event["payload"]["payload"]["action"] == "PLACED_WARD" and event["payload"]["payload"]["payload"]["wardType"] != "unknown":
            check = 1  # 0 = True | 1 = False
            row.append([])
            row[count].append(event["payload"]["payload"]["additionalProperties"]["esportsGameID"])
            row[count].append(round(event["payload"]["payload"]["payload"]["gameTime"] / 1000))  # Game Time in Seconds
            row[count].append(event["payload"]["payload"]["payload"]["position"][0])  # xWard
            row[count].append(event["payload"]["payload"]["payload"]["position"][1])  # yWard
            row[count].append(event["payload"]["payload"]["payload"]["wardType"])
            for player in players[0]["participants"]: #Check Blue Team
                if player["urn"] == event["payload"]["payload"]["payload"]["placerUrn"]:
                    row[count].append(player["summonerName"])
                    row[count].append(str(player["summonerName"]).split()[0])
                    row[count].append("Blue")
                    check = 0
                    break
            if check == 1:
                for player in players[1]["participants"]:  # Check Red Team
                    if player["urn"] == event["payload"]["payload"]["payload"]["placerUrn"]:
                        row[count].append(player["summonerName"])
                        row[count].append(str(player["summonerName"]).split()[0])
                        row[count].append("Red")
                        break
            count += 1
    return row

def gsheetPlotWards(gsheet_key, sheet_name, Team, gameTime=9999999):
    sa = gspread.service_account("client_secret.json")
    sh = sa.open_by_key(gsheet_key)
    wks = sh.worksheet(sheet_name)

    #get all values from spreadsheet and filter them using the Team value
    bayes = pandas.DataFrame(wks.get_all_values())
    plotWards(bayes,Team,gameTime)

def plotWards(rows, Team, gameTime=9999999):
    #get all values from spreadsheet and filter them using the Team value
    bayes = pandas.DataFrame(rows)
    bayes.loc[-1] = ["esportsGameID","gameTime","xWard","yWard","wardType","wardedBy","Team","Side"]
    bayes.index = bayes.index + 1
    bayes.sort_index(inplace=True)
    bayes.columns = bayes.iloc[0]
    bayes = bayes[bayes["Team"] == Team]
    bayes = bayes.reset_index()
    player = []
    player.append(getUnique(bayes["wardedBy"]))
    colors = {player[0][0]: "Red", player[0][1]: "Blue", player[0][2]: "Yellow", player[0][3]: "Green", player[0][4]: "White" }
    xTeam1,yTeam1,colorTeam1,time1 = [],[],[],[]
    i=0

    for x in bayes["gameTime"]:
        if int(x) > gameTime:
            pass
        else:
            xTeam1.append(512*int(bayes["xWard"][i])/14980) # per plottarli sulla S/R devo fare 512*x/14980, uguale per la y
            yTeam1.append(512*int(bayes["yWard"][i])/14980)
            colorTeam1.append(bayes["wardedBy"][i])
            time1.append(str(datetime.timedelta(seconds=int(bayes["gameTime"][i]))).split(":",1)[1])
        i += 1

    df1 = pandas.DataFrame(dict(xWards=xTeam1, yWards=yTeam1, teamColor=colorTeam1, wardTime=time1))
    fig, ax = plt.subplots()
    for k,d in df1.groupby("teamColor"):
        ax.scatter(d["xWards"], d["yWards"], c=d["teamColor"].map(colors), label=k, zorder=1)
    for idx,row in df1.iterrows():
        ax.annotate(row["wardTime"],(row["xWards"], row["yWards"]), xytext=(0,5), textcoords="offset points", family="sans-serif", color="white")


    img = Image.open("Summoners Rift Minimap.png")
    plt.imshow(img,zorder=0, extent=[0,512,0,512])
    plt.axis("off")
    plt.legend(loc="upper right")
    plt.show()