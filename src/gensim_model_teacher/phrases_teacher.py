import sys
import os
import gzip
import tarfile
import logging
import re
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


mpath = os.path.join('..', 'info_service/data_for_program/_saved_models/gensim-model.bin')
gensim_model = gensim.models.KeyedVectors.load(mpath)


morph_vocab = MorphVocab()
segmenter = Segmenter()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)


# https://datascience.stackexchange.com/questions/25524/how-does-phrases-in-gensim-work

if __name__ == '__main__':
    DOTRAIN = True

    def tarfile_path(tfile):
        basen = tfile.getnames()[0]
        basen = re.sub(r'\([^)]*\)', '', basen)
        return (basen + '/' + basen + '-sentences.txt').replace('.tar.gz', '')

    def corpus_line_callback(line):
        global Doc, segmenter, morph_tagger
        if not line:
            return line
        ret = ' '.join([x.partition('|')[0] for x in ((line.split(' ')[1:] if line[0].isdigit else line))])
        return ret

    train_file_suffixes = ['(1)', '(2)', '(3)']

    corpuses = sorted(glob.glob(os.path.join(MAIN_PACKAGE_DIR, "corpuses", "*.gz")), key=lambda x: x.replace('.gz', '(0).gz') if not '(' in os.path.basename(x) else x)
    processed = []

    for corpus in corpuses:
        if corpus in processed: continue
        processed.append(processed)

        dirname = os.path.dirname(corpus)
        base_name = os.path.basename(corpus)
        modfname_bi = os.path.join(dirname, f"{base_name}_bigram.pkl")
        modfname_tri = os.path.join(dirname, f"{base_name}_trigram.pkl")

        if DOTRAIN:
            sentences_b = CorpusWrapper(corpus, line_callback=corpus_line_callback, tarfile_path=tarfile_path)

            if not os.path.isfile(modfname_bi + 'full'):
                phrases = Phrases(sentences_b, min_count=1, delimiter=' ', threshold=2)
            else:
                phrases = Phrases.load(modfname_bi + 'full')

            if not os.path.isfile(modfname_tri + 'full'):
                triphrases = Phrases(phrases[sentences_b], min_count=1, delimiter=' ', threshold=2)
            else:
                triphrases = Phrases.load(modfname_tri + 'full')

            copath = list(os.path.splitext(corpus))
            if '.tar' in copath[0]:
                copath[0] = copath[0].rpartition('.tar')[2]
                copath[1] = '.tar' + copath[1]

            for suff in train_file_suffixes:
                corppath_bi = copath[0] + suff + copath[1]
                if not os.path.isfile(corppath_bi):
                    if not os.path.isfile(corppath_bi.replace('.gz', '.tar.gz')):
                        continue
                    else:
                        corppath_bi = corppath_bi.replace('.gz', '.tar.gz')
                processed.append(corppath_bi)
                sentences_b_train = CorpusWrapper(corppath_bi, line_callback=corpus_line_callback, tarfile_path=tarfile_path)

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

        try:
            bigram_reloaded = Phraser.load(modfname_bi)
            trigram_reloaded = Phraser.load(modfname_tri)
            phr = bigram_reloaded[['варшавского', 'договора']]
            phr1 = bigram_reloaded[['российские', 'войска']]
            phr2 = bigram_reloaded[['игорь', 'пархоменко']]
            print(phr)
        except: pass
