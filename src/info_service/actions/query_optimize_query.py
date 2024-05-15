import os
import time
import json
import asyncio
import itertools
import math

import gensim
import snowballstemmer

from gensim.models.phrases import Phrases, Phraser

from pprint import pprint

from itertools import chain

from copy import copy

from collections import OrderedDict

from PyQt5 import QtCore, QtGui, QtWidgets

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
from natasha.syntax import token_deps

from navec import Navec


from info_service.db_base import Session, QuestAnswerBase

from info_service.db_utils import togudb_serializator

from info_service.actions._answers_utils import *


SENT_MEMBERS = {
    'root': 'сказуемое',
    'nsubj': 'подлежащее',
    'amod': 'определение',
    'advmod': 'обстоятельство',
    'nmod': 'дополнение',
    'obl': 'обособление',
    'obj': 'обособленое дополнение',
    'xcomp': 'инфинитивный комплемент (открытый клаузальный комплемент) / дополнение вторичной предикации',
    'acl': 'отношение(подлежащее)',
    'advcl': 'отношение(сказуемое)',
    'det': 'определитель, уточнение',
    'flat:name': 'обращение',
    'appos': 'уточнение',
    'nsubj:pass': 'подлежащее пассива',
    'ccomp': 'клаузальный комплемент',
}


RUS_POS = {
    'S': 'сущ.',
    'A': 'прил.',
    'NUM': 'числ.',
    'A-NUM': 'числ. прил.',
    'V': 'глаг.',
    'ADV': 'нар.',
    'PRAEDIC': 'предикатив',
    'PARENTH': 'вводное',
    'S-PRO': 'мест. сущ.',
    'A-PRO': 'мест. прил.',
    'ADV-PRO': 'мест. нареч.',
    'PRAEDIC-PRO': 'мест. предик.',
    'PR': 'предлог',
    'PART': 'частица',
    'INIT': 'инит',
    'NONLEX': 'нонлекс',

    'DET': 'мест.',
    'CCONJ': 'союз',

    'ADP': 'предлог',
    'NOUN': 'сущ.',
    'ADJ': 'прил.',
    'ADJF': 'имя прилагательное (полное)',
    'ADJS': 'имя прилагательное (краткое)',
    'COMP': 'компаратив',
    'VERB': 'глагол (личная форма)',
    'INFN': 'глагол (инфинитив)',
    'PRTF': 'причастие (полное)',
    'PRTS': 'причастие (краткое)',
    'GRND': 'деепричастие',
    'NUMR': 'числ.',
    'ADVB': 'нар.',
    'NPRO': 'местоимение-существительное',
    'PRED': 'предикатив',
    'PREP': 'предлог',
    'CONJ': 'союз',
    'PRCL': 'частица',
    'INTJ': 'междометие',

}


class ModifNavec(Navec):
    @property
    def as_gensim(self):
        from gensim.models import KeyedVectors
        model = KeyedVectors(self.pq.dim)
        weights = self.pq.unpack()  # warning! memory heavy
        model.add_vectors(self.vocab.words, weights)
        return model


ru_stemmer = snowballstemmer.stemmer('russian')


