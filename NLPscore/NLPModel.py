#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, pickle, math
import pandas as pd
import numpy as np
from sklearn.naive_bayes import BernoulliNB
from sklearn.cross_validation import train_test_split
import nltk, os
from nltk import bigrams, trigrams
from nltk.tokenize import word_tokenize , RegexpTokenizer

BASE_DIR = os.path.dirname(__file__)




# r = requests.get('http://www.patientslikeme.com/forum/muscles_bones_joints/topics/102180?post_id=1577947#post-1577947')
# print r.text.encode(encoding='UTF-8',errors='ignore')

def removeNonAscii(s): return "".join(filter(lambda x: ord(x)<128, s))

class NLPModel:
  """docstring for NLPModel: for CS5555 project, build a helpfulness model to gauge helpfulness of unstructured text"""


  def __init__(self):
    # regexp to remove punctuation
    self.toker = RegexpTokenizer(r'((?<=[^\w\s])\w(?=[^\w\s])|(\W))+|\$?\d+(\.\d+)?%?', gaps=True)

    # stopwords prep from nltk
    self.stopwords = nltk.corpus.stopwords.words('english')

  def prepData(self):
    r = {}
    r['unigrams'] = []
    r['bigrams'] = []
    r['trigrams'] = []
    r['helpfulnessVotes'] = []


    # extract data from csv and extract uni and bigrams trigrams, tabulate them
    data = pd.read_csv('HealthProjectRawData.csv')
    # print a

    temp_data = []

    # remove unicode text
    for i in data.iterrows():
      temp_data.append(i[1][1])
      r['helpfulnessVotes'].append(i[1][0])

    data = temp_data

    # calc stats for helpfulnessVotes
    print 'calc stats for helpfulnessVotes:'
    print 'number of datapoints:', len(r['helpfulnessVotes'])
    print 'mean:', np.mean(r['helpfulnessVotes'])
    print 'median:', np.median(r['helpfulnessVotes'])

    self.topQ = np.percentile(r['helpfulnessVotes'],50)
    print 'top-quartile:', self.topQ

    self.bottomQ = np.percentile(r['helpfulnessVotes'],25)
    print 'bottom-quartile:', self.bottomQ



    # unigrams
    for i in data:
      # # remove punctuation
      # tokens = toker.tokenize(i)

      # # print i
      # # tokens = nltk.word_tokenize(i)
      
      # # replace with lowercase
      # tokens = [token.lower() for token in tokens if len(token) > 1] #same as unigrams

      

      # # keep the stopwords for bi and trigrams, otherwise they might not read naturally
      # bi_tokens = list(bigrams(tokens))
      # tri_tokens = list(trigrams(tokens))

      # # remove stopwords
      # tokens = [w.lower() for w in tokens if w.lower() not in stopwords]

      tokens, bi_tokens, tri_tokens = self.getngramsFromString(i)

      # load tokens to results:
      r['unigrams'].append(tokens)
      r['bigrams'].append(bi_tokens)
      r['trigrams'].append(tri_tokens)

    # print tokens, bi_tokens, tri_tokens
    # unigramFreq = nltk.FreqDist(tokens)
    # print 'FreqDist..... unigrams'
    # print unigramFreq.most_common(500)
    # print len(r['unigrams']), len(r['bigrams']),  r['helpfulnessVotes']


    self.data = r

  def findFreqDist(self):
    # extract popular unigrams
    popularUnigrams = []
    unpopularUnigrams = []

    popBigrams = []
    unpopBigrams = []

    popTrigrams = []
    unpopTrigrams = []

    for index, v in enumerate(self.data['helpfulnessVotes']):
      if v >= self.topQ:
        popularUnigrams.append(self.data['unigrams'][index])
        popBigrams.append(self.data['bigrams'][index])
        popTrigrams.append(self.data['trigrams'][index])
      elif v <= self.bottomQ:
        unpopularUnigrams.append(self.data['unigrams'][index])
        unpopBigrams.append(self.data['bigrams'][index])
        unpopTrigrams.append(self.data['trigrams'][index])

    # flatten and store freq dist to object
    self.popularUnigramFreq = nltk.FreqDist([word for post in popularUnigrams for word in post]) 
    self.unpopularUnigramFreq = nltk.FreqDist([word for post in unpopularUnigrams for word in post])

    self.popBigramFreq = nltk.FreqDist([word for post in popBigrams for word in post]) 
    self.unpopBigramFreq = nltk.FreqDist([word for post in unpopBigrams for word in post]) 

    self.popTrigramFreq = nltk.FreqDist([word for post in popTrigrams for word in post]) 
    self.unpopTrigramFreq = nltk.FreqDist([word for post in unpopTrigrams for word in post]) 

  def getngramsFromString(self, iStr):
    tokens = self.toker.tokenize(removeNonAscii(iStr) )

    # replace with lowercase
    tokens = [token.lower() for token in tokens if len(token) > 1] #same as unigrams

    

    # keep the stopwords for bi and trigrams, otherwise they might not read naturally
    bi_tokens = list(bigrams(tokens))
    tri_tokens = list(trigrams(tokens))

    # remove stopwords
    tokens = [w.lower() for w in tokens if w.lower() not in self.stopwords]
    return tokens, bi_tokens, tri_tokens

  def getVectorFromngrams(self, unigramInPost, bigramInPost, trigramInPost):
    unigramVec = []
    bigramVec = []
    trigramVec = []

    for u in self.unigramSet:
      if u in unigramInPost:
        unigramVec.append(1)
      else:
        unigramVec.append(0)

    for u in self.bigramSet:
      if u in bigramInPost:
        bigramVec.append(1)
      else:
        bigramVec.append(0)

    for u in self.trigramSet:
      if u in trigramInPost:
        trigramVec.append(1)
      else:
        trigramVec.append(0)

    return unigramVec + bigramVec + trigramVec

  def getVectorFromString(self, iStr):
    unigramInPost ,bigramInPost ,trigramInPost = self.getngramsFromString(iStr)
    return self.getVectorFromngrams(unigramInPost, bigramInPost, trigramInPost)

  def buildFeatureVector(self):
    print 'buiding feature Vectors...'
    featureCount = 500
 
    unigramSet = set()
    for i in self.popularUnigramFreq.most_common(featureCount):
     unigramSet.add(i[0])
    for i in self.unpopularUnigramFreq.most_common(featureCount):
     unigramSet.add(i[0])
    print 'unigramSet length:',len(unigramSet)

    bigramSet = set()
    for i in self.popBigramFreq.most_common(featureCount):
     bigramSet.add(i[0])
    for i in self.unpopBigramFreq.most_common(featureCount):
     bigramSet.add(i[0])
    print 'bigramSet length:',len(bigramSet)

    trigramSet = set()
    for i in self.popTrigramFreq.most_common(featureCount):
     trigramSet.add(i[0])
    for i in self.unpopTrigramFreq.most_common(featureCount):
     trigramSet.add(i[0])
    print 'trigramSet length:',len(trigramSet)

    self.unigramSet = unigramSet
    self.bigramSet = bigramSet
    self.trigramSet = trigramSet


    X = []
    Y = []
    for i, v in enumerate(self.data['helpfulnessVotes']):
      unigramInPost = self.data['unigrams'][i]
      bigramInPost = self.data['bigrams'][i]
      trigramInPost = self.data['trigrams'][i]

      X.append(self.getVectorFromngrams(unigramInPost, bigramInPost, trigramInPost) )

      if v >= self.topQ:
        Y.append(1)
      else:
        Y.append(0)

    print len(X), len(X[0])
    self.X = X
    self.Y = Y

  def useModel(self, iStr):
    trainedModel = pickle.load(open( BASE_DIR +'/trainedModel.p', 'rb'))
    clf = trainedModel['clf']
    self.unigramSet = trainedModel['unigramSet']
    self.bigramSet = trainedModel['bigramSet']
    self.trigramSet = trainedModel['trigramSet']

    log_probab = clf.predict_log_proba(self.getVectorFromString(iStr))
    print 'log_probab:', log_probab

    probab = clf.predict_proba(self.getVectorFromString(iStr))
    print 'probab:', probab

    prediction = clf.predict(self.getVectorFromString(iStr))
    print 'prediction:', prediction

    relativeScore = log_probab[0][1] - log_probab[0][0]
    # print 'relativeScore:', math.log(relativeScore)
    print 'relativeScore:', relativeScore

    return relativeScore




  def buildModel(self):
    X_train, X_test, Y_train, Y_test = train_test_split(self.X, self.Y, test_size=0.25, random_state=42)
    clf = BernoulliNB()
    clf.fit(X_train, Y_train)
    trainedModel = {
    'clf': clf,
    'unigramSet':self.unigramSet,
    'bigramSet': self.bigramSet,
    'trigramSet': self.trigramSet
    }

    # save model to pickle
    pickle.dump(trainedModel, open( BASE_DIR +'/trainedModel.p', 'wb'))


    print 'model score:',clf.score(X_test, Y_test)


