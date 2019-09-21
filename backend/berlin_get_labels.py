import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
from sklearn import metrics

from imblearn.over_sampling import RandomOverSampler

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences

from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder

import re
from translate import Translator
import requests
import json

from geopy.geocoders import Nominatim

def getPrediction():
  listingsdf = pd.read_csv("listings_summary.csv", engine="python", encoding='utf-8', error_bad_lines=False)
  labelleddf = listingsdf[['latitude','longitude','review_scores_location', 'review_scores_value', 'review_scores_rating']]
  labelleddf['label'] = labelleddf['review_scores_rating'].apply(lambda x: goodOrBad(float(x)))
  lat = labelleddf['latitude'].astype(str)
  long = labelleddf['longitude'].astype(str)
  labelleddf['lat_and_long'] = "("+lat + "," + long+")"

  labelleddf = labelleddf.dropna(axis=0)

  X = labelleddf.iloc[:, 0:2]
  Y = labelleddf.iloc[:,5]

  rus = RandomOverSampler(random_state=0)
  X_resampled, Y_resampled = rus.fit_resample(X, Y)


  X = X_resampled
  Y = Y_resampled

  classifier = createModel(25)

  #Split data
  X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = 0.2, random_state = 0)

  trainModel(classifier, X_train, Y_train)

  predictClasses(classifier, X_test, Y_test)

  prediction = predictPlace("Gendarmenmarkt", classifier)

  classifyNeighbourhoods("location_info.csv", classifier)

  return prediction


#label the data as good or bad 
def goodOrBad(score):
  if score >= 80.0:
    return 1
  else:
    return 0

#create and train the KNN model
def createModel(n):
  classifier = KNeighborsClassifier(n_neighbors = n, metric = 'minkowski', p = 2)
  return classifier 

#train the data 
def trainModel(classifier, X_train, Y_train):
  classifier.fit(X_train, Y_train)

# Predict 
def predictClasses(classifier, X_test, Y_test):
  Y_pred = classifier.predict(X_test)
  print("Accuracy:\n%s" % metrics.accuracy_score(Y_test, Y_pred))
  
#classify the neighbourhoods
def classifyNeighbourhoods(filename, classifier):
  neighbourhoods = pd.read_csv(filename)
  neighbourhoods.head()

  nX = neighbourhoods.iloc[:,2:4]

  predictions = classifier.predict(nX)

  neighbourhoods['predictions'] = predictions

def getLatAndLong(place):
 geolocator = Nominatim()
 location = geolocator.geocode(place)
 return location.latitude, location.longitude

#function to make a prediction on a single value:
def predictPlace(place, classifier):
 #get the lat and long
 lat, long = getLatAndLong(place)
 coord = np.array([lat,long])
 coord = coord.reshape(1,-1)
 pred = classifier.predict(coord)
 return pred[0]