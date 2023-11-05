import sys
import os
import glob
import gzip
import multiprocessing
import logging

import gensim

from gensim import utils as gs_utils
from gensim import models as gs_models

try:
    from gensim.models.word2vec_inner import MAX_WORDS_IN_BATCH
except ImportError:
    raise gs_utils.NO_CYTHON


cdef public void initteacher():
    pass


logger = logging.getLogger('gensim')
logger.setLevel(logging.ERROR)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))

MAIN_PACKAGE_DIR = os.path.abspath(os.path.join(os.path.split(str(__file__))[0]))
PACKAGE_NAME = os.path.basename(MAIN_PACKAGE_DIR)
sys.path.append(MAIN_PACKAGE_DIR)
sys.path.append(os.path.abspath(os.path.join(os.path.split(str(__file__))[0], '..')))


def load_gz_lines(path, encoding='utf8'):
    with gzip.open(path) as file:
        for line in file:
            yield line.decode(encoding).rstrip('\n')




class CorpusWrapper:
    """
    https://habr.com/ru/companies/vk/articles/426113/
    """
    def __init__(self, path):
        self.path = path

    def __iter__(self):
        corpus_lines = load_gz_lines(self.path)
        for line in corpus_lines:
            # assume there's one document per line, tokens separated by whitespace
            yield gs_utils.simple_preprocess(line)



def load_train(
    train=False,
    train_kwargs={},
    train_file_suffix='',
    train_debug=False,
    vector_size=100,
    alpha=0.025,
    window=5,
    min_count=5,
    max_vocab_size=None,
    sample=1e-3,
    seed=1,
    workers=0,
    min_alpha=0.0001,
    sg=0,
    hs=0,
    negative=5,
    ns_exponent=0.75,
    cbow_mean=1,
    hashfxn=hash,
    epochs=5,
    null_word=0,
    trim_rule=None,
    sorted_vocab=1,
    batch_words=MAX_WORDS_IN_BATCH,
    compute_loss=False,
    callbacks=(),
    comment=None,
    max_final_vocab=None,
    shrink_windows=True,
):
    func_arguments = {k:v for k, v in locals().items()}
    train_ = func_arguments.pop("train") if "train" in func_arguments else False
    train_file_suffix_ = func_arguments.pop("train_file_suffix") if "train_file_suffix" in func_arguments else ''
    train_debug_ = func_arguments.pop("train_debug") if "train_debug" in func_arguments else False
    if train_ and train_debug_:
        logger.setLevel(logging.DEBUG)
    train_kwargs_ = func_arguments.pop("train_kwargs") if "train_kwargs" in func_arguments else {}

    if 'workers' not in func_arguments or not func_arguments['workers']:
        func_arguments['workers'] = multiprocessing.cpu_count()-1

    corpuses = glob.glob(os.path.join(MAIN_PACKAGE_DIR, "corpuses", "*.gz"))
    for corpus in corpuses:

        dirname = os.path.dirname(corpus)
        base_name = os.path.basename(corpus)
        modfname = os.path.join(dirname, f"{base_name}.bin")

        sentences_ = CorpusWrapper(corpus) if train_ or not os.path.isfile(modfname) else None

        if os.path.isfile(modfname):
            model = gs_models.Word2Vec.load(modfname)
        else:
            model = gs_models.Word2Vec(sentences=sentences_, **func_arguments)
            model.save(modfname)

        if train_:
            if train_file_suffix_:
                copath = os.path.splitext(corpus)
                sentences_ = CorpusWrapper(copath[0]+train_file_suffix_+copath[1])

            if 'total_examples' not in train_kwargs_:
                train_kwargs_['total_examples'] = model.corpus_count

            if 'total_words' not in train_kwargs_:
                train_kwargs_['total_words'] = model.corpus_total_words

            if 'epochs' not in train_kwargs_:
                train_kwargs_['epochs'] = model.epochs

            if 'start_alpha' not in train_kwargs_:
                train_kwargs_['start_alpha'] = model.alpha

            if 'end_alpha' not in train_kwargs_:
                train_kwargs_['end_alpha'] = model.min_alpha

            if 'compute_loss' not in train_kwargs_:
                train_kwargs_['compute_loss'] = model.compute_loss

            model.train(corpus_iterable=sentences_, **train_kwargs)
            model.save(modfname)


def PyInit_teacher():
    initteacher()


if __name__ == '__main__':
    load_train()