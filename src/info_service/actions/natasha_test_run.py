
from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,
    PER,
    NamesExtractor,
    Doc
)
from pprint import pprint


def main():

    segmenter = Segmenter()
    morph_vocab = MorphVocab()

    emb = NewsEmbedding()
    morph_tagger = NewsMorphTagger(emb)
    syntax_parser = NewsSyntaxParser(emb)
    ner_tagger = NewsNERTagger(emb)

    names_extractor = NamesExtractor(morph_vocab)

    text = '''
    Квинтиллий никогда не пропускал битв с участием Сикария. Казалось, ему доставляет удовольствие бередить собственные раны. Он уже проиграл такое количество денег, что его хватило бы на покупку виллы в Кампании, но продолжал посещать Колизей; пожалуй, он мог бы найти своему времени и вниманию лучшее применение, отправившись на заседание Сената, но ничего не мог с собой поделать.
    '''.strip()

    doc = Doc(text)
    pprint(doc)

    print('\n=======Segmentation========\n')

    doc.segment(segmenter)

    for token in doc.tokens:
        pprint(token)

    print('\n')

    for sentence in doc.sents:
        pprint(sentence)

    print('\n=======Morphology========\n')

    doc.tag_morph(morph_tagger)

    for token in doc.tokens:
        pprint(token)

    print('\n')

    for sentence in doc.sents:
        sentence.morph.print()

    print('\n=======Lemmatization=========\n')

    for token in doc.tokens:
        token.lemmatize(morph_vocab)

    pprint({_.text: _.lemma for _ in doc.tokens})

    print('\n=======Syntax=========\n')

    doc.parse_syntax(syntax_parser)

    for token in doc.tokens:
        pprint(token)

    print('\n')

    for sentence in doc.sents:
        sentence.syntax.print()

    print('\n======NER========\n')

    doc.tag_ner(ner_tagger)

    for span in doc.spans:
        pprint(span)

    print('\n')

    doc.ner.print()

    print('\n=======Named entity normalization=========\n')

    for span in doc.spans:
        span.normalize(morph_vocab)

    for span in doc.spans:
        pprint(span)

    print('\n')

    pprint({_.text: _.normal for _ in doc.spans if _.text != _.normal})

    print('\n=======Named entity parsing========\n')

    for span in doc.spans:
        if span.type == PER:
            span.extract_fact(names_extractor)

    for span in doc.spans:
        pprint(span)

    print('\n')

    pprint({_.normal: _.fact.as_dict for _ in doc.spans if _.type == PER})


if __name__ == '__main__':
    main()
