from __future__ import print_function

import optparse, os, re
from collections import OrderedDict
'''
Created on Sep 3, 2017

@author: Abbas Ghaddar
'''
tagIdx = ('LOC', 'MISC','ORG','PER')

def prepareInput (sentence):
    begin_indices = [i for i, x in enumerate(sentence) if x == "<B-NE>"]
    end_indices = [i for i, x in enumerate(sentence) if x == "<L-NE>"]
    entity_indices = zip(begin_indices, end_indices)
    tokens = [ re.sub("\d", "#", item.lower()) for item in sentence]
    for i in begin_indices+end_indices:
        tokens[i]= tokens[i].upper() 
    
    return entity_indices, tokens
    
def predictSentenceAll (sentence):
    sentence= sentence.strip().split(" ")
    entity_indices, tokens=  prepareInput (sentence)
    
    if len(entity_indices) == 0:
        return 
    
    mixture = mix.getCombination(list(tokens), entity_indices, model['mix'])
    context = cont.getCombination(list(tokens), model['cont'])
    embeddings = [ utils.vec_similarity(tokens[entity_indices[i][0]+1:entity_indices[i][1]], model['emb']) \
                   for i in range(len(entity_indices))]
    print(embeddings)
    fVec = np.asarray([utils.getFeatures ([mixture[i], context[i], embeddings[i]]) for i in range(len(mixture))])
    Y_pred = [x-1 for x in model['rf'].predict(fVec)]
    Y_pred = map(int, Y_pred)
    
    for i in range(len(entity_indices)):
        print ("Entity ", i, ":", " ".join(sentence[entity_indices[i][0]+1:entity_indices[i][1]]),\
                " Predicted Tag: ", tagIdx[Y_pred[i]] )
        print ("MIX ", sorted(utils.scoreNormalizer (mixture[i]), key=lambda x: x[1], reverse=True))
        print ("Cont", sorted(utils.scoreNormalizer (context[i]), key=lambda x: x[1], reverse=True))
        print ("EMB ", sorted(utils.scoreNormalizer (embeddings[i]), key=lambda x: x[1], reverse=True))
        print ("\n")
    print ("\n")

def predictSentenceOne (sentence):
    sentence= sentence.strip().split(" ")
    entity_indices, tokens=  prepareInput (sentence)
    
    if len(entity_indices) == 0:
        return
    
    if opts.mix: 
        representation = mix.getCombination(tokens, entity_indices, model['mix'])
        print ("Predict using MIX model")
    elif opts.cont:
        representation = cont.getCombination(tokens, model['cont'])
        print ("Predict using CONTEXT model")
    elif opts.emb:
        representation = [ utils.vec_similarity(tokens[entity_indices[i][0]+1:entity_indices[i][1]], model['emb']) \
                            for i in range(len(entity_indices))]
        print ("Predict using EMBEDDINGS model")
    
    for i in range(len(entity_indices)):
        print ("Entity ", (i+1) ,":", " ".join(sentence[entity_indices[i][0]+1:entity_indices[i][1]]))
        print ("Prediction", sorted(utils.scoreNormalizer (representation[i]), key=lambda x: x[1], reverse=True))
        print ("\n")
    print ("\n")
    


optparser = optparse.OptionParser()

optparser.add_option(
    "-m", "--mix_lm", default='/data/lm.mixture.binary',
    help="Location of mix Language Model"
)

optparser.add_option(
    "-c", "--cont_lm", default='/data/lm.context.binary',
    help="Location of context Language Model"
)

optparser.add_option(
    "-e", "--pre_emb", default='/data/embeddings.386388.50.binary',
    help="Location of pretrained embeddings"
)

optparser.add_option(
    "-p", "--rf", default='/data/rf.pkl',#
    help="Location of RF model"
)

optparser.add_option('--mix', action='store_true', default= False,
                    help='Use only MIX model')

optparser.add_option('--cont', action='store_true', default= False,
                    help='Use only CONTEXT model')

optparser.add_option('--emb', action='store_true', default= False,
                    help='Use only Embedding model')


opts = optparser.parse_args()[0]

# Parse parameters
Parse_parameters = OrderedDict()
Parse_parameters['pre_emb'] = opts.pre_emb
Parse_parameters['cont_lm'] = opts.cont_lm
Parse_parameters['mix_lm'] = opts.mix_lm
Parse_parameters['rf'] = opts.rf
Parse_parameters['mix'] = opts.mix
Parse_parameters['cont'] = opts.cont
Parse_parameters['emb'] = opts.emb





import kenlm
from gensim import models
from cPickle import load as pkl_load
import numpy as np
import mix, cont , utils

# Check parameters validity
assert os.path.isfile(opts.pre_emb)
assert os.path.isfile(opts.cont_lm)
assert os.path.isfile(opts.mix_lm)
assert os.path.isfile(opts.rf)
assert sum([opts.mix, opts.cont, opts.emb]) < 2

#load model
model = {}
model_single = None

if sum([opts.mix, opts.cont, opts.emb]) == 0:
    print ("Loading MIX Language Model..........")
    model['mix']= kenlm.Model(opts.mix_lm)
    
    print ("Loading CONTEXT Language Model..........")
    model['cont']= kenlm.Model(opts.cont_lm)
    
    print ("Loading pre trained Embeddings..........")
    model['emb']= models.Word2Vec.load_word2vec_format(opts.pre_emb, binary=False)

    print ("Loading Classfier:\t..........")
    with open(opts.rf, 'rb') as fid:
        model['rf'] = pkl_load(fid)
    model['rf'].set_params( verbose=0)

else:
    if opts.mix:
        model_single= 'mix'
        print ("Loading MIX Language Model..........")
        model['mix']= kenlm.Model(opts.mix_lm)
    elif opts.cont:
        model_single= 'cont'
        print ("Loading CONTEXT Language Model..........")
        model['cont']= kenlm.Model(opts.cont_lm)
    elif opts.emb:
        model_single= 'emb'
        print ("Loading pre trained Embeddings..........")
        model['emb']= models.Word2Vec.load_word2vec_format(opts.pre_emb, binary=False)

print("\nInput Requirement: Tokenized (space-separated) sentence + entity boundary as in:")
print("<B-NE> Gonzales <L-NE> will be featured on <B-NE> Daft Punk <L-NE> .\n")
print("Also entity can be nominal or pronominal mentions as in:")        
print("<B-NE> The company <L-NE> liquidated <B-NE> its <L-NE> assets .\n")

while True:
    input_term = raw_input("\nEnter sentence (EXIT to break): ")
    if input_term == 'EXIT':
        break
    else:
        try:
            if sum([opts.mix, opts.cont, opts.emb]) == 0:
                predictSentenceAll (input_term)
            else:
                predictSentenceOne (input_term)

        except Exception, e:
            print (e)
            pass