def get_has_in_postgres_TF_IDF(lexem, only_questions=False):
    session = Session()
    que_type = 0
    if only_questions:
        que_type = 1

    sqlstr = '''

        CREATE OR REPLACE FUNCTION public.telegram_bot_link_base_get_words(query_type int)
        RETURNS SETOF RECORD LANGUAGE plpgsql as
        '
        DECLARE
          answer RECORD;
        BEGIN
            IF query_type = 0 THEN
              FOR answer IN SELECT id FROM telegram_bot_link_base
              LOOP
                    RETURN QUERY select answer.id as ans_id, lexems.word, lexems.nentry num_in_doc, lexems.weight_norm, (select SUM(allexem.cnt)
                    from
                    (
                    SELECT count(*) cnt FROM ts_stat(''SELECT search_vector FROM telegram_bot_link_base where telegram_bot_link_base.id=''||answer.id::VARCHAR , ''ABCD'')
                    ) allexem) from
                    (
                    SELECT 1.0 as weight_norm,  * FROM ts_stat(''SELECT search_vector FROM telegram_bot_link_base where telegram_bot_link_base.id=''||answer.id::VARCHAR, ''A'')
                    union all
                    SELECT 0.4 as weight_norm, * FROM ts_stat(''SELECT search_vector FROM telegram_bot_link_base where telegram_bot_link_base.id=''||answer.id::VARCHAR, ''B'')
                    union all
                    SELECT 0.2 as weight_norm,  * FROM ts_stat(''SELECT search_vector FROM telegram_bot_link_base where telegram_bot_link_base.id=''||answer.id::VARCHAR, ''C'')
                    union all
                    SELECT 0.1 as weight_norm,  * FROM ts_stat(''SELECT search_vector FROM telegram_bot_link_base where telegram_bot_link_base.id=''||answer.id::VARCHAR, ''D'')
                    ) lexems;
              END LOOP;
            ELSE
              FOR answer IN SELECT id FROM telegram_bot_link_base
              LOOP
                    RETURN QUERY select answer.id as ans_id, lexems.word, lexems.nentry num_in_doc, lexems.weight_norm, (select SUM(allexem.cnt)
                    from
                    (
                    SELECT count(*) cnt FROM ts_stat(''SELECT q_search_vector FROM telegram_bot_link_base where telegram_bot_link_base.id=''||answer.id::VARCHAR , ''AB'')
                    ) allexem) from
                    (
                    SELECT 1.0 as weight_norm,  * FROM ts_stat(''SELECT q_search_vector FROM telegram_bot_link_base where telegram_bot_link_base.id=''||answer.id::VARCHAR, ''A'')
                    union all
                    SELECT 0.4 as weight_norm, * FROM ts_stat(''SELECT q_search_vector FROM telegram_bot_link_base where telegram_bot_link_base.id=''||answer.id::VARCHAR, ''B'')
                    ) lexems;
              END LOOP;
            END IF;
            RETURN;
        END;
        '

    '''
    results = session.execute(sqlstr)
    session.commit()

    sqlstr = '''

        select count(*) from telegram_bot_link_base

    '''.format(lexem)
    alldocs = session.execute(sqlstr).scalar()

    sqlstr = '''

        select * from (
        SELECT * FROM public.telegram_bot_link_base_get_words({que_type}) f(ans_id int, word text, num_in_doc int4, weight_norm numeric, summa numeric)
        ) lemms where length(lemms.word)>1 and not isnumeric(lemms.word) and  lemms.word='{lexem}'
        ORDER BY summa DESC, weight_norm DESC, word

    '''.format(lexem=lexem, que_type=que_type)

    results = session.execute(sqlstr).fetchall()
    if not len(results):
        return None, 0
    results = map(dict, results)

    bydocs_tf = [x['num_in_doc'] / x['summa'] for x in results]

    # ndoc - Ответов с вхождением
    # nentry - Вхождений за всю базу

    if not only_questions:
        sqlstr = '''

            select distinct * from
            (
                SELECT 'questions' as col_name, 'A' as weight, 1.0 as weight_norm,  * FROM ts_stat('SELECT search_vector FROM telegram_bot_link_base  ', 'A')
                union all
                SELECT 'abstract' as icolumn, 'B' as  weight, 0.4 as weight_norm, * FROM ts_stat('SELECT search_vector FROM telegram_bot_link_base  ', 'B')
                union all
                SELECT 'keywords' as icolumn, 'C' as weight, 0.2 as weight_norm,  * FROM ts_stat('SELECT search_vector FROM telegram_bot_link_base  ', 'C')
                union all
                SELECT 'name' as icolumn, 'D' as weight, 0.1 as weight_norm,  * FROM ts_stat('SELECT search_vector FROM telegram_bot_link_base  ', 'D')

            ) lemms where length(lemms.word)>1 and not isnumeric(lemms.word) and lemms.word='{lexem}'
            ORDER BY weight_norm DESC, nentry DESC, ndoc DESC, word

        '''.format(lexem=lexem)
    else:
        sqlstr = '''

            select distinct * from
            (
                SELECT 'questions' as col_name, 'A' as weight, 1.0 as weight_norm,  * FROM ts_stat('SELECT q_search_vector FROM telegram_bot_link_base  ', 'A')
                union all
                SELECT 'keywords' as icolumn, 'B' as  weight, 0.4 as weight_norm, * FROM ts_stat('SELECT q_search_vector FROM telegram_bot_link_base  ', 'B')

            ) lemms where length(lemms.word)>1 and not isnumeric(lemms.word) and lemms.word='{lexem}'
            ORDER BY weight_norm DESC, nentry DESC, ndoc DESC, word

        '''.format(lexem=lexem)

    results = session.execute(sqlstr).first()
    results = dict(results)

    idf = math.log(alldocs / results['ndoc'])

    bydocs_tf_idf = [float(tf) * float(idf) for tf in bydocs_tf]

    mean_tf_idf = sum(bydocs_tf_idf) / float(len(bydocs_tf_idf))

    return results, mean_tf_idf


