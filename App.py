from flask import Flask, request, jsonify, Response
from io import BytesIO
from IPython.core.display import Image
from multiprocessing import Process
from matplotlib import cm
import pandas as pd
import requests
import json
import re
import time
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# YW Bryce, Yiyin, Hardik, Han
app = Flask(__name__)
df = pd.read_csv("main.csv", header = 0)
num_subscribed = 0
count_visit = 0
json_visit = 0
count_A = 0
count_B = 0
source_dict = {}

@app.route('/')
def home():
    global count_visit
    global count_A 
    global count_B 
    count_visit += 1
    
    with open("index.html") as f:
        html = f.read()
    if count_visit <= 10:
        if (count_visit % 2) == 0:
            htmlA = html.replace("background-color: white", "background-color: #8DC0F8")
            htmlA = htmlA.replace("donate.html", "donate.html?from=A")
            return htmlA ##
        else:
            htmlB = html.replace("background-color: white", "background-color: #86D9C0")
            htmlB = htmlB.replace("donate.html", "donate.html?from=B")
            return htmlB ##
    else:
        if count_A > count_B:
            htmlA = html.replace("background-color: white", "background-color: #8DC0F8")
            htmlA = htmlA.replace("donate.html", "donate.html?from=A")
            return htmlA
        else:
            htmlB = html.replace("background-color: white", "background-color: #86D9C0")
            htmlB = htmlB.replace("donate.html", "donate.html?from=B")
            return htmlB
    htmlA = html.replace("background-color: white", "background-color: #8DC0F8")
    htmlA = htmlA.replace("donate.html", "donate.html?from=A")
    return htmlA

@app.route('/browse.html')
def get_table():
    html_t = df.to_html()
    header="TED Talks"
    return f"<html><body><button onclick=history.back()>back</button><h1>{header}<h1>{html_t}</body></html>"

@app.route('/email', methods=["POST"])
def email():
    email = str(request.data, "utf-8")
    global num_subscribed
    if re.match(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}", email): # 1
        with open("emails.txt", "a") as f: # open file in append mode
            f.write(email + "\n") # 2
            num_subscribed += 1
        return jsonify(f"thanks, you're subscriber number {num_subscribed}!")
    return jsonify(f"invalid email!") # 3

@app.route('/donate.html')
def donate():
    global count_A 
    global count_B 
    version = request.args.get("from")
    if version == "A":
        count_A += 1
    if version == "B":
        count_B += 1
    return f"<html1><h1><b><u>Donations</u></b></h1><body>Thank you!<body></html>"

@app.route('/browse.json')
def limiter_json():
    global json_vist
    global source_dict
    header = "TEDTalks/json"
    json_table = df.to_dict(orient = "index")
    ip_source = request.remote_addr
    if ip_source in source_dict.keys():
        if (time.time() - source_dict[ip_source]) > 60:
            source_dictt[ip_source] = time.time()
            return jsonify(json_table)
        else:
            request_message = "TOO MANY REQUEST, 1 REQUEST PER MINUTE"
            source_dict[ip_source] = time.time()
        return Response(request_message, status = 429, headers = {"Retry-After" : 60}) 
    else:
        source_dict[ip_source] = time.time()
        return jsonify(json_table)

@app.route('/dashboard1.svg')
def dashboard_1():
    fig, ax = plt.subplots()
    current_x_views = df["views"]
    current_y_likes = df["likes"]
    
    plt.scatter(x = current_x_views, y = current_y_likes)
    ax.set_xlabel("Views")
    ax.set_ylabel("Likes")
    ax.set_title("Views vs Likes. TED Talks")
    if request.args.get('cmap') != None:
        # citation: https://medium.com/data-science-canvas/way-to-show-colorbar-without-calling-imshow-or-scatter-4a378058316
        colors = plt.cm.hsv(current_y_likes / float(max(current_y_likes)))
        sm = plt.cm.ScalarMappable(cmap=plt.cm.hsv, norm=plt.Normalize(vmin=0, vmax=1))
        ax.set_title("Views vs Likes. Overall Population Watching TED talks")
        plt.scatter(current_x_views,current_y_likes, color = colors)
        plt.colorbar(sm).set_label(request.args['cmap'])
        # --------------------------------------------------------------------------------------------------------------------
    fake_file = BytesIO()
    fig.savefig(fake_file, format = "svg", bbox_inches = "tight")
    plt.close(fig)
    return Response(fake_file.getvalue(), headers = {"Content-Type" : "image/svg+xml"})

@app.route('/dashboard2.svg')
def dashboard_2():
    fig, ax = plt.subplots()
    plt.hist(df["date"])
    ax.set_title("Histogram of Posted TED Talks Date")
    ax.set_xlabel("Date")
    ax.set_ylabel("Count")
    fake_file = BytesIO()
    fig.savefig(fake_file, format = "svg", bbox_inches = "tight")
    plt.close(fig)
    return Response(fake_file.getvalue(), headers = {"Content-Type" : "image/svg+xml"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False)