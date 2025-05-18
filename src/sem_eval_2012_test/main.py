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

from math import nan

from googletrans import Translator

from dataclasses import make_dataclass

from navec import Navec
from natasha.morph.vocab import MorphVocab
from collections import defaultdict

from scipy.stats import spearmanr
from sklearn.metrics.pairwise import cosine_similarity

from itertools import groupby


from matplotlib import patches
from scipy.spatial import ConvexHull
import warnings; warnings.simplefilter('ignore')
import time


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
        'etalon',
        'test_models/4corpora_3,5Msentences.gz.bin',
        'test_models/navec_news_v1_1B_250K_300d_100q.tar',
        'test_models/navec_hudlit_v1_12B_500K_300d_100q.tar',
    ]

    results = defaultdict(list)
    max_Spearman = {}
    max_Spearman_allcount = {}
    max_Spearman_oov = {}

    import matplotlib.pyplot as plt

    # As many colors as there are unique midwest['category']
    categories = [os.path.basename(x) for x in MODEL_LIST]
    colors = [plt.cm.tab10((i / float(len(categories) - 1))) for i in range(len(categories))]
    colors_fg = [plt.cm.tab20(i / float(len(categories) - 1)) for i in range(len(categories))]

    # Step 2: Draw Scatterplot with unique color for each category
    fig = plt.figure(figsize=(16, 10), dpi=80, facecolor='w', edgecolor='k')

    # Step 3: Encircling
    # https://stackoverflow.com/questions/44575681/how-do-i-encircle-different-data-sets-in-scatter-plot
    def encircle(x, y, ax=None, **kw):
        if not ax: ax = plt.gca()
        p = np.c_[x, y]
        hull = ConvexHull(p)
        poly = plt.Polygon(p[hull.vertices, :], **kw)
        ax.add_patch(poly)

    size_legend = None

    for model_i, model_name in enumerate(MODEL_LIST):

        if model_name != 'etalon':
            if not 'navec_' in model_name:
                gensim_model = gensim.models.Word2Vec.load(model_name)
            else:
                navec_model = ModifNavec.load(model_name)
                gensim_model = navec_model.as_gensim

            kv_model = gensim_model.wv if type(gensim_model).__name__ == 'Word2Vec' else gensim_model

        model_name_ = os.path.basename(model_name)

        for filestr, tpairs_ in groupby(test_pairs, key=lambda x: x['filestr']):
            human_scores = []
            model_scores = []
            tpairs = list(tpairs_)
            oov_count = 0

            if model_name != 'etalon':
                # Прогнозирование
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
            if model_name != 'etalon':
                rho, _ = spearmanr(human_scores, model_scores)
            else:
                rho = float(Spearman_etalon.get(filestr, 0.0))

            allcount = len(tpairs)
            if not math.isnan(rho) and ((oov_count / allcount) if allcount else 1.0) < 0.75:
                results[model_name_].append({'Spearman_etalon_val': tpairs[0]['Spearman_etalon_val'],
                                             'Spearman': rho,
                                             'filestr': filestr,
                                             'oov_count': oov_count,
                                             'allcount': allcount,
                                             'weight': 1 - (oov_count / allcount),
                                             'dot_size': 200 * ((1 - (oov_count / allcount))),
                                             'modelname': model_name_,
                                             })
                print(f"Модель:{model_name_}, Корреляция Спирмена: {rho:.3f}")
                if not model_name_ in max_Spearman or max_Spearman[model_name_] < rho:
                    max_Spearman_oov[model_name_] = oov_count
                    max_Spearman[model_name_] = rho
                    max_Spearman_allcount[model_name_] = allcount
            else:
                print(f"Все oov или больше 75%")

        df = pandas.DataFrame.from_dict(results[model_name_])

        print(f'''


Максимальная Корреляция Спирмена: {max_Spearman[model_name_]}, OOV:{max_Spearman_oov[model_name_]}/{max_Spearman_allcount[model_name_]} для модели {model_name_}


        ''')

        plotname = f'{model_name_}'
        if model_name_ == 'etalon':
            plotname = 'Эталонная кореляция типичности "SemEval-2012"'

        sc = plt.scatter(x=df.index.array, y='Spearman', data=df, s='dot_size', c=colors[model_i], label=str(plotname), edgecolors='black', linewidths=.5)

        def g(s): return s / 200
        size_legend = plt.legend(*sc.legend_elements("sizes", num=4, func=g), frameon=False, title="Качество по OOV", loc='upper right')

        # Select data to be encircled
        midwest_encircle_data = df

        # Draw polygon surrounding vertices
        encircle(midwest_encircle_data.index.array, midwest_encircle_data.Spearman, ec="none", fc=colors_fg[model_i], alpha=0.05)
        encircle(midwest_encircle_data.index.array, midwest_encircle_data.Spearman, ec=colors[model_i], fc="none", linewidth=0.5, linestyle=':')

    # Step 4: Decorations
    plt.gca().set(ylim=(-0.75, 1.35), xlabel='Группы тестов', ylabel='Коэффицент корреляции Спирмана: ρ')

    plt.gca().xaxis.label.set(fontsize=16)
    plt.gca().yaxis.label.set(fontsize=16)

    plt.axhline(y=0.7,
                color='green',
                linestyle='--',
                linewidth=0.75,
                label=f'Хорошее качество (близко к человеческим оценкам)')

    plt.axhline(y=0.0,
                color='red',
                linewidth=1.5,
                label=f'Корреляция меньше нуля')

    plt.xticks([]); plt.yticks(fontsize=12)

    if len(MODEL_LIST) > 2:
        windtitle = f'''
    Тесты семантической близости "SemEval-2012-Platinum-Ratings"
    ({len(MODEL_LIST)-1} модели)
    '''
    else:
        windtitle = f'''
    Тесты семантической близости "SemEval-2012-Platinum-Ratings"
    (Модель "{os.path.basename(MODEL_LIST[1])}")
    '''

    plt.title(windtitle, fontsize=20)

    plt.legend(fontsize=12, loc='lower right')
    plt.gca().add_artist(size_legend)

    plt.show()

    pass
