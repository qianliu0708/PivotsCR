# PivotsCR
We released the used **QALD data** and **codes** of the proposed method in the paper entitled "Pivots-based Candidate Retrieval for Cross-lingual Entity Linking".

We also released our code to process knowledge base (DBpedia) for reference.

Toy examples and files are provided to run our method.

## QALD Data

**1. Cross-lingual entity linking data**

The original QALD 4-9 datasets are available [here](https://github.com/ag-sc/QALD).  

We processed these datasets for cross-lingual entity linking task. We merged multilingual QALD 4-9 data. These examples are cross-lingual question answering over different knowledge bases. We extracted examples which can be execute on DBpedia 2016-10. The result files are in **QALD_data** folder:
 - **QALD_multilingual4-9.json**. This file contains all extracted examples from QALD 4-9. It can be used for cross-lingual entity linking (XEL) and cross-lingual question answering over knowledge base (X-KBQA). 
 
 - **QALD_XEL folder**. We splited the previous file into different languages, including German (de), French (fr), Russian (ru), Dutch (nl), Spanish (es), Italian (it), Romanian (ro), and Portuguese (pt), and extracted information related to XEL task. Below are several examples: 
 ```ruby
    # an example in QADL_data/QALD_XEL/qald_de.json
    {
        "context": "Wer ist der König der Niederlande?",
        "id": 562,
        "keywords": [
            "König",
            "Niederlande"
        ],
        "uris": [
            "<http://dbpedia.org/ontology/Royalty>",
            "<http://dbpedia.org/resource/Netherlands>"
        ]
    },
    # an example in QADL_data/QALD_XEL/qald_ro.json
    {
        "context": "Dă-mi toate prenumele feminine.",
        "id": 30,
        "keywords": [
            "feminine",
            "prenume"
        ],
        "uris": [
            "<http://dbpedia.org/resource/Female>",
            "<http://dbpedia.org/ontology/GivenName>"
        ]
    }
```

**2. Knowledge base**

Notable, the used knowledge base for QALD dataset is DBpedia 2016-10. This knowledge base can be downloadedfrom this [link](https://wiki.dbpedia.org/downloads-2016-10).

We provided our code to download this knowledge base and extract its all entities (~6 million) for reference. The results files (i.e., the dictionary of all uris in KB) are available in this [link](https://drive.google.com/drive/folders/1p6U03OmIvk5JCDAEe9ryWx3UJ21nM6kL?usp=sharing).
The details of our code: 
 ``` ruby
# download the KB files from http://downloads.dbpedia.org/2016-10/core-i18n/en/ and put them in "DBpedia_bz" folder
# mkdir DBpedia_bz
# cp download.sh DBpedia_bz/
# dos2unix download.sh
bash download.sh

# generate all entities in these KB files
python Gen_KB_entities.py 	
# input: the name of folder contains KB files, i.e., "DBpedia_bz"
# output: DBpedia_bz/clean_kb_data, 
# uri2mention_dis.pk and mention2uri_dis.pk are used, which contain 6477011 and 6472104 items, respectively.
# uri2mention_dis.pk is a dictionary contains all entities and their corresponding aliases. For example, 
# {'<http://dbpedia.org/resource/World_of_Miracles>': 'world miracles', 
#  '<http://dbpedia.org/resource/Antique_Beat>':'antique beat',...}
```
Notes: 
1) If we named the input folder as DBpedia_bz, the output files are in DBpedia_bz/clean_kb_data. uri2mention_dis.pk and mention2uri_dis.pk are used in experiments, which contain 6477011 and 6472104 items, respectively. uri2mention_dis.pk is a dictionary contains all entities and their corresponding aliases. 
2) QALD dataset is used for question answering task over knowlege base. Thus, the isolate nodes(which do not have relations to other nodes) are not used in the task. In our implement, we removed the "isolate" nodes. The code of this step is Gen_KB_entities_remove_isolate.py. The output_file is named as uri2mention_dis_iso.pk, and it contains 6002089 entities.
## Code

The code to implement our proposed "pivots-based candidate retrieval" method.

**Step1:** Preparing cross-lingual entity linking data and the corresponding Knowledge Base.

In this paper, we used the DBpedia 2016-10. We provided our code to download this knowledge base and extract its all entities (~6 million) for reference. E.g., 
```ruby
bash download.sh		# download the used KB files
python Gen_KB_entities.py 	# generate all entities in KB
```
**Step2:** Generating aligned word embedding for source language (e.g., German) and target language (English). There are two optional methods:
 - Directly download the published aligned word vectors by fastText from [here](https://fasttext.cc/docs/en/aligned-vectors.html). E.g.,
	```ruby
	# download aligned word embeddings
	wget https://dl.fbaipublicfiles.com/fasttext/vectors-aligned/wiki.en.align.vec
	wget https://dl.fbaipublicfiles.com/fasttext/vectors-aligned/wiki.de.align.vec
	```
 - Or, employ [MUSE](https://github.com/facebookresearch/MUSE) to align monolingual word embeddings:
	- **supervised**: using a bilingual dictionary to learn a mapping from the source to the target space.
	- **unsupervised**: without any parallel data or anchor point, learn a mapping from the source to the target space using adversarial training and (iterative) Procrustes refinement.
	
Notable, we used the MUSE method to generate aligned word embeddings in the paper, and other multilingual word representation methods also can be used.

**Step3:** Generate Plausible English Mentions

 - Search the most similar English words for each word in a source-language mention. In this paper, we used the CSLS (Cross-domain similarity local scaling) proposed by [MUSE](https://github.com/facebookresearch/MUSE) (e.g., the contextual similarity mearsure "csls_knn_" in src/evaluation/word_translation.py). Alternatively, you can employ the cosine similarity of vectors to measure the word similarity and [GENSIM](https://radimrehurek.com/gensim/models/keyedvectors.html) is suggested. E.g.,
	 ```ruby
	 # generate similar words
	 import gensim
	 en_word_vectors = gensim.models.KeyedVectors.load_word2vec_format("wiki.en.align.vec", binary=False)
	 de_word_vectors = gensim.models.KeyedVectors.load_word2vec_format("wiki.de.align.vec", binary=False)

	de_mention = "sieben wunder der antiken welt"# means--Seven Wonders of the Ancient World
	 for word in de_mention.split(" "):
		print(word, en_word_vectors.similar_by_vector(de_word_vectors[word],topn=5))
	# output:
	# sieben [('seven', 0.6118286848068237), ('six', 0.5721521377563477), ('eight', 0.5684829354286194), ('nine', 0.5678043961524963), ('five', 0.565507173538208)]
	# wunder [('miracle', 0.4607662260532379), ('miracles', 0.38330158591270447), ('‘miracle', 0.34849193692207336), ('miraculous', 0.3447709083557129), ('miracl', 0.3389461040496826)]
	# ...
	# welt [('world', 0.4459209144115448), ('world—', 0.39981919527053833), ('worlds', 0.39319226145744324), ('world,', 0.3859684467315674), ('world—i', 0.3614097535610199)]
	 ```

 - Clean the similar words using NMS algorithm, and generate a set of plausible English mentions for each source mention.
	 ```ruby
	 python SemanticNMS.py [input_file] [output_file]
	 
	 # toy examples:
	 # input file: toydata/input_de.json
	 # output file: toydata/plausible_de.json
	 # plausible English mentions of "sieben wunder der antiken welt":
	 # ('seven miracle the antiquity world', 0.05677208132856291)
	 # ('seven miracle the ancient world', 0.05670805866980465)...
	 ```
 
**Step4:**  Lexical Retrieval and Generate TopN Candidates	
 - Build search index for all entities.  In this paper, we build the index of all entities in KB using [Whoosh](https://whoosh.readthedocs.io/en/latest/index.html), which is a library of classes and functions for indexing text and then searching the index. E.g.,
  	```ruby
    # pip install Whoosh
	python Build_KB_Index.py # This step took over 2 hours in our experiments.
	
	# input file: a dictionary of all entities in KB. E.g.,
	# {'<http://dbpedia.org/resource/World_of_Miracles>': 'world miracles', '<http://dbpedia.org/resource/Antique_Beat>':'antique beat'}
	# output: the Index
	``` 
 - Search the plausible mentions, return top-1000 candidates. E.g., 
 	```ruby
	 python LexicalSearch.py
	 # input_file: toydata/plausible_de.json, the path of KB Index
	 # output_file: toydata/output_de.json. E.g., the "xel_cr_results" of German mention "sieben wunder der antiken welt" include:
	 # [('<http://dbpedia.org/resource/Category:Seven_Wonders_of_the_Ancient_World>', 0.04279009208377855),
	 # ('<http://dbpedia.org/resource/Seven_Wonders_of_the_Ancient_World>', 0.04279009208377855),
	 # ('<http://dbpedia.org/resource/World_of_Miracles>', 0.035886112485214505)...]
	``` 