def runExamples():

  a = NLPModel()


  print 'poor example with no thought at all:',a.useModel("i don't understand RA I'm sad.")
  print 'slightly better example with added keywords:',a.useModel("i don't chronic pain understand RA I've sadden the pain like emotion my husband love.")
  
  print 'example from arthritis.org:'
  istr = """ Rheumatoid Arthritis
Rheumatoid arthritis (RA) is an autoimmune disease in which your body’s immune system – which protects your health by attacking foreign substances like bacteria and viruses – mistakenly attacks your joints. The abnormal immune response causes inflammation that can damage joints and organs, such as the heart. Early diagnosis and prompt treatment is the key to preventing joint destruction and organ damage.

People
About 1.5 million people in the United States have rheumatoid arthritis (RA). Nearly three times as many women have the disease as men. In women, RA most commonly begins between ages 30 and 60. In men, it often occurs later in life.

Symptoms
The severity of the disease can vary from person to person. Symptoms can change from day to day. Sudden increases in symptoms and illness are called flares. A flare can last for days or months. Key rheumatoid arthritis symptoms are pain, fatigue and warm, swollen, reddish joints. Long periods of joint stiffness in the morning are common. Inflammation in the small joints of the wrist and hand is typical. If a joint on one side of the body is affected, the same one on the other side is usually affected, too.

Treatment
There is no cure for RA, but there are a number of medications available to help ease symptoms, reduce inflammation, and slow the progression of the disease. No one drug works for everyone but many people find treatments that are very effective. The goal of treatment is remission, a state when inflammation is gone or is very low. A doctor, likely a rheumatologist – a specialty doctor who treats people with arthritis – should monitor your levels of disease activity, or inflammation, on a regular basis through exams and blood tests that reveal how well treatment is working. The doctor may add or change your medications or adjust the dosage after a few months, if the disease is still active. 

Self-care
Self-management is an important part of rheumatoid arthritis care. Staying physically active is the key to keeping joints flexible. Too little movement can lead to joint stiffness. Strong muscles protect joints. Overall fitness improves health in many ways. Managing your weight, eating a nutritious diet and getting a good balance of rest and activity each day are important, too.

What to Do
If you think you might have rheumatoid arthritis - Find out when to see a doctor. """

