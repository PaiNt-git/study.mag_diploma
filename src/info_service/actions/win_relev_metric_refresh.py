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


def main(main_window):
    from info_service import actions

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

<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>

</head><body class="zoomed">

$$x = {-b \pm \sqrt{b^2-4ac} \over 2a}$$

$$x = {-b \pm \sqrt{b^2-4ac} \over 2a}.$$

</body></html>
'''

    WebViewRelevPreview = getattr(main_window, f'WebViewRelevPreview')
    WebViewRelevPreview.setHtml(enreturn)
