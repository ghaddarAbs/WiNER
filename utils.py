

import math
tagIdx = ('LOC', 'MISC','ORG','PER')

'''
Created on Sep 3, 2017

@author: Abbas Ghaddar
'''

def scoreNormalizer (rank):
    if rank[0][1] == -1000:
        return [ (item[0], "NAN") for item in rank]
    lowest = abs(sorted(rank, key=lambda x: x[1])[0][1])
    rank= [ (item[0], item[1]+lowest) for item in rank]
    total = sum([item[1] for item in rank])
    rank= [ (item[0], item[1]/total ) for item in rank]
      
    return rank

def getFeatures (lst):
    fVec = []  
    
    lst [0] = sorted(scoreNormalizer (lst[0]))
     
    if lst[1][0][1] == -1000:
        lst [1] = lst [0]
    else:   
        lst [1] = sorted(scoreNormalizer (lst[1]))
     
    if lst[2][0][1] == -1000:
        lst [2] = lst [0]
    else: 
        lst [2] = sorted(lst[2])         
      
    
    for j in range(len(lst)):    
        vec = sorted([(item[0],float("{0:.4f}".format(item[1]))) for item in lst[j] ], key=lambda x: x[1], reverse=True)
        fVec = getNumericFeatures (vec, fVec)             
    
    return  fVec

def getNumericFeatures (rank, fVec):
         
    #entities rank
    for i in range (0,len(rank)):
        tmp = [0] * 4
        tmp[tagIdx.index(rank[i][0])] = 1
        fVec += tmp
    
    #entity score
    for i in range (0,len(rank)):
        fVec.append(rank[i][1])
    
    #entity diff    
    for i in range (0,len(rank)):
        for j in range (i+1,len(rank)):
            score = rank[i][1]-rank[j][1]
            fVec.append (score)
    
    return fVec


def vec_similarity(entity, model):
    debug = [] 
    entity = [ item for item in entity if item in model.vocab]

    if len(entity) == 0:
        for ele in tagIdx:
            debug.append( (ele, -1000))                 
    elif len(entity) == 1:
        for ele in tagIdx:
            debug.append( (ele, cosine_similarity( model['<u-'+ele.lower()+'>'], model[entity[0]])))
    else:
        for ele in tagIdx:
            dist = cosine_similarity( model['<b-'+ele.lower()+'>'], model[entity[0]] ) + cosine_similarity( model[entity[len(entity)-1]], model['<l-'+ele.lower()+'>'])
            for k in range (0, len(entity)):
                dist += cosine_similarity( model['<i-'+ele.lower()+'>'], model[entity[k]] )
    
            debug.append( ( ele,dist/(len(entity)+2)) )
             
    debug= sorted(debug, key=lambda x: x[1], reverse=True)       
                                                                           
    return   debug

def cosine_similarity(v1, v2):
    "compute cosine similarity of v1 to v2: (v1 dot v2)/{||v1||*||v2||)"
    sumxx, sumxy, sumyy = 0, 0, 0
    for i in range(len(v1)):
        x = v1[i]; y = v2[i]
        sumxx += x*x
        sumyy += y*y
        sumxy += x*y
    return sumxy/math.sqrt(sumxx*sumyy)
    