#     istr = """ I know some of you may have seen this before but I'm reposting it for those who havent. Its a great resource to copy and print to give to friends or family.

# A Letter to the Normal’s from a Person With Severe Chronic Pain"

# Having chronic pain means many things change, and a lot of them are invisible. Unlike having cancer or being hurt in an accident, most people do not understand even a little about chronic pain and its effects, and of those that think they know, many are actually misinformed. 

# In the spirit of informing those who wish to understand: These are the things that I would like you to understand about me before you judge me.

# Please understand that being sick doesn't mean I'm not still a human being. I have to spend most of my day in considerable pain and exhaustion, and if you visit, sometimes I probably don't seem like much fun to be with, but I'm still me, stuck inside this body. I still worry about work, my family, my friends, and most of the time, I'd still like to hear you talk about yours, too.

# Please understand the difference between "happy" and "healthy". When you've got the flu, you probably feel miserable with it, but I've been sick for years. I can't be miserable all the time. In fact, I work hard at not being miserable. So, if you're talking to me and I sound happy, it means I'm happy. that's all. It doesn't mean that I'm not in a lot of pain, or extremely tired, or that I'm getting better, or any of those things. Please don't say, "Oh, you're sounding better!" or "But you look so healthy!" I am merely coping. I am sounding happy and trying to look normal. If you want to comment on that, you're welcome.




