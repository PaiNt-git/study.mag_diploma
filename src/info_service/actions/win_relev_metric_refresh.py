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


def main(main_window):
    from info_service import actions

    only_questions = main_window.MAINWINDOW_LOCAL_STORAGE['only_questions']

    session = Session()

    K = 10

    all_queries = session.query(QuestAnswerBaseRelevQuery)
    count_queries = all_queries.count()

    try:
        p_at_K = '[' + ', '.join([f'{actions.metrics_getPrecisionAtK(x.query, K, only_questions)}' for x in all_queries]) + ']'
        ap_at_K = '[' + ', '.join([f'{actions.metrics_getAvgPrecisionOfKres(x.query, K, only_questions)}' for x in all_queries]) + ']'
        map_at_K = f'{actions.metrics_getPrecisionAtK(K, only_questions)}'
    except Exception as e:
        print(e)

    enreturn = '''
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

<script src="polyfill.min.js?features=es6"></script>
<script id="MathJax-script" async src="tex-mml-chtml.js"></script>


<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>

</head><body class="zoomed">

<h4>Precision at K (p@K)</h4>
<div>Tочность на K элементах — базовая метрика качества ранжирования для одного объекта.</div>
$$p@K = \frac{\sum_{k=1}^{K}{r^{true}(\pi^{-1})(k))}}{K} = \frac{релевантных элементов}{K} = ''' + p_at_K + '''$$

<h4>Average precision at K (ap@K)</h4>
<div>Равна сумме p@k по индексам k от 1 до K только для релевантных элементов, деленому на K.</div>
$$ap@K = \frac{1}{K}\sum_{k=1}^{K}{r^{true}(\pi^{-1})(k))}\cdot p@k = ''' + ap_at_K + '''$$

<h4>Mean average precision at K (map@K)</h4>
<div>одна из наиболее часто используемых метрик качества ранжирования.
В p@K и ap@K качество ранжирования оценивается для отдельно взятого объекта (поискового запроса).
Идея map@K заключается в том, чтобы посчитать ap@K для каждого объекта(запроса) и усреднить.</div>
$$map@K = \frac{1}{N}\sum_{j=1}^{N}{ap@K_{j}} = ''' + map_at_K + '''$$


<i>-, где $$K = ''' + K + '''$$, N  запросов $$ U = \left\{ u_{i} \right\}_{i=1}^{N} $$ M ответов в выдаче $$ E = \left\{ e_{j} \right\}_{j=1}^{M} $$. </i>


</body></html>
'''

    WebViewRelevPreview = getattr(main_window, f'WebViewRelevPreview')
    WebViewRelevPreview.setHtml(enreturn)
