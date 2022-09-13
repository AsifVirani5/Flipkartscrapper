from flask import Flask, request, render_template
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pandas as pd



app = Flask(__name__)

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    # return 'this is the help'
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        searchString = request.form['content'].replace(" ", "")
        flipkart_URL = "https://www.flipkart.com/search?q=" + searchString
        uClient = uReq(flipkart_URL)
        flipkartPage = uClient.read()
        uClient.close()
        flipkart_html = bs(flipkartPage, "html.parser")
        bigboxes = flipkart_html.find_all('div', {"class": "_1AtVbE col-12-12"})
        box = bigboxes[5]
        productLink = "https://www.flipkart.com" + box.div.a['href']
        prodRes = requests.get(productLink)
        prodRes.encoding = 'utf-8'
        prod_html = bs(prodRes.text, "html.parser")
        all_review = prod_html.find_all('div', {"class": "_16PBlm"})
        reviews = []
        for i in range(len(all_review) - 1):
            try:
                Customer_comment = all_review[i].find('p', {"class": "_2-N8zT"}).text
            except:
                Customer_comment = 'No comment found'

            try:
                Customer_rating = all_review[i].div.div.div.div.text
            except:
                Customer_rating = 'No rating found'
            try:
                Customer_full_comment = all_review[i].div.div.text
            except:
                Customer_full_comment = 'No comment found'
            try:
                Customer_location = all_review[i].find('p', {'class': '_2mcZGG'}).text.split()[2]
            except:
                Customer_location = 'No location found'

            try:
                Customer_name = all_review[i].find('p', {'class': "_2sc7ZR _2V5EHH"}).text
            except:
                Customer_name = 'No Name found'

            mydict = {"Customer_comment": Customer_comment, "Customer_rating": Customer_rating,
                      "Customer_full_comment": Customer_full_comment, "Customer_location": Customer_location,
                      "Customer_name": Customer_name}
            reviews.append(mydict)
            df = pd.DataFrame(reviews)
            columns = list(df.columns)
            reviews1 = [[df.loc[i, col] for col in df.columns] for i in range(len(df))]
        return render_template('result.html', titles=columns, rows=reviews1)
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(port=5007)

