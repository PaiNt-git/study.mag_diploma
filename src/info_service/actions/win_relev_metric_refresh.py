import os
import time
import json
import asyncio
import itertools

from copy import copy

from pprint import pprint

from itertools import chain
from collections import OrderedDict

from PyQt5 import QtCore, QtGui, QtWidgets

from info_service.db_base import Session, QuestAnswerBase, QuestAnswerBaseRelevQuery, QuestAnswerBaseRelevQueryRel
from info_service.db_utils import togudb_serializator


def main(main_window, optimize=False, substringsearch=False):
    from info_service import actions

    MAIN_DIR = os.path.abspath(os.path.join(os.path.split(str(__file__))[0]))
    if not os.path.isdir(MAIN_DIR) or MAIN_DIR.endswith('actions'):
        MAIN_DIR = os.path.abspath(os.path.join(os.path.split(str(__file__))[0], '..'))

    MAIN_DIR = MAIN_DIR.replace('\\', '/')

    enreturn = r'''
<!DOCTYPE HTML>
<html><head>

<style>
.zoomed {
    zoom: 1.5;
    -moz-transform: scale(1.5);
    -moz-transform-origin: 0 0;
}
.minzoomed {
    zoom: 1.1;
    -moz-transform: scale(1.1);
    -moz-transform-origin: 0 0;
}
</style>

<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>

</head><body class="minzoomed">
</body></html>
'''

    WebViewRelevPreview = getattr(main_window, f'WebViewRelevPreview')
    WebViewRelevPreview.setHtml(enreturn)

    only_questions = main_window.MAINWINDOW_LOCAL_STORAGE['only_questions']

    session = Session()

    MetricRefreshProgressBar = main_window.MetricRefreshProgressBar

    K = 10

    all_queries = session.query(QuestAnswerBaseRelevQuery)
    count_queries = all_queries.count()

    MetricRefreshProgressBar.setRange(0, 3)
    MetricRefreshProgressBar.setValue(0)
    time.sleep(0.5)

    if substringsearch:
        def query_text_wrapper(x): return ('{' + str(x) + '}')
    else:
        def query_text_wrapper(x): return str(x)

    try:
        p_at_K = '' + ', '.join([f'{actions.metrics_getPrecisionAtK(query_text_wrapper(x.query), K, only_questions, optimize)}' for x in all_queries]) + ''
        MetricRefreshProgressBar.setValue(1)
        time.sleep(0.2)

        ap_at_K = [actions.metrics_getAvgPrecisionOfKresDecomp(query_text_wrapper(x.query), K, only_questions, optimize) for x in all_queries]

        r_dot_pk = [' +'.join(map(str, x['precKs'])) for x in ap_at_K]
        apKfrct = []
        for i in range(len(r_dot_pk)):
            apKfrct.append((r'\frac{' + str(r_dot_pk[i]) + r'}{' + str(ap_at_K[i]['lenk']) + r'}') if ap_at_K[i]['lenk'] else '0.0')

        apKfrct = '' + ', '.join(apKfrct) + ''

        ap_at_K = '' + ', '.join([f'{x["all"]}' for x in ap_at_K]) + ''
        MetricRefreshProgressBar.setValue(2)
        time.sleep(0.2)

        map_at_K = actions.metrics_getMeanAvgPrecisionAtKDecomp(K, only_questions, optimize, substringsearch)

        apks = ' +'.join(map(str, map_at_K['SumApAtKs']))
        apks = r'\frac{' + apks + '}{' + str(map_at_K['count_queries']) + '}'

        map_at_K = f'{map_at_K["all"]}'
        MetricRefreshProgressBar.setValue(3)
        time.sleep(0.2)

    except Exception as e:
        print(e)

    enreturn = r'''
<!DOCTYPE HTML>
<html><head>

<style>
.zoomed {
    zoom: 1.5;
    -moz-transform: scale(1.5);
    -moz-transform-origin: 0 0;
}
.minzoomed {
    zoom: 1.1;
    -moz-transform: scale(1.1);
    -moz-transform-origin: 0 0;
}
</style>

<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>

</head><body class="minzoomed">

<h4>Precision at K (p@K)</h4>
<div>Tочность на K элементах — базовая метрика качества ранжирования для одного объекта.</div>
$$p@K = \frac{\sum_{k=1}^{K}{r^{true}(\pi^{-1}(k))}}{K} = \frac{релевантных элементов}{K} = \left[ ''' + str(p_at_K) + r''' \right]$$
<br>
<h4>Average precision at K (ap@K)</h4>
<div>Равна сумме p@k по индексам k от 1 до K только для релевантных элементов, деленому на K.</div>
$$ap@K = \frac{1}{K}\sum_{k=1}^{K}{r^{true}(\pi^{-1}(k))}\cdot p@k = \left[ ''' + str(apKfrct) + r''' \right] = \left[ ''' + str(ap_at_K) + r''' \right]$$
<br>
<h4>Mean average precision at K (map@K)</h4>
<div>одна из наиболее часто используемых метрик качества ранжирования.
В p@K и ap@K качество ранжирования оценивается для отдельно взятого объекта (поискового запроса).
Идея map@K заключается в том, чтобы посчитать ap@K для каждого объекта(запроса) и усреднить.</div>
$$map@K = \frac{1}{N}\sum_{j=1}^{N}{ap@K_{j}} = ''' + str(apks) + r''' = ''' + str(map_at_K) + r'''$$

<br>
<i>где K = ''' + str(K) + r''', N = ''' + str(count_queries) + r'''  запросов \(U=\left\{u_{i}\right\}_{i=1}^{N}\), M ответов в выдаче \(E=\left\{e_{j}\right\}_{j=1}^{M}\). </i>


</body></html>
'''

    WebViewRelevPreview.setHtml(enreturn)
