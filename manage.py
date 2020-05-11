#!/usr/bin/env python
import os
import sys
import pandas as pd
import wordcloud
from math import pi
import datetime as dt
from forms import videoForm
from flask_cors import CORS
from flask_table import Table, Col
from flask import Flask, render_template,redirect,request,url_for
from youtube_transcript_api import YouTubeTranscriptApi
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords


app = Flask(__name__)
CORS(app, resources={r"/": {"origins": "https://cdn.bokeh.org/bokeh/release/bokeh-2.0.0.min.js"}})
app.config['SECRET_KEY'] = '3791528bx0e45ce9c602dgde210bs329'
nltk.download('stopwords')
nltk.download('punkt')

def gen_word_cloud(text):   
    sw = stopwords.words('english')
    sencenteces = text.replace("\n", " ")
    words = nltk.tokenize.word_tokenize(sencenteces)
    vocab = nltk.FreqDist(words)
    #mc = sorted([w for w in vocab.most_common(80) if len(w[0]) > 4] , key=lambda x: x[1], reverse=True)
    fig = plt.figure()
    wcloud = wordcloud.WordCloud(width = 300, height = 300, background_color ='black', 
                    stopwords = sw, min_font_size = 10,colormap = "autumn",normalize_plurals  = True).generate(sencenteces)
    plt.figure(figsize = (24, 24), facecolor = None) 
    plt.imshow(wcloud) 
    plt.savefig("static/word_cloud.png")
    plt.close(fig)
            
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = videoForm(video="https://youtu.be/ARDqw9AWQ3k")
    if form.validate_on_submit():
        video_url = form.video.data
        if ("youtu.be" in video_url):          
            vid_id = video_url.split("/")[-1]
        elif ("www.youtube.com" in video_url):
            vid_id = video_url.split("t=")[0].split("=")[-1]
        else:
            vid_id = None
            return render_template('results.html', data="Did not find data for this video")
        try:
            transcript = YouTubeTranscriptApi.get_transcript(vid_id)
            text = [x['text'] for x in transcript if 'text' in x]
            text = [x.replace("[Music]","") for x in text]
            text = [x.replace("[MUSIC PLAYING]","") for x in text]
            text = "\n".join(text)
            #text = "you suck"
        except Exception as e:
            text ="Did not find data for this video\n{}".format(e)
        gen_word_cloud(text)
        return render_template('results.html', data=text)
    return render_template("base.html",form= form)

if __name__ == "__main__":
    app.run(debug=True,port=8000)