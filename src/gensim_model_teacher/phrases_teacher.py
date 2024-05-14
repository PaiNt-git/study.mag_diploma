import sys
import os
import gzip
import logging

import glob

import gensim

from gensim.models.phrases import Phrases, Phraser

from gensim import utils as gs_utils
from gensim import models as gs_models
from natasha.morph.vocab import MorphVocab
from natasha.doc import DocSent, Doc
from natasha.segment import Segmenter
from natasha.morph.tagger import NewsMorphTagger
from natasha.emb import NewsEmbedding


logger = logging.getLogger('gensim.models.phrases')
logger.setLevel(logging.INFO)
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

    def __init__(self, path, line_callback=None):
        self.path = path
        self.line_callback = line_callback

    def __iter__(self):
        corpus_lines = load_gz_lines(self.path)
        for line in corpus_lines:
            if self.line_callback:
                line = self.line_callback(line)
            # assume there's one document per line, tokens separated by whitespace
            yield gs_utils.simple_preprocess(line)


mpath = os.path.join('..', 'info_service/data_for_program/_saved_models/gensim-model.bin')
gensim_model = gensim.models.KeyedVectors.load(mpath)


morph_vocab = MorphVocab()
segmenter = Segmenter()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)


# https://datascience.stackexchange.com/questions/25524/how-does-phrases-in-gensim-work

if __name__ == '__main__':
    def corpus_line_callback(line):
        global Doc, segmenter, morph_tagger
        ret = ' '.join([x.partition('|')[0] for x in line.split(' ')])
        return ret

    train_file_suffixes = ['(1)', '(2)', '(3)']

    corpuses = glob.glob(os.path.join(MAIN_PACKAGE_DIR, "corpuses", "*.gz"))

    for corpus in corpuses:

        dirname = os.path.dirname(corpus)
        base_name = os.path.basename(corpus)
        modfname_bi = os.path.join(dirname, f"{base_name}_bigram.pkl")
        modfname_tri = os.path.join(dirname, f"{base_name}_trigram.pkl")

        sentences_b = CorpusWrapper(corpus, line_callback=corpus_line_callback)

        if not os.path.isfile(modfname_bi + 'full'):
            phrases = Phrases(sentences_b, min_count=1, delimiter=' ', threshold=2)
        else:
            phrases = Phrases.load(modfname_bi + 'full')

        if not os.path.isfile(modfname_tri + 'full'):
            triphrases = Phrases(phrases[sentences_b], min_count=1, delimiter=' ', threshold=2)
        else:
            triphrases = Phrases.load(modfname_tri + 'full')

        copath = os.path.splitext(corpus)

        for suff in train_file_suffixes:
            corppath_bi = copath[0] + suff + copath[1]
            if not os.path.isfile(corppath_bi):
                continue
            sentences_b_train = CorpusWrapper(corppath_bi, line_callback=corpus_line_callback)

            phrases.add_vocab(sentences_b_train)
            triphrases.add_vocab(phrases[sentences_b_train])

        phrases.save(modfname_bi + 'full')
        phrases = Phrases.load(modfname_bi + 'full')

        triphrases.save(modfname_tri + 'full')
        triphrases = Phrases.load(modfname_tri + 'full')

        bigram = Phraser(phrases)
        trigram = Phraser(triphrases)

        # Apply the exported model to each sentence of a corpus:
        for sent in bigram[sentences_b]:
            pass

        # Apply the exported model to each sentence of a corpus:
        for sent in trigram[sentences_b]:
            pass

        # Save / load an exported collocation model.
        bigram.save(modfname_bi)
        bigram_reloaded = Phraser.load(modfname_bi)
        del bigram
        del phrases

        trigram.save(modfname_tri)
        trigram_reloaded = Phraser.load(modfname_tri)
        del trigram
        del triphrases

        print(bigram_reloaded[['варшавского', 'договора']])
        print(trigram_reloaded)
