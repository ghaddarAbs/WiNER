import sys, itertools, re

'''
Created on Sep 3, 2017

@author: Abbas Ghaddar
'''

tagIdx = ('LOC', 'MISC','ORG','PER')
rate = 4

def getCombination (sent, entity_indices, model):
    maxscore = -sys.maxint
    
    if len(entity_indices) < rate:
        for p in itertools.product(tagIdx, repeat=len(entity_indices)): 
            for i in range(len(entity_indices)):                               
                sent[entity_indices[i][0]] = '<B-'+p[i]+">"
                sent[entity_indices[i][1]] = '<L-'+p[i]+">"
            
            score = model.score(' '.join(sent))
            if score > maxscore:
                best = p
                maxscore = score
        
        for i in range(len(entity_indices)):
            sent[entity_indices[i][0]] = '<B-'+best[i]+">"
            sent[entity_indices[i][1]] = '<L-'+best[i]+">"
    else:
        sent, best, maxscore  = getBestForLarge (entity_indices, sent, model)
       
    return getTopCandidates (entity_indices, sent, maxscore, model)

def getBestForLarge (entity_indices, sent, model):
    best = []
    maxscore = -sys.maxint
    
    
    for k in range (0, len(entity_indices), rate):
        if k + rate >=  len(entity_indices) :
            rate = len(entity_indices) - k 
        
        maxscore = -sys.maxint
        for p in itertools.product(tagIdx, repeat=rate) : 
            for i in range(len(entity_indices)):
                if i >= k and i < k+rate:
                    sent[entity_indices[i][0]] = '<B-'+p[i-k ]+">"
                    sent[entity_indices[i][1]] = '<L-'+p[i-k]+">"
                elif i> k+rate:
                    sent[entity_indices[i][0]] = ' '
                    sent[entity_indices[i][1]] = ' '
            
            score = model.score(re.sub( '\s+', ' ', ' '.join(sent)))
            if score > maxscore:
                best1 = p
                maxscore = score
    
        for tag in best1 :
            best.append(tag)
            
        for i in range(len(entity_indices)):
                if i >= k and i < k+rate:
                    sent[entity_indices[i][0]] = '<B-'+best1[i-k]+">"
                    sent[entity_indices[i][1]] = '<L-'+best1[i-k]+">"
    
    score = model.score(re.sub( '\s+', ' ', ' '.join(sent)))
    
    return sent,best,score 


def getTopCandidates (entity_indices, sent, maxscore, model):
    lst= []
    
    if len(entity_indices) == 0 :
        return []
    
    for i in range(len(entity_indices)):
        tag = sent[entity_indices[i][0]].replace('<B-','').replace('>','')
        tmp = sent
        local = []
        
        local.append ((tag, maxscore))
        for p in itertools.product(tagIdx, repeat=1):
            if p[0] != tag :
                tmp[entity_indices[i][0]] = '<B-'+p[0]+">"
                tmp[entity_indices[i][1]] = '<L-'+p[0]+">"
                score = model.score(' '.join(tmp))
                local.append ((p[0], score))                    
            
        tmp[entity_indices[i][0]] = '<B-'+tag+">"
        tmp[entity_indices[i][1]] = '<L-'+tag+">"
        lst.append(sorted(local, key=lambda x: x[1], reverse=True))
        
    return lst   

