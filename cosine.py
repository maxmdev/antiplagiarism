import re
import math

def cosinedatabaseTF(databasetxt):
    universalSetOfUniqueWords = []
    databaseTF = []
    database1 = databasetxt

    databaseWordList = re.sub("[^\w]", " ", str(database1)).split()  # Replace punctuation by space and split
    for word in databaseWordList:
        if word not in universalSetOfUniqueWords:
            universalSetOfUniqueWords.append(word)
    for word in universalSetOfUniqueWords:
        databaseTfCounter = 0
        for word2 in databaseWordList:
            if word == word2:
                databaseTfCounter += 1
        databaseTF.append(databaseTfCounter)
    #print (universalSetOfUniqueWords)
    #print (databaseTF)
    resp = []
    for i,_ in enumerate(universalSetOfUniqueWords):
        resp.append("\"{}\":{}".format(universalSetOfUniqueWords[i], databaseTF[i]))
    d = ",".join(resp)
    return "\"fileTFCosine\": " + "[{" + d + "}]"

def cosineSimilarity(input, databasetxt):
    universalSetOfUniqueWords = []
    matchPercentage = 0

    ####################################################################################################

    inputQuery = input
    lowercaseQuery = inputQuery.lower()

    queryWordList = re.sub("[^\w]", " ", lowercaseQuery).split()  # Replace punctuation by space and split
    for word in queryWordList:
        if word not in universalSetOfUniqueWords:
            universalSetOfUniqueWords.append(word)

    ####################################################################################################

    database1 = databasetxt

    databaseWordList = re.sub("[^\w]", " ", database1).split()  # Replace punctuation by space and split
    for word in databaseWordList:
        if word not in universalSetOfUniqueWords:
            universalSetOfUniqueWords.append(word)

    ####################################################################################################

    queryTF = []
    databaseTF = []
    count_iter = 0
    for word in universalSetOfUniqueWords:
        count_iter += 1
        queryTfCounter = 0
        databaseTfCounter = 0
        for word2 in queryWordList:
            count_iter += 1
            if word == word2:
                queryTfCounter += 1
        queryTF.append(queryTfCounter)

        for word2 in databaseWordList:
            count_iter += 1
            if word == word2:
                databaseTfCounter += 1
        databaseTF.append(databaseTfCounter)

    dotProduct = 0
    for i in range(len(queryTF)):
        count_iter += 1
        dotProduct += queryTF[i] * databaseTF[i]
    #print(dotProduct)

    queryVectorMagnitude = 0
    for i in range(len(queryTF)):
        count_iter += 1
        queryVectorMagnitude += queryTF[i] ** 2
    queryVectorMagnitude = math.sqrt(queryVectorMagnitude)

    databaseVectorMagnitude = 0
    for i in range(len(databaseTF)):
        count_iter += 1
        databaseVectorMagnitude += databaseTF[i] ** 2
    databaseVectorMagnitude = math.sqrt(databaseVectorMagnitude)
    try:
        matchPercentage = (float)(dotProduct / (queryVectorMagnitude * databaseVectorMagnitude)) * 100
    except Exception:
        pass
    mean_len_words = int((len(queryWordList) + len(databaseWordList))/2)
    return matchPercentage, count_iter, mean_len_words