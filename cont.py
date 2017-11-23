
import string, sys, itertools, re

'''
Created on Sep 3, 2017

@author: Abbas Ghaddar
'''

tagIdx = ('LOC', 'MISC','ORG','PER')
rate = 4

def getCombination (sent, model):
    tokens = []
    flag = False
    
    for w in sent:
        if w == '<B-NE>':
            tokens.append('<u>')
            flag = True
        elif w == '<L-NE>':
            flag = False
        elif not flag: 
            tokens.append(w)
    
    entity_indices = [i for i, x in enumerate(tokens) if x == "<u>"]
    print tokens, entity_indices
    
    
    # check if we have enough context 
    count= len(entity_indices) + len([item for item in tokens if  item in string.punctuation and "#" not in item])
    if len(tokens) == count:
        return  [[ (ele, -1000) for ele in tagIdx] for _ in entity_indices] 
    
    
    #check best combination of entity    
    maxscore = -sys.maxint    
    if len(entity_indices) < rate:
        for p in itertools.product(tagIdx, repeat=len(entity_indices)) : 
            for i in range (len(entity_indices)):                               
                tokens[entity_indices[i]] = '<'+p[i]+'>'          
            
            score = model.score(' '.join(tokens))
            if score > maxscore:
                best = p
                maxscore = score
        
        for i in range (len(entity_indices)):
            tokens[entity_indices[i]] = '<'+best[i]+'>'
    else:
        tokens, best, maxscore= getBestForLarge (entity_indices, tokens, model)

    
    return getTopCandidates (entity_indices, tokens, maxscore, model)


"""
if len(entity) > rate; find the best combination by batch of size rate
"""

def getBestForLarge (entity_indices, sent, model):
    best = []
    maxscore = -sys.maxint
        
    
    for k in range (0, len(entity_indices), rate):
        if k + rate >=  len(entity_indices) :
            rate = len(entity_indices) - k 
        maxscore = -sys.maxint
        for p in itertools.product(tagIdx, repeat=rate) : 
            for i in range(0, len(entity_indices)):
                if i >= k and i < k+rate:
                    sent[entity_indices[i]] = '<'+p[i-k]+'>'
                elif i> k+rate:
                    sent[entity_indices[i]] = ' '
                                
            score = model.score(re.sub( '\s+', ' ', ' '.join(sent)))
            if score > maxscore:
                best1 = p
                maxscore = score
    
        for tag in best1 :
            best.append(tag)
            
        for i in range(0, len(entity_indices)):
                if i >= k and i < k+rate:
                    sent[entity_indices[i]] = '<'+best1[i-k]+'>'
                    
    score = model.score(re.sub( '\s+', ' ', ' '.join(sent)))
    
    return sent,best,score 

"""
Output: a list of size len(entity); each item in the list is a list that contains the score for each tag
"""
def getTopCandidates (entity_indices, tokens, maxscore, model):
    lst = []
    
    
    if len(entity_indices) == 0 :
        return []   
    
    for i in range(len(entity_indices)):
        tag = tokens[entity_indices[i]].replace('<','').replace('>','')
        tmp = tokens
        local = []
        
        local.append ((tag, maxscore))
        for p in itertools.product(tagIdx, repeat=1):
            if p[0] != tag :
                tmp[entity_indices[i]] = '<'+p[0]+">"
                score = model.score(' '.join(tmp))
                local.append ((p[0], score))                    
            
        tmp[entity_indices[i]] = "<"+tag+">"
        lst.append(sorted(local, key=lambda x: x[1], reverse=True))
                        
    return lst