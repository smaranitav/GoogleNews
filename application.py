from flask import Flask, jsonify, request
from flask_cors import CORS
from newsapi import NewsApiClient
from collections import Counter
import json

# create the application object
application = Flask(__name__)
CORS(application)

@application.route('/index', methods=['GET', 'POST'])
def news():
    
    newsapi = NewsApiClient(api_key='546efd0c61864b23969558f0dd4cd2ed')

    news_dictionary=dict()
    news_dictionary["general_headlines"]= newsapi.get_top_headlines(
                                            language='en',
                                            country='us',
                                            page_size=30)
    
    news_dictionary["specific_cnn_news"]= newsapi.get_top_headlines(
                                          sources='cnn',
                                          language='en',
                                          page_size=30)
    news_dictionary["specific_fox_news"] = newsapi.get_top_headlines(
                                          sources='fox-news',
                                          language='en',
                                          page_size=30)
    
    #word cloud
    # get all titles
    titles=[]
    articles=news_dictionary["general_headlines"]["articles"]
    for i in range(len(articles)):
        titles.append(articles[i]["title"])
    #print(titles)

    stop_words=[]
    file_ptr =open("stopwords_en.txt","r")
    for line in file_ptr:
        #print(line)
        stop_words.append(line[:-1])

    #print(stop_words)

    all_words=[]
    # get all words in title
    for i in range(len(titles)):
        words=titles[i].split(' ')
        for word in words:
            transformed_word=''.join(letter for letter in word if letter.isalnum())
            if len(transformed_word)==0:
                all_words.append(word)
            if len(transformed_word)>0:
                if transformed_word.lower() not in stop_words:
                    all_words.append(transformed_word)
    
    count_dic=Counter(all_words)
    sorted_dic=dict(sorted(count_dic.items(), key=lambda x:x[1], reverse=True))
    count_of_words=0
    size_of_words=30
    word_cloud_list=[]#list of dictionaries
    for k,v in sorted_dic.items():
        word_cloud_dic={}
        if count_of_words>29:
            break
        word_cloud_dic["word"]=k
        word_cloud_dic["size"]=size_of_words
        size_of_words=size_of_words-0.8
        word_cloud_list.append(word_cloud_dic)
        count_of_words=count_of_words+1
        #print(k,v)

    news_dictionary["word_cloud"]=word_cloud_list

    return jsonify(news_dictionary)

@application.route('/search', methods=['GET','POST'])
def getSourcesForCategory():
    newsapi = NewsApiClient(api_key='546efd0c61864b23969558f0dd4cd2ed')
    news_sources={}
    if request.args.get('category'):
        category=request.args.get('category')
    
        news_sources=newsapi.get_sources(category=category, language="en", country="us")
    else:
        news_sources=newsapi.get_sources(language="en", country="us")
    
    return jsonify(news_sources)

@application.route('/everything',methods=['GET','POST'])
def getFormData():
    newsapi = NewsApiClient(api_key='546efd0c61864b23969558f0dd4cd2ed')
    query_keyword=request.args.get('q')

    from_date=request.args.get('from_date')
    to_date=request.args.get('to_date')
    source_news=request.args.get('source_news')

    if(source_news=="all"):
        source_news=None
    
    json_dic={}

    try:
        data=newsapi.get_everything(q=query_keyword, sources=source_news, from_param=from_date, to=to_date,
            language="en", sort_by="publishedAt", page_size=30 )
        json_dic["data"]=data
        return jsonify(json_dic)
    
    except Exception as e:
        #print("ERROR")
        #print(e.args[0])
        json_dic["error_data"]=e.args[0]
        return jsonify(json_dic)
    
@application.route('/')
def getAll():
    return application.send_static_file('index.html')

if __name__ == '__main__':
    application.run(debug=True)