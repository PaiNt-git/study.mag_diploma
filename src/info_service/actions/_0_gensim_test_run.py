import os

import gensim

from navec import Navec
from natasha.morph.vocab import MorphVocab
import snowballstemmer


class ModifNavec(Navec):
    pass

    @property
    def as_gensim(self):
        from gensim.models import KeyedVectors

        model = KeyedVectors(self.pq.dim)
        weights = self.pq.unpack()  # warning! memory heavy
        model.add_vectors(self.vocab.words, weights)
        return model


def main():

    # mpath = os.path.join('..' if __name__ == '__main__' else os.getcwd(), 'data_for_program/_saved_models/gensim-model.bin')
    navecpath = os.path.join('..' if __name__ == '__main__' else os.getcwd(), 'data_for_program/_saved_models/navec_hudlit_v1_12B_500K_300d_100q.tar')
    # navecpath = os.path.join('..' if __name__ == '__main__' else os.getcwd(), 'data_for_program/_saved_models/navec_news_v1_1B_250K_300d_100q.tar')

    mpath = os.path.join('..' if __name__ == '__main__' else os.getcwd(), '..', 'gensim_model_teacher/corpuses/aij-wikiner-ru-wp3.gz.bin')

    if os.path.isfile(mpath):
        gensim_model = gensim.models.Word2Vec.load(mpath)
    else:
        navec_model = ModifNavec.load(navecpath)
        gensim_model = navec_model.as_gensim
        del navec_model
        gensim_model.save(mpath)

    morph_vocab = MorphVocab()

    phrase = list(map(lambda x: morph_vocab.lemmatize(x, 'NOUN', {}), 'монарх мужчина'.split()))

    ru_stemmer = snowballstemmer.stemmer('russian')

    ff = ru_stemmer.stemWord('Кота')

    syn = gensim_model.wv.most_similar(positive=phrase)
    print(syn)

    syn = gensim_model.wv.most_similar(positive=['королева'], negative=['женщина'])
    print(syn)

    syn = gensim_model.wv.most_similar('путин')
    print(syn)


if __name__ == '__main__':
    main()
