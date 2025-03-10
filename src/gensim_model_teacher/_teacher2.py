import sys
import os
import glob
import gzip
import tarfile
import multiprocessing
import logging

import gensim

from gensim import utils as gs_utils
from gensim import models as gs_models

try:
    from gensim.models.word2vec_inner import MAX_WORDS_IN_BATCH
except ImportError:
    raise gs_utils.NO_CYTHON


logger = logging.getLogger('gensim')
logger.setLevel(logging.ERROR)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))

MAIN_PACKAGE_DIR = os.path.abspath(os.path.join(os.path.split(str(__file__))[0]))
PACKAGE_NAME = os.path.basename(MAIN_PACKAGE_DIR)
sys.path.append(MAIN_PACKAGE_DIR)
sys.path.append(os.path.abspath(os.path.join(os.path.split(str(__file__))[0], '..')))


def load_gz_lines(path, encoding='utf8', tarfile_path=None):
    if '.tar.gz' in path and tarfile_path:
        with tarfile.open(path, mode='r:gz') as tfile:
            with tfile.extractfile(tarfile_path(tfile)) as file:
                for line in file:
                    yield line.decode(encoding).rstrip('\n')
    else:
        with gzip.open(path) as file:
            for line in file:
                yield line.decode(encoding).rstrip('\n')


class CorpusWrapper:
    """
    https://habr.com/ru/companies/vk/articles/426113/
    """

    def __init__(self, path, line_callback=None, tarfile_path=None):
        self.path = path
        self.line_callback = line_callback
        self.tarfile_path = tarfile_path

    def __iter__(self):
        corpus_lines = load_gz_lines(self.path, tarfile_path=self.tarfile_path)
        for line in corpus_lines:
            if self.line_callback:
                line = self.line_callback(line)
            # assume there's one document per line, tokens separated by whitespace
            yield gs_utils.simple_preprocess(line)


def load_train(
    **kwargs
):
    """
    Available kwargs
    :param train:
    :param train_kwargs:
    :param train_file_suffixes:
    :param train_debug:
    :param corpus_line_callback:
    :param vector_size:
    :param alpha:
    :param window:
    :param min_count:
    :param max_vocab_size:
    :param sample:
    :param seed:
    :param workers:
    :param min_alpha:
    :param sg:
    :param hs:
    :param negative:
    :param ns_exponent:
    :param cbow_mean:
    :param hashfxn:
    :param epochs:
    :param null_word:
    :param trim_rule:
    :param sorted_vocab:
    :param batch_words:
    :param compute_loss:
    :param callbacks:
    :param comment:
    :param max_final_vocab:
    :param shrink_windows:

    Defaults:

    train=False, train_kwargs={}, train_file_suffixes=None, train_debug=False, corpus_line_callback=None,
    vector_size=100, alpha=0.025, window=5, min_count=5, max_vocab_size=None, sample=1e-3, seed=1, workers=0, min_alpha=0.0001,
    sg=0, hs=0, negative=5, ns_exponent=0.75, cbow_mean=1, hashfxn=hash, epochs=5, null_word=0, trim_rule=None,
    sorted_vocab=1, batch_words=MAX_WORDS_IN_BATCH, compute_loss=False, callbacks=(),
    comment=None, max_final_vocab=None, shrink_windows=True
    """
    func_arguments = {k: v for k, v in kwargs.items()}
    print(func_arguments)
    train_ = func_arguments.pop("train") if "train" in func_arguments else False
    train_file_suffixes_ = func_arguments.pop("train_file_suffixes") if "train_file_suffixes" in func_arguments else None
    train_file_suffixes_ = [] if not train_file_suffixes_ else train_file_suffixes_
    train_debug_ = func_arguments.pop("train_debug") if "train_debug" in func_arguments else False
    if train_ and train_debug_:
        logger.setLevel(logging.DEBUG)
    train_kwargs_ = func_arguments.pop("train_kwargs") if "train_kwargs" in func_arguments else {}
    corpus_line_callback_ = func_arguments.pop("corpus_line_callback") if "corpus_line_callback" in func_arguments else None
    tarfile_path_ = func_arguments.pop("tarfile_path") if "tarfile_path" in func_arguments else None

    if 'workers' not in func_arguments or not func_arguments['workers']:
        func_arguments['workers'] = multiprocessing.cpu_count() - 1

    allready_trained_path = os.path.join(os.path.join(MAIN_PACKAGE_DIR, "corpuses"), 'allready_trained.txt')
    if not os.path.isfile(allready_trained_path):
        fp = open(allready_trained_path, 'w')
        fp.close()

    allready_trained = []
    with open(allready_trained_path) as f:
        allready_trained = f.readlines()
    allready_trained = [x.strip() for x in set(allready_trained)]

    corpuses = glob.glob(os.path.join(MAIN_PACKAGE_DIR, "corpuses", "*.gz"))

    def filterfunc(pat):
        for trainsuff in train_file_suffixes_:
            if pat.endswith(trainsuff + '.gz') or pat.endswith(trainsuff + '.tar.gz'):
                return False
        return True

    corpuses = filter(filterfunc, corpuses)

    for corpus in corpuses:

        dirname = os.path.dirname(corpus)
        base_name = os.path.basename(corpus)
        modfname = os.path.join(dirname, f"{base_name}.bin")

        sentences_ = CorpusWrapper(corpus, line_callback=corpus_line_callback_, tarfile_path=tarfile_path_) if train_ or not os.path.isfile(modfname) else None

        if os.path.isfile(modfname):
            model = gs_models.Word2Vec.load(modfname)
        else:
            model = gs_models.Word2Vec(sentences=sentences_, **func_arguments)
            model.save(modfname)

        if train_:

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

            trained = False

            # Дообучение
            if len(train_file_suffixes_):
                copath = list(os.path.splitext(corpus))

                if '.tar' in copath[0]:
                    copath[0] = copath[0].rpartition('.tar')[2]
                    copath[1] = '.tar' + copath[1]

                for suff in train_file_suffixes_:
                    corppath = copath[0] + suff + copath[1]

                    if not os.path.isfile(corppath):
                        if not os.path.isfile(corppath.replace('.gz', '.tar.gz')):
                            continue
                        else:
                            corppath = corppath.replace('.gz', '.tar.gz')

                    if allready_trained.count(os.path.basename(corppath)) == 0:
                        sennces_ = CorpusWrapper(corppath, line_callback=corpus_line_callback_, tarfile_path=tarfile_path_)
                        model.train(corpus_iterable=sennces_, **train_kwargs_)
                        allready_trained.append(os.path.basename(corppath))
                        trained = True

            else:
                if allready_trained.count(os.path.basename(corpus)) == 0:
                    model.train(corpus_iterable=sentences_, **train_kwargs_)
                    allready_trained.append(os.path.basename(corpus))
                    trained = True

            if trained:
                model.save(modfname)

    with open(allready_trained_path, 'w') as f:
        f.seek(0)
        f.truncate(0)
        f.writelines(map(lambda x: x + '\n', allready_trained))
