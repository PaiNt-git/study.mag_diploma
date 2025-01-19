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
    # mpath = os.path.join('..' if __name__ == '__main__' else os.getcwd(), 'data_for_program/_saved_models/gensim-model.bin')
    # mpath = os.path.join('..' if __name__ == '__main__' else os.getcwd(), 'data_for_program/_saved_models/gensim-model.bin')

    navecpath = os.path.join('..' if __name__ == '__main__' else os.getcwd(), 'data_for_program/_saved_models/navec_hudlit_v1_12B_500K_300d_100q.tar')
    # navecpath = os.path.join('..' if __name__ == '__main__' else os.getcwd(), 'data_for_program/_saved_models/navec_news_v1_1B_250K_300d_100q.tar')

    mpath = os.path.join('..' if __name__ == '__main__' else os.getcwd(), '..', 'gensim_model_teacher/corpuses/aij-wikiner-ru-wp3.gz.bin')
    print(mpath)

    if os.path.isfile(mpath):
        gensim_model = gensim.models.Word2Vec.load(mpath)
    else:
        navec_model = ModifNavec.load(navecpath)
        gensim_model = navec_model.as_gensim
        del navec_model
        gensim_model.save(mpath)

    morph_vocab = MorphVocab()

    phrase = list(map(lambda x: morph_vocab.lemmatize(x, 'NOUN', {}), 'правитель мужчина средневековье'.split()))

    ru_stemmer = snowballstemmer.stemmer('russian')

    ff = ru_stemmer.stemWord('Кота')

    syn = gensim_model.wv.most_similar(positive=phrase)
    print(syn)

    syn = gensim_model.wv.most_similar(positive=['королева'], negative=['женщина'])
    print(syn)

    syn = gensim_model.wv.most_similar('путин')
    print(syn)

    mpath = os.path.join('..' if __name__ == '__main__' else os.getcwd(), '..', 'gensim_model_teacher/corpuses/rus_news_2021_1M.tar.gz.bin')
    print(mpath)

    if os.path.isfile(mpath):
        gensim_model = gensim.models.Word2Vec.load(mpath)
    else:
        navec_model = ModifNavec.load(navecpath)
        gensim_model = navec_model.as_gensim
        del navec_model
        gensim_model.save(mpath)

    morph_vocab = MorphVocab()

    phrase = list(map(lambda x: morph_vocab.lemmatize(x, 'NOUN', {}), 'правитель мужчина средневековье'.split()))

    ru_stemmer = snowballstemmer.stemmer('russian')

    ff = ru_stemmer.stemWord('Кота')

    syn = gensim_model.wv.most_similar(positive=phrase)
    print(syn)

    syn = gensim_model.wv.most_similar(positive=['королева'], negative=['женщина'])
    print(syn)

    syn = gensim_model.wv.most_similar('путин')
    print(syn)

    mpath = os.path.join('..' if __name__ == '__main__' else os.getcwd(), '..', 'gensim_model_teacher/corpuses/rus_wikipedia_2021_1M.tar.gz.bin')
    print(mpath)

    if os.path.isfile(mpath):
        gensim_model = gensim.models.Word2Vec.load(mpath)
    else:
        navec_model = ModifNavec.load(navecpath)
        gensim_model = navec_model.as_gensim
        del navec_model
        gensim_model.save(mpath)

    morph_vocab = MorphVocab()

    phrase = list(map(lambda x: morph_vocab.lemmatize(x, 'NOUN', {}), 'правитель мужчина средневековье'.split()))

    ru_stemmer = snowballstemmer.stemmer('russian')

    ff = ru_stemmer.stemWord('Кота')

    syn = gensim_model.wv.most_similar(positive=phrase)
    print(syn)

    syn = gensim_model.wv.most_similar(positive=['королева'], negative=['женщина'])
    print(syn)

    syn = gensim_model.wv.most_similar('путин')
    print(syn)

    mpath = os.path.join('..' if __name__ == '__main__' else os.getcwd(), '..', 'gensim_model_teacher/corpuses/rus-ru_web-public_2019_1M.tar.gz.bin')
    print(mpath)

    if os.path.isfile(mpath):
        gensim_model = gensim.models.Word2Vec.load(mpath)
    else:
        navec_model = ModifNavec.load(navecpath)
        gensim_model = navec_model.as_gensim
        del navec_model
        gensim_model.save(mpath)

    morph_vocab = MorphVocab()

    phrase = list(map(lambda x: morph_vocab.lemmatize(x, 'NOUN', {}), 'правитель мужчина средневековье'.split()))

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

    exit()

    from gensim.test.utils import datapath
    from gensim.models.word2vec import Text8Corpus
    from gensim.models.phrases import Phrases, Phraser

    # Load training data. https://stackoverflow.com/questions/46148182/issues-in-getting-trigrams-using-gensim
    sentences = Text8Corpus(datapath('testcorpus.txt'))
    # The training corpus must be a sequence (stream, generator) of sentences,
    # with each sentence a list of tokens:
    print(list(sentences)[0][:10])

    # Train a toy bigram model.
    phrases = Phrases(sentences, min_count=1, delimiter=' ', threshold=1)
    # Apply the trained phrases model to a new, unseen sentence.
    print(phrases[['trees', 'graph', 'sun']])
    # The toy model considered "trees graph" a single phrase => joined the two
    # tokens into a single token, `trees_graph`.
    # Update the model with two new sentences on the fly.
    phrases.add_vocab([["hello", "world"], ["meow"]])

    triphrases = Phrases(phrases[sentences], min_count=1, delimiter=' ', threshold=1)

    # Export the trained model = use less RAM, faster processing. Model updates no longer possible.
    bigram = Phraser(phrases)
    print(bigram[['trees', 'graph', 'minors']])  # apply the exported model to a sentence

    # Export the trained model = use less RAM, faster processing. Model updates no longer possible.
    trigram = Phraser(triphrases)
    print(trigram[['trees', 'graph', 'minors']])  # apply the exported model to a sentence

    # Apply the exported model to each sentence of a corpus:
    for sent in bigram[sentences]:
        pass

    # Save / load an exported collocation model.
    bigram.save("/tmp/my_bigram_model.pkl")
    bigram_reloaded = Phraser.load("/tmp/my_bigram_model.pkl")
    print(bigram_reloaded[['trees', 'graph', 'minors']])  # apply the exported model to a sentence
