#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 01:04:38 2023

@author: shree
"""
from flask import Flask, render_template, request, Response, session, send_file
import server
import client
import json
import sys

app = Flask(__name__)
app.secret_key = "WoC"
glob_vars = dict()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/download")
def getPlotCSV():

    csv = '1,2,3\n4,5,6\n'
    return Response(
                    csv,
                    mimetype="text/csv",
                    headers={"Content-disposition":
                             "attachment; filename=myplot.csv"}
    )


@app.route('/feed_server')
def video_server():
    global client_socket

    return Response(server.feed_generator(client_socket),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/feed_client')
def video_client():
    global host_ip, port, glob_vars
    glob_vars["message"] = ""
    return Response(client.feed_generator(host_ip, port, glob_vars),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/server_status', methods=['GET'])
def server_status():  
  return json.dumps(glob_vars)

@app.route('/client_status', methods=['GET'])
def client_status():
  return json.dumps(glob_vars)


@app.route("/server")
def server_page():
    global host_ip, port, connected
    host_ip, port, connected = "", "", "False"

    return render_template("server.html")

@app.route("/client", methods=["POST", "GET"])
def client_page():
    global host_ip, port
    host_ip, port = "", 0
    if request.method == "POST":

        host_ip, port = str(request.form['ip']), int(request.form['port'])
        return render_template("client.html", video_url="/feed_client")
    return render_template("client.html", video_url="")


if __name__ == "__main__":
    app.run(debug=True, port=5048)