#  """

  print a.useModel(istr)


  print 'example from wiki:'
  istr = """ Rheumatoid arthritis (RA) is a chronic, systemic inflammatory disorder that primarily affects joints.[1] It may result in deformed and painful joints, which can lead to loss of function. The disease may also have signs and symptoms in organs other than joints.
The cause of RA is not completely understood. The process involves an inflammatory and fibrosis of the capsule around the joints. It also affects the underlying bone and cartilage.[1] RA can produce diffuse inflammation in the lungs, the membrane around the heart, the membranes of the lung, and whites of the eye. It can also produce nodular lesions, most common within the skin. It is a clinical diagnosis made mostly on the basis of symptoms and physical examination. X-rays, laboratory testing, and synovial fluid analysis might help support a diagnosis or exclude other diseases with similar symptoms.[2]
Treatments include both medication and non-pharmacological measures - the goal being to control joint inflammation and prevent joint damage and disability. Non-pharmacological treatment includes physical therapy, splints and braces, occupational therapy and dietary changes but these do not stop the progression of joint destruction. Painkillers and anti-inflammatory drugs, including steroids, suppress symptoms, but do not stop the progression either. Disease-modifying antirheumatic drugs (DMARDs) may slow or halt the progress of the disease.[2] Biological DMARDS like anti-TNF agents are effective but usually avoided in persons with active disease or hypersensitivity to these agent.[3] They have been shown to decrease the number of tender or swollen joints and the pain and disability due to the disease but there is little data about side effects.[4] Alternative medicine is not supported by evidence.[5][6][7]
RA affects between 0.5 and 1 of adults in the developed world with between 5 and 50 per 100,000 people newly developing the condition each year.[8] Onset is most frequent during middle age, but people of any age can be affected.[9] In 2013 it resulted in 38,000 deaths up from 28,000 deaths in 1990.[10] The name is based on the term "rheumatic fever", an illness which includes joint pain and is derived from the Greek word ῥεύμα-rheuma (nom.), ῥεύματος-rheumatos (gen.) ("flow, current"). The suffix -oid ("resembling") gives the translation as joint inflammation that resembles rheumatic fever. The first recognized description of RA was made in 1800 by Dr. Augustin Jacob Landré-Beauvais (1772–1840) of Paris.[11] """
  print a.useModel(istr)

  print 'example from PubMed:'
  istr = """ 
  About RA
Rheumatoid arthritis (RA) is a disease that causes pain, swelling, and stiffness in the joints. In some people, it can also cause the joints to become damaged and deformed.

Although it can affect any joint in the body, RA is most commonly found in the hands, wrists, feet, and knees. Usually, if it is found in one hand, it will appear in the other as well.
Sometimes RA can cause problems with body parts other than your joints such as your heart, lungs, eyes, or mouth.
RA usually lasts many years or an entire lifetime. For some people, RA can last for only a few months to a few years with treatment, although this is rare.
The symptoms of RA (pain, swelling, stiffness) can get worse for some periods of time (called a "flareup") and then get better for some periods of time.
What causes RA?

The cause of RA is unknown, but researchers think the condition may be passed down in families. The pain and symptoms of RA happen when your immune system (the system of the body that helps defend you from germs) attacks the healthy lining of your joints. Doctors are not sure why the immune system in some people attacks their joints...
 """

  print a.useModel(istr)

  print 'example from academic paper:'
  istr = """ 
  Over the last 2 decades, the treatment of patients with rheumatoid arthritis (RA) has changed considerably. Currently, the goal of therapy is not only symptom relief, but in particular the prevention of long-term structural damage and functional decline. To this end, an increasing number of effective disease-modifying antirheumatic drugs (DMARDs) as well as biologic agents have been developed and have demonstrated clinical value in randomized clinical trials. It has become clear that treatment should start early and must be maintained without interruption to reduce the occurrence of irreversible joint damage (1–8). Furthermore, several combinations of DMARDs as well as tumor necrosis factor (TNF) antagonists have shown superiority to DMARD monotherapy in patients with early (9–17) and longstanding (18–22) RA. Finally, intensive monitoring of disease activity and adjusting DMARD use accordingly has resulted in improved outcomes (23). However, the increase in therapeutic options has left unanswered the question of what the optimal therapeutic strategy is in patients presenting with RA.

The BeSt (Dutch acronym for Behandel-Strategieën, “treatment strategies”) study is a multicenter, randomized clinical trial in which we compared the clinical and radiographic outcomes of 4 different treatment strategies: sequential monotherapy (group 1), step-up combination therapy (group 2), initial combination therapy with tapered high-dose prednisone (group 3), and initial combination therapy with the TNF antagonist infliximab (group 4). The common goal in all strategies was to reduce disease activity rapidly and persistently by tight monitoring and immediate adjustment of therapy in the case of an insufficient response. Here we present the results of the first year of followup.
 """

  print a.useModel(istr)



if __name__ == '__main__':
  a = NLPModel()
  a.prepData()
  # print a.data['unigrams'][0]

  a.findFreqDist()

  print 'popular unigram freq'
  print a.popularUnigramFreq.most_common(500)

  print 'unpopular unigram freq'
  print a.unpopularUnigramFreq.most_common(500)

  print 'popular bigram freq'
  print a.popBigramFreq.most_common(500)

  print 'unpopular bigram freq'
  print a.unpopBigramFreq.most_common(500)

  print 'popular trigram freq'
  print a.popTrigramFreq.most_common(500)

  print 'unpopular trigram freq'
  print a.unpopTrigramFreq.most_common(500)

  # a.buildFeatureVector()

  # a.buildModel()

  a.useModel('poo')
  runExamples()


