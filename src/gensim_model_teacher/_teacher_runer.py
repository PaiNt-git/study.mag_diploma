import os
import re
#import teacher
import _teacher2 as teacher


def tarfile_path(tfile):
    basen = tfile.getnames()[0]
    basen = re.sub(r'\([^)]*\)', '', basen)
    return (basen + '/' + basen + '-sentences.txt').replace('.tar.gz', '')


def corpus_line_callback(line):
    global Doc, segmenter, morph_tagger
    if not line:
        return line
    ret = ' '.join([x.replace('|', ' _').replace('_I-', '_I _').replace('_B-', '_B _') for x in ((line.split(' ')[1:] if line[0].isdigit else line))])
    return ret


teacher.load_train(train=True, train_file_suffixes=[
    '(1)',
    '(2)',
    '(3)',
    '(4)',
    '(5)',
], train_debug=True, workers=8, vector_size=300, max_vocab_size=500000,
    corpus_line_callback=corpus_line_callback,
    tarfile_path=tarfile_path
)  #
