'''
Created on 14 мая 2025 г.

@author: PaiNt
'''
import os
import glob

import pickle
import numpy as np
import gensim
import snowballstemmer

import timeit

import math
import pandas

from googletrans import Translator

from dataclasses import make_dataclass

from navec import Navec
from natasha.morph.vocab import MorphVocab
from collections import defaultdict

from scipy.stats import spearmanr
from sklearn.metrics.pairwise import cosine_similarity

from itertools import groupby
from math import nan


# https://sites.google.com/site/semeval2012task2/home?authuser=0


class ModifNavec(Navec):
    pass

    @property
    def as_gensim(self):
        from gensim.models import KeyedVectors

        model = KeyedVectors(self.pq.dim)
        weights = self.pq.unpack()  # warning! memory heavy
        model.add_vectors(self.vocab.words, weights)
        return model


if __name__ == '__main__':
    translator = Translator()

    Spearman_etalon = {}
    with open("semeval_ds\SemEval-2012-Platinum-Ratings\platinum-data-correlations.csv", "r") as f:
        for line in f:
            filestr, score = line.strip().split(",")
            try:
                Spearman_etalon[filestr] = float(score)
            except: pass

    test_pairs = []
    if os.path.isfile('test_pairs.pkl'):
        with open('test_pairs.pkl', 'rb') as filep:
            test_pairs = pickle.load(filep)
    else:
        for filestr in glob.glob(os.path.join(os.path.dirname(__file__), 'semeval_ds', 'SemEval-2012-Platinum-Ratings', 'Phase2AnswersScaled', "*.txt")):
            with open(filestr, "r") as f:
                for line in f:
                    if not line.startswith('#'):
                        try:
                            score, pair = line.strip().split(" ")
                            score = float(score)
                            pair = pair.replace('"', '')
                            pair = pair.strip().split(":")
                        except: score = pair = None
                        if not pair: continue
                        if len(pair) != 2: continue

                        bfn = os.path.basename(filestr)

                        Spearman_etalon_val = Spearman_etalon.get(bfn, None)

                        pair_rus = [translator.translate(pair[0], src='en', dest='ru').text, translator.translate(pair[1], src='en', dest='ru').text]

                        test_pairs.append({'Spearman_etalon_val': Spearman_etalon_val, 'filestr': bfn, 'score': score, 'pair': pair, 'pair_rus': pair_rus})

        with open('test_pairs.pkl', 'wb') as filep:
            filep.seek(0)
            pickle.dump(test_pairs, filep)

    MODEL_LIST = [
        'test_models/4corpora_3,5Msentences.gz.bin',
        'test_models/navec_news_v1_1B_250K_300d_100q.tar',
        'test_models/navec_hudlit_v1_12B_500K_300d_100q.tar',
    ]

    results = defaultdict(list)
    max_Spearman = {}
    max_Spearman_allcount = {}
    max_Spearman_oov = {}

    for model_name in MODEL_LIST:

        if not 'navec_' in model_name:
            gensim_model = gensim.models.Word2Vec.load(model_name)
        else:
            navec_model = ModifNavec.load(model_name)
            gensim_model = navec_model.as_gensim

        kv_model = gensim_model.wv if type(gensim_model).__name__ == 'Word2Vec' else gensim_model

        for filestr, tpairs_ in groupby(test_pairs, key=lambda x: x['filestr']):

            # Прогнозирование
            human_scores = []
            model_scores = []
            tpairs = list(tpairs_)
            oov_count = 0

            for semitem in tpairs:
                word1 = semitem['pair_rus'][0]
                word2 = semitem['pair_rus'][1]
                score = semitem['score']

                if word1 in kv_model and word2 in kv_model:
                    emb1 = kv_model[word1].reshape(1, -1)
                    emb2 = kv_model[word2].reshape(1, -1)
                    sim = cosine_similarity(emb1, emb2)[0][0]
                    human_scores.append(score)
                    model_scores.append(sim)
                else:
                    oov_count += 1

            human_scores = np.array(human_scores)
            model_scores = np.interp(model_scores, (-1, 1), (-100, 100))

            # Оценка
            rho, _ = spearmanr(human_scores, model_scores)

            allcount = len(tpairs)
            if not math.isnan(rho) and ((oov_count / allcount) if allcount else 1.0) < 0.80:
                model_name_ = os.path.basename(model_name)
                results[model_name_].append({'Spearman_etalon_val': tpairs[0]['Spearman_etalon_val'],
                                             'Spearman': rho,
                                             'filestr': filestr,
                                             'oov_count': oov_count,
                                             'allcount': allcount,
                                             'weight': (1 / (oov_count / allcount)) if oov_count else 1.0
                                             })
                print(f"Модель:{model_name_}, Корреляция Спирмена: {rho:.3f}")
                if not model_name_ in max_Spearman or max_Spearman[model_name_] < rho:
                    max_Spearman_oov[model_name_] = oov_count
                    max_Spearman[model_name_] = rho
                    max_Spearman_allcount[model_name_] = allcount
            else:
                print(f"Все oov или больше 80%")

        df = pandas.DataFrame.from_dict(results[model_name_])

        print(f'''


Максимальная Корреляция Спирмена: {max_Spearman[model_name_]}, OOV:{max_Spearman_oov[model_name_]}/{max_Spearman_allcount[model_name_]} для модели {model_name_}


        ''')

    pass
