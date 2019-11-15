# -*- coding: utf-8 -*-
import pandas as pd
from flask import Flask, render_template, request, Response, send_file
import os
import numpy as np
import sys

def generate_statistics(new_df, all_name_of_input_writer):  #This function count how many time each pen name for the author occur in title and full text
    temp_df = new_df
    temp_df.insert(temp_df.shape[1], 'Number of times being metioned in title', np.nan)
    temp_df.insert(temp_df.shape[1], 'Number of times being mentioned in the fulltext', np.nan)
    full_count_in_title = {}
    full_count_in_text = {}
    for element in all_name_of_input_writer:
        full_count_in_title[element] = 0
        full_count_in_text[element] = 0
    for i in range(0, temp_df.shape[0]): 
        title_count_match_for_each_name = {}
        full_text_count_match_for_each_name = {}
        title = temp_df.iloc[i]['Title']
        full_text = temp_df.iloc[i]['Fulltext']
        if str(title) == 'nan':
            title = ' '
        if str(full_text) == 'nan':
            full_text = ' '
        for element in all_name_of_input_writer:
            title_count_match_for_each_name[element] = title.count(element) 
            full_text_count_match_for_each_name[element] = full_text.count(element)
            full_count_in_title[element] += title.count(element)
            full_count_in_text[element] += full_text.count(element)
        title_count_match_for_each_name = {x:y for x,y in title_count_match_for_each_name.items() if y!=0}
        full_text_count_match_for_each_name = {x:y for x,y in full_text_count_match_for_each_name.items() if y!=0}
        res = bool(title_count_match_for_each_name)
        if res == True: 
            string_for_title_count = ''
            for key in title_count_match_for_each_name:
                string_for_title_count = string_for_title_count + key + ' : ' + str(title_count_match_for_each_name[key]) + ';;;'
            temp_df['Number of times being metioned in title'][i] = string_for_title_count
        res = bool(full_text_count_match_for_each_name)
        if res == True: 
            string_for_content_count = ''
            for key in full_text_count_match_for_each_name:
                string_for_content_count = string_for_content_count + key + ' : ' + str(full_text_count_match_for_each_name[key]) + ';;;'
            temp_df['Number of times being mentioned in the fulltext'][i] = string_for_content_count
    number_of_articles = temp_df.shape[0]
    full_count_in_title_str, full_count_in_text_str = '',''
    for key in full_count_in_title:
        full_count_in_title_str = full_count_in_title_str + key + ' : ' + str(full_count_in_title[key]) + ' ; '
        full_count_in_text_str = full_count_in_text_str + key + ' : ' + str(full_count_in_text[key]) + ' ; '
    full_count_in_title_str = full_count_in_title_str[:-3]
    full_count_in_text_str = full_count_in_text_str[:-3]
    return temp_df, number_of_articles, full_count_in_title_str, full_count_in_text_str



def generating_combined_result_file(input_get_statistics, search_field, data, name_list): #This function combine the result for each pen name for the author into one dataframe
    list_for_name_and_frequency = []
    df = pd.DataFrame()
    for each_name in name_list:
        if search_field == 'author':
            temp_df = data[data["Creator"].str.contains(each_name, na = False)]
        elif search_field == 'content':
            temp_df = data[~(data["Creator"].str.contains(each_name, na = False)) & ((data["Title"].str.contains(each_name, na = False)) | (data["Fulltext"].str.contains(each_name, na = False)))]
        list_for_name_and_frequency.append(each_name + ' : ' + str(temp_df.shape[0])) 
        df = pd.concat([df,temp_df])
    df = df.reset_index()
    if input_get_statistics == "T":
        df,number_of_articles,mention_in_title,mention_in_fulltext = generate_statistics(df, name_list)  
    elif input_get_statistics == "F":
        number_of_articles,mention_in_title,mention_in_fulltext = '','',''
    return df,number_of_articles,mention_in_title,mention_in_fulltext


def check_name(name_str): #This function check the pen name for the input author name
    name_list = []
    name_list.append(name_str)
    for i in range(0,author_data.shape[0]):
        temp_name_list = list(set(author_data.iloc[i]['Be Known as ':]))
        temp_name_list = [str(x) for x in temp_name_list if str(x) != 'nan' and not str(x).isspace() and str(x)!='same as column 1']    
        if name_str in temp_name_list:
            name_list = name_list + temp_name_list
    name_list = list(set(name_list))
    return name_list


def get_result_for_creator_name(data,name): 
    df = data[data["Creator"].str.contains(name, na = False)]
    df = df.reset_index()
    return df


def get_result_for_content(data,name):
    df = data[~(data["Creator"].str.contains(name, na = False)) & ((data["Title"].str.contains(name, na = False)) | (data["Fulltext"].str.contains(name, na = False)))]
    df = df.reset_index()
    return df

app = Flask(__name__,static_folder='./static')
pd.set_option('display.max_colwidth', -1)
data = pd.read_csv('https://storage.googleapis.com/search-tool-259006.appspot.com/WeeklyAllTextCleaned-utf8.csv')
author_data = pd.read_csv('https://raw.githubusercontent.com/joe608939/test/master/(Draft)%20HKLit%20Author%20list%202019_v.6_20190920.csv')


methods = ''
@app.route("/",methods = ['GET','POST'])                  
def search_page():  
    if request.method == 'POST':
        name = request.form['author_name']
        search_field = request.form['search_field']
        get_stat = request.form['get_stat']
        result = get_result_for_title(data,name)
        return render_template('result.html',  tables=[result.to_html(classes='data')], titles=result.columns.values)

    return render_template('ask_for_input.html')     

