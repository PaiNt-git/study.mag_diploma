import teacher

teacher.load_train(train=True, train_debug=True, workers=12, corpus_line_callback=lambda x: x.replace('|', ' _').replace('_I-', '_I _').replace('_B-', '_B _'))  #
