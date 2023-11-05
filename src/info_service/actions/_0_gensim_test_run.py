import os

import gensim

from navec import Navec


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

    mpath = os.path.join('..' if __name__ == '__main__' else os.getcwd(), 'data_for_program/_saved_models/gensim-model.bin')
    navecpath = os.path.join('..' if __name__ == '__main__' else os.getcwd(), 'data_for_program/_saved_models/navec_hudlit_v1_12B_500K_300d_100q.tar')
    # navecpath = os.path.join('..' if __name__ == '__main__' else os.getcwd(), 'data_for_program/_saved_models/navec_news_v1_1B_250K_300d_100q.tar')

    if os.path.isfile(mpath):
        gensim_model = gensim.models.KeyedVectors.load(mpath)
    else:
        navec_model = ModifNavec.load(navecpath)
        gensim_model = navec_model.as_gensim
        del navec_model
        gensim_model.save(mpath)

    syn = gensim_model.most_similar('специальность')
    print(syn)

    syn = gensim_model.most_similar('кровь')
    print(syn)

    syn = gensim_model.most_similar('вино')
    print(syn)

    syn = gensim_model.most_similar('ведьмак')
    print(syn)


if __name__ == '__main__':
    main()
