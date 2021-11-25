import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize


inputFile = 'cik_list.csv'
outputFile = 'output_2021_10_23.csv'
masterDictionaryFile = 'LoughranMcDonald_MasterDictionary_2018.csv'
stopWordsFile = 'StopWords_Generic.txt'
uncertainityDictFile = 'uncertainty_dictionary.csv'
constrainingDictFile = 'constraining_dictionary.csv'

baseUrl = 'https://www.sec.gov/Archives/'

def read_csv(inputFile):
    csv_file = pd.read_csv(inputFile)
    links = [baseUrl+x for x in csv_file['SECFNAME']]

    return csv_file, links


def generate_metrics(url_list, positiveWordList, negativeWordList, uncertainityWordList, constrainingWordList):
    # print(url_list)
    headers = {
        "User-Agent": "mchinmayee@gmail.com",
        "Accept-Encoding": "gzip, deflate",
        "Host": "www.sec.gov"
    }

    resultDict = {
        'positive_score':[],
        'negative_score':[],
        'polarity_score':[],
        'average_sentence_length':[],
        'percentage_of_complex_words':[],
        'fog_index':[],
        'complex_word_count':[],
        'word_count':[],
        'uncertainty_score':[],
        'constraining_score':[],
        'positive_word_proportion':[],
        'negative_word_proportion':[],
        'uncertainty_word_proportion':[],
        'constraining_word_proportion':[],
        'constraining_words_whole_report':[],
    }

    # readCount = 0
    for dataUrl in url_list:
        # read data
        print('reading URL: {}'.format(dataUrl))
        request_url = requests.get(dataUrl, headers=headers)
        data = request_url.content
        ##1: HTML string from the website; ‘r.content’
        #2: What HTML parser to use; ‘html5lib’
        soup = BeautifulSoup(data,'html5lib')
        reportText = soup.get_text()

        # print(reportText)

        reportWordList = tokenize(reportText)
        reportWordList = [w.upper() for w in reportWordList]

        # word_count	
        wordCount = len(reportWordList)

        # positive_score and negative_score	
        positiveScore = count_words_in_given_list(positiveWordList, reportWordList)
        negativeScore = count_words_in_given_list(negativeWordList, reportWordList)

        # polarity_score	
        polarityScore = polarity_score(positiveScore, negativeScore)

        # average_sentence_length	
        averageSentenceLen = calculate_agv_sentence_len(reportText, reportWordList)

        # complex_word_count
        complexWordCount = complex_word_count(reportWordList) 
        # percentage_of_complex_words	
        complexWordPercent = complexWordCount / wordCount * 100

        # fog_index		
        fogIndex = calculate_fog_index(averageSentenceLen, complexWordPercent)
        # 
        # uncertainty_score	
        uncertainityScore = count_words_in_given_list(uncertainityWordList, reportWordList)

        # constraining_score	
        constrainingScore = count_words_in_given_list(constrainingWordList, reportWordList)
        
        # positive_word_proportion	
        positiveWordProportion = positiveScore / wordCount

        # negative_word_proportion	
        negativeWordProportion = negativeScore / wordCount
        
        # uncertainty_word_proportion	
        uncertainityWordProportion = uncertainityScore / wordCount

        # constraining_word_proportion	
        constrainingWordProportion = constrainingScore / wordCount

        # constraining_words_whole_report
        constrainingWordsWholeReport = constrainingScore


        # save the metrics
        resultDict['positive_score'].append(positiveScore)
        resultDict['negative_score'].append(negativeScore)
        resultDict['polarity_score'].append(polarityScore)
        resultDict['average_sentence_length'].append(averageSentenceLen)
        resultDict['percentage_of_complex_words'].append(complexWordPercent)
        resultDict['fog_index'].append(fogIndex)
        resultDict['complex_word_count'].append(complexWordCount)
        resultDict['word_count'].append(wordCount)
        resultDict['uncertainty_score'].append(uncertainityScore)
        resultDict['constraining_score'].append(constrainingScore)
        resultDict['positive_word_proportion'].append(positiveWordProportion)
        resultDict['negative_word_proportion'].append(negativeWordProportion)
        resultDict['uncertainty_word_proportion'].append(uncertainityWordProportion)
        resultDict['constraining_word_proportion'].append(constrainingWordProportion)
        resultDict['constraining_words_whole_report'].append(constrainingWordsWholeReport)

        # readCount += 1

        # if readCount == 1:
        #     break

    
    return resultDict

def count_words_in_given_list(dictionary_words, words):
    score = 0
    # print('WORD DICT: {}'.format(dictionary_words))
    for word in words:
        # print('comparing: {}'.format(word))
        if word in dictionary_words:
            score += 1
    return score

'''
Generate global variables
'''
def generate_positive_negative_word_list():
    master_dic = pd.read_csv(masterDictionaryFile)

    positive_dictionary = [x for x in master_dic[master_dic['Positive'] != 0]['Word']] #354
    negative_dictionary = [x for x in master_dic[master_dic['Negative'] != 0]['Word']]  # 2355

    return positive_dictionary, negative_dictionary

def generate_uncertainity_word_list():
    uncertainty_file = pd.read_csv(uncertainityDictFile)

    return [ words for words in uncertainty_file['Word']]

def generate_constraining_word_list():
    uncertainty_file = pd.read_csv(constrainingDictFile)

    return [ words for words in uncertainty_file['Word']]

'''
Helper functions
'''

def tokenize(text):
    text = re.sub(r'[^A-Za-z]',' ',text.upper())
    tokenized_words = word_tokenize(text)

    return tokenized_words


def complex_word_count(words):
    complexWordCount = 0
    complex_wordList=[]
    for word in words:
        vowels=0
        word = word.lower()
        if not word.endswith(('es','ed')):
           
            for w in word:
                if w in ['a','e','i','o','u']:
                    vowels += 1
            if(vowels > 2):
                complexWordCount += 1
                complex_wordList.append(word)
                
    # print(complex_wordList)            
    return complexWordCount

def fog_index_cal(average_sentence_length, percentage_complexwords):
    return 0.4*(average_sentence_length + percentage_complexwords)

def calculate_agv_sentence_len(reportTxt, words):
    sentences = sent_tokenize(reportTxt)
    num_sentences = len(sentences)
    average_sentence_length = len(words)/num_sentences

    return average_sentence_length

def calculate_fog_index(average_sentence_length, percentage_complexwords):
    return 0.4*(average_sentence_length + percentage_complexwords)

def polarity_score(positive_score, negative_score):
     return (positive_score - negative_score)/((positive_score + negative_score)+ 0.000001)

def main():
    positiveWordList, negativeWordList = generate_positive_negative_word_list()
    uncertainityWordList = generate_uncertainity_word_list()
    constrainingWordList = generate_constraining_word_list()

    df, urlList = read_csv(inputFile)
    metricsDict = generate_metrics(urlList, positiveWordList, negativeWordList, uncertainityWordList, constrainingWordList)

    print('MertricsDict : {}'.format(metricsDict))

    # df = df.drop( df.index.to_list()[1:] ,axis = 0 )
    # print(df)
    for metricName in metricsDict:
        df[metricName] = metricsDict[metricName]

    df.to_csv(outputFile)
    

main()