def main(text_query: str, only_questions=True):
    global ru_stemmer

    from info_service import actions

    allstr = ''

    all_tokens_with_synonims = []
    sentence_members = []

    try:

        doc = Doc(text_query)

        morph_vocab = MorphVocab()
        segmenter = Segmenter()

        emb = NewsEmbedding()

        morph_tagger = NewsMorphTagger(emb)
        syntax_parser = NewsSyntaxParser(emb)
        ner_tagger = NewsNERTagger(emb)

        doc.segment(segmenter)

        doc.tag_morph(morph_tagger)
        doc.parse_syntax(syntax_parser)
        doc.tag_ner(ner_tagger)

        doc_spans = list(doc.spans)
        spchains = list(itertools.chain.from_iterable(map(lambda x: getattr(x, 'tokens', []), doc_spans)))
        for i, row in enumerate(doc_spans):
            row.normalize(morph_vocab)

        bigrammpath = os.path.join('..' if __name__ == '__main__' else os.getcwd(), 'data_for_program/_saved_models/aij-wikiner-ru-wp3.gz_bigram.pkl')
        bigram_reloaded = Phraser.load(bigrammpath)
        bigrams = []
        for sentence in doc.sents:
            phrases = bigram_reloaded[[x.text.lower() for x in sentence.tokens]]
            bigrams.extend([x for x in phrases if ' ' in x])
        bigrams_listoflist = [x.split(' ') for x in bigrams]
        has_bigram = []
        for sentence in doc.sents:
            for token in sentence.tokens:
                bigrams_intersect = [' '.join(x) for x in bigrams_listoflist if token.text.lower() in x]
                if len(bigrams_intersect):
                    setattr(token, '_is_bigram', True)
                    for bigram_text in bigrams_intersect:
                        if bigram_text not in has_bigram:
                            has_bigram.append(bigram_text)
                else:
                    setattr(token, '_is_bigram', False)

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

        def get_childs(parent_token, alltokens, nesting_level=0):
            rt = list(filter(lambda x: (x.head_id == parent_token.id), alltokens))
            if nesting_level > 0:
                rt.extend(itertools.chain.from_iterable([get_childs(x, alltokens, nesting_level=nesting_level - 1) for x in rt]))
            return rt

        for sentence in doc.sents:

            sentence_members.append({
                'main': [],
                'additional': [],
                'first_level_cut': [],
            })

            for token in sentence.tokens:

                # синтаксический разбор членов предлоежения
                if token.rel in SENT_MEMBERS.keys():
                    virt_token = token
                    _is_ner = False
                    if token.id in [x.id for x in spchains]:
                        for span in doc_spans:
                            if token.id in [x.id for x in span.tokens]:
                                virt_token = copy(span)
                                setattr(virt_token, 'rel', token.rel)
                                setattr(virt_token, 'start', token.start)
                                setattr(virt_token, 'id', token.id)
                                setattr(virt_token, 'head_id', token.head_id)
                                _is_ner = True

                    setattr(virt_token, '_is_ner', _is_ner)

                    has_root = len([x for x in sentence.tokens if x.rel == 'root']) > 0
                    has_nsubj = len([x for x in sentence.tokens if x.rel == 'nsubj']) > 0

                    if (virt_token.rel in ('root', 'nsubj', 'nsubj:pass')) or (not has_root and virt_token.rel == 'advcl') or (not has_nsubj and virt_token.rel == 'acl'):
                        sentence_members[-1]['main'].append(virt_token)
                    else:
                        sentence_members[-1]['additional'].append(virt_token)

                    if virt_token._is_ner or virt_token._is_bigram:
                        has_tok_ids = [x.id for x in sentence_members[-1]['first_level_cut']]
                        if virt_token.id not in has_tok_ids:
                            sentence_members[-1]['first_level_cut'].append(virt_token)

                    if (virt_token.rel == 'root') or (not has_root and virt_token.rel == 'advcl') or (virt_token.id == virt_token.head_id and virt_token.rel != 'punct'):

                        sentence_members[-1]['first_level_cut'].append(virt_token)

                        if (virt_token.rel == 'root' and not has_nsubj):
                            sentence_members[-1]['first_level_cut'].extend(get_childs(virt_token, sentence.tokens, nesting_level=2))
                        elif has_root and has_nsubj:
                            sentence_members[-1]['first_level_cut'].extend(get_childs(virt_token, sentence.tokens, nesting_level=1))
                        elif has_root and not has_nsubj:
                            sentence_members[-1]['first_level_cut'].extend(get_childs(virt_token, sentence.tokens, nesting_level=0))
                        elif not has_root and virt_token.id == virt_token.head_id and virt_token.rel != 'punct':
                            sentence_members[-1]['first_level_cut'].extend(get_childs(virt_token, sentence.tokens, nesting_level=1))

                        sentence_members[-1]['first_level_cut'] = list(filter(lambda x: (x.rel in SENT_MEMBERS.keys() and
                                                                                         x.pos in ('NOUN', 'ADJ', 'VERB', 'INFN', 'PROPN')),
                                                                              sentence_members[-1]['first_level_cut']))

                token.lemmatize(morph_vocab)

                _gensim_synonyms = []
                if token.pos not in (
                    'PUNCT',    # знаки препинания
                    'ADP',      # предлог
                    'CCONJ',    # союз
                    'DET',      # местоимение
                ):
                    try:
                        if token.id not in [x.id for x in spchains]:
                            _gensim_synonyms = (gensim_model.most_similar(positive=[token.lemma]) if token.lemma and len(token.text) > 2 else [])
                    except KeyError:
                        pass
                    _gensim_synonyms.sort(key=lambda x: x[1], reverse=True)

                token_info = {}
                token_info['_natasha_token'] = token
                token_info['POS'] = token.pos
                token_info['id'] = token.id

                token_info['text'] = token.text
                token_info['ann_lemma'] = token.lemma
                token_info['ann_lexem'] = ru_stemmer.stemWord(token.text).lower()
                token_info['pg_lexem'] = actions.db_get_searchterm_get_stemming(token.text, logging=False) if token.text else None
                token_info['weight'] = 1.0
                token_info['synonyms'] = []

                _has_that_lemma = []

                for syn, weight in _gensim_synonyms:
                    syn_norm = morph_vocab.lemmatize(syn, token.pos, token.feats)
                    if syn_norm in _has_that_lemma:
                        continue
                    syn_info = {}

                    syn_info['_prime_token_info'] = token_info

                    syn_info['POS'] = token.pos
                    syn_info['id'] = token.id

                    syn_info['text'] = syn
                    syn_info['ann_lemma'] = syn_norm
                    syn_info['ann_lexem'] = ru_stemmer.stemWord(syn_norm).lower()
                    syn_info['pg_lexem'] = actions.db_get_searchterm_get_stemming(syn_norm, logging=False) if syn_norm else None
                    syn_info['weight'] = weight

                    token_info['synonyms'].append(syn_info)

                    _has_that_lemma.append(syn_norm)

                all_tokens_with_synonims.append(token_info)

            try:
                sentence_members[-1]['first_level_cut'] = sorted(sentence_members[-1]['first_level_cut'], key=lambda x: x.start)
                _uniq_tokens_ids = []
                _uniq_tokens = []
                _has_base_tokens = []
                for tk in sentence_members[-1]['first_level_cut']:
                    if tk.id not in _uniq_tokens_ids:
                        _uniq_tokens_ids.append(tk.id)
                        if not len([x for x in _has_base_tokens if x in tk.text]):
                            _uniq_tokens.append(tk)
                            _has_base_tokens.extend((tk.text.split(' ') if tk.text.count(' ') else [tk.text]))
            except Exception as e:
                print(e)

            sentence_members[-1]['first_level_cut'] = _uniq_tokens

        def get_ext_token_by_id(tid):
            for token_info in all_tokens_with_synonims:
                if token_info['_natasha_token'].id == tid:
                    return token_info

        opt_tokens_ = [get_ext_token_by_id(x.id) for x in itertools.chain.from_iterable(map(lambda x: x['first_level_cut'], sentence_members))]

        opt_tokens = []

        for token in opt_tokens_:

            pg_lexem, tf_idf = get_has_in_postgres_TF_IDF(token['pg_lexem'], only_questions)

            ten_pers = 0 if tf_idf <= 0 else tf_idf * 0.1

            synonyms = list(filter(lambda x: (bool(x['pg_lexem']) and x['pg_lexem'] != token['pg_lexem']), token['synonyms']))

            if token['pg_lexem'] and len(synonyms):

                has_tf_idf_tokens = False
                for synonym in synonyms:
                    pg_lexem_syn, tf_idf_syn = get_has_in_postgres_TF_IDF(synonym["pg_lexem"], only_questions)
                    if pg_lexem_syn and tf_idf_syn > tf_idf + ten_pers:
                        opt_tokens.append(synonym)
                        has_tf_idf_tokens = True
                        break

                if not has_tf_idf_tokens:
                    if tf_idf > 0.0:
                        opt_tokens.append(token)

            else:
                if tf_idf > 0.0:
                    opt_tokens.append(token)

        allstr = ' '.join([x['pg_lexem'] for x in opt_tokens])
        first_allstr = allstr
        res = actions.db_list_search_entries(allstr, category=None, sort=False, only_questions=only_questions)

        # Проверка и Обрезка дополнительных членов предложения
        if not len(res):
            for add_sm in itertools.chain.from_iterable(map(lambda x: x['additional'], sentence_members)):

                add_sm = get_ext_token_by_id(add_sm.id)

                if add_sm['id'] in [x['id'] for x in opt_tokens]:
                    # Проверим исходный член предлоежения
                    opt_tokens_prime = [(x.get('_prime_token_info', x) if (x['id'] == add_sm['id']) else x) for x in opt_tokens]
                    allstr = ' '.join([x['pg_lexem'] for x in opt_tokens_prime])
                    res = actions.db_list_search_entries(allstr, category=None, sort=False, only_questions=only_questions)
                    if not len(res):
                        # Уберем дополнительный член предлоежения
                        opt_tokens = list(filter(lambda x: x['id'] != add_sm['id'], opt_tokens))
                        allstr = ' '.join([x['pg_lexem'] for x in opt_tokens])
                        res = actions.db_list_search_entries(allstr, category=None, sort=False, only_questions=only_questions)
                        if len(res):
                            break
                    else:
                        break

        # Оставшиеся члены предложения по пробуем заменить исходными токенами
        if not len(res):
            for i in range(opt_tokens):
                opt_tokens = [(x.get('_prime_token_info', x) if (x['id'] == opt_tokens[i]['id']) else x) for x in opt_tokens]
                allstr = ' '.join([x['pg_lexem'] for x in opt_tokens])
                res = actions.db_list_search_entries(allstr, category=None, sort=False, only_questions=only_questions)
                if len(res):
                    break
            else:
                allstr = first_allstr

    except Exception as e:
        print(e)

    print(allstr)
    return allstr
