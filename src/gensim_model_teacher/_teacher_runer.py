import teacher

teacher.load_train(train=True, train_file_suffixes=[
    '(1)',
    '(2)',
    '(3)',
    '(4)',
    '(5)',
], train_debug=True, workers=4, corpus_line_callback=lambda x: x.replace('|', ' _').replace('_I-', '_I _').replace('_B-', '_B _'))  #
