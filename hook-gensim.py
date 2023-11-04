from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# This collects all dynamically imported gensim modules and data files.
hiddenimports = (collect_submodules('gensim') + collect_submodules('gensim.models')+
                 collect_submodules('gensim.corpora')+ collect_submodules('gensim.sklearn_api')+
                 collect_submodules('gensim.summarization') + collect_submodules('gensim.parsing')+
collect_submodules('gensim.topic_coherence')+collect_submodules('gensim.scripts')+collect_submodules('gensim.viz')+
                 collect_submodules('gensim.similarities')+collect_submodules('gensim.test')


)
datas = (collect_data_files('gensim') + collect_data_files('gensim.models')+
                 collect_data_files('gensim.corpora')+ collect_data_files('gensim.sklearn_api')+
                 collect_data_files('gensim.summarization') + collect_data_files('gensim.parsing')+
collect_data_files('gensim.topic_coherence')+collect_data_files('gensim.scripts')+collect_data_files('gensim.viz')+
                 collect_data_files('gensim.similarities')+collect_data_files('gensim.test')

)