@app.route("/send",methods = ['GET','POST'])                 
def print_result():  
    reminder_to_user = ''
    if request.method == 'POST':
        name = request.form['author_name']              #Get the datafrom user input
        search_field = request.form['search_field']
        get_stat = request.form['get_stat']
        get_name_list = request.form['get_name_list']
        separte_name = request.form['separte_name']
        input_name = name
        if get_name_list =='F':            #Check if we have to generate the result for the pen name of the author
            reminder_to_user = reminder_to_user + 'We only search for the enter name. '
            name_list = []
            name_list.append(name)
        elif get_name_list == 'T':
            reminder_to_user = reminder_to_user + 'We also search for the pen name. '
            name_list = check_name(name)
        dataframe_collection = {}     
        number_of_articles_collection = {}
        mention_in_title_collection = {}
        mention_in_fulltext_collection = {}
        if search_field == 'author':      #See whether the user want to search in the field creator or in the title and fulltext
            reminder_to_user = reminder_to_user + 'Search in the filed creator. '
            if separte_name =='T':    
                reminder_to_user = reminder_to_user + 'Separte the result for each name. '
                if get_stat == 'T':
                    reminder_to_user = reminder_to_user + 'Generate count. '
                elif get_stat == 'F':
                    reminder_to_user = reminder_to_user + 'Do not generate count. ' 
                for name in name_list:
                    result = get_result_for_creator_name(data,name)
                    if get_stat == 'T':
                        result, number_of_articles, mention_in_title, mention_in_fulltext = generate_statistics(result,name_list)
                    else:
                        number_of_articles, mention_in_title, mention_in_fulltext =  '','',''
                    dataframe_collection[name] = result
                    number_of_articles_collection[name] = number_of_articles
                    mention_in_title_collection[name] = mention_in_title
                    mention_in_fulltext_collection[name] = mention_in_fulltext
            elif separte_name =='F':           #See whether the user want to search in the field creator or in the title and fulltext
                reminder_to_user = reminder_to_user +  'Do not separte the result for each name. '
                if get_stat == 'T':
                    reminder_to_user = reminder_to_user + 'Generate count. '
                elif get_stat == 'F':
                    reminder_to_user = reminder_to_user + 'Do not generate count. ' 
                result,number_of_articles,mention_in_title,mention_in_fulltext = generating_combined_result_file(get_stat, search_field, data, name_list)
                dataframe_collection[name] = result
                number_of_articles_collection[name] = number_of_articles
                mention_in_title_collection[name] = mention_in_title
                mention_in_fulltext_collection[name] = mention_in_fulltext
        elif search_field == 'content':
            reminder_to_user = reminder_to_user + 'Search in the field Title and Full Text. '
            if separte_name == 'T':
                reminder_to_user = reminder_to_user + 'Separte the result for each name. '
                if get_stat == 'T':
                    reminder_to_user = reminder_to_user + 'Generate count. '
                elif get_stat == 'F':
                    reminder_to_user = reminder_to_user + '<br>Do not generate count. '                  
                for name in name_list:
                    result = get_result_for_content(data,name)
                    if get_stat == 'T':
                        result,number_of_articles,mention_in_title,mention_in_fulltext = generate_statistics(result,name_list)            
                    elif get_stat == 'F':
                        number_of_articles, mention_in_title, mention_in_fulltext =  '','',''
                    dataframe_collection[name] = result
                    number_of_articles_collection[name] = number_of_articles
                    mention_in_title_collection[name] = mention_in_title
                    mention_in_fulltext_collection[name] = mention_in_fulltext
            elif separte_name =='F':
                reminder_to_user = reminder_to_user + 'Do not separte the result for each name. '
                if get_stat == 'T':
                    reminder_to_user = reminder_to_user + 'Generate count. '
                elif get_stat == 'F':
                    reminder_to_user = reminder_to_user + 'Do not generate count. ' 
                result,number_of_articles,mention_in_title,mention_in_fulltext = generating_combined_result_file(get_stat, search_field, data, name_list)
                dataframe_collection[name] = result
                number_of_articles_collection[name] = number_of_articles
                mention_in_title_collection[name] = mention_in_title
                mention_in_fulltext_collection[name] = mention_in_fulltext
        all_name_str = ','.join(name_list)
        return render_template('result.html',dataframe_collection = dataframe_collection,number_of_articles = number_of_articles_collection, mention_in_title = mention_in_title_collection, mention_in_fulltext = mention_in_fulltext_collection,get_stat = get_stat, all_name_str = all_name_str, author_name = input_name, reminder_to_user = reminder_to_user, separte_name = separte_name , name_list = name_list, field = search_field) 

@app.route("/<name>/<field>/<separte_name>")
def download_csv(name,field,separte_name):
    df = pd.DataFrame()
    if separte_name == 'T':
        if field == 'content':
            df = get_result_for_content(data,name)
        elif field == 'author':
            df = get_result_for_creator_name(data,name)
    elif separte_name == 'F':
        name_list = check_name(name)
        df = pd.DataFrame()
        if field == 'content':
            for each_name in name_list:
                temp_df = get_result_for_content(data,each_name)
                df = pd.concat([df,temp_df])
        elif field == 'author':
            for each_name in name_list:
                temp_df = get_result_for_creator_name(data,each_name)
                df = pd.concat([df,temp_df])            
    csv = df.to_csv('%s_%s.csv'%(name,field), index = None, header = True, encoding='utf-8-sig')
    return send_file('%s_%s.csv'%(name,field),
                     mimetype='text/csv',
                     attachment_filename='%s_%s.csv'%(name,field),
                     as_attachment=True)
    os.remove('%s_%s.csv'%(name,field))

if __name__ == "__main__":        # on running python app.py
    app.run()           





