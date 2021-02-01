import json
from scipy.special import softmax
from tqdm import tqdm
def read_json(input_file):
    with open(input_file, "r", encoding="utf-8-sig") as f:
        content = f.read()
        return json.loads(content)
def write_json_to_file(json_object, json_file, mode='w', encoding='utf-8'):
    with open(json_file, mode, encoding=encoding) as outfile:
        json.dump(json_object, outfile, indent=4, sort_keys=True, ensure_ascii=False)
import logging
logger = logging.getLogger(__name__)
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))
import nltk
from nltk.stem import WordNetLemmatizer
import itertools
import re
from nltk.stem.snowball import SnowballStemmer
def NMS(sim_en_score_list,snow_stemmer):
    stem_words = []
    NMS_words = []
    for (en_word, sim_score) in sim_en_score_list:
        en_word = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", en_word)
        stem_en_word = snow_stemmer.stem(en_word)
        if stem_en_word not in stem_words:
            NMS_words.append((en_word, sim_score))
            stem_words.append(stem_en_word)
    return NMS_words
def MySoftmax(sim_en_words):
    [words,scores] = list(zip(*sim_en_words))
    soft_scores = softmax(scores).tolist()
    return list(zip(words,soft_scores))
Lan_Dict = {'en': 'english', 'de': 'german', 'fr': 'french', 'ru': 'russian', 'nl': 'dutch',
        'es': 'spanish', 'it': 'italian', 'ro': 'romanian', 'pt': 'portuguese'}
if __name__ == '__main__':
    is_NMS = True
    input_file = "Release/input_toy_de.json"
    output_file = "Release/output_toy_de.json"
    lan = "de"
    snow_stemmer = SnowballStemmer(language='english')
    all_data = read_json(input_file)
    for data in tqdm(all_data):
        keyword2SearchResult = {}
        for keyword,similar_words_dict in data['simwords'].items():
            sim_list = []#soft_max function
            for orig_word in keyword.lower().split(" "):
                if orig_word in similar_words_dict:
                    sim_en_words =  similar_words_dict[orig_word]
                    sim_en_words = MySoftmax(sim_en_words)# add the softmax
                    if is_NMS:
                        new_sim_en_words = NMS(sim_en_words,snow_stemmer)
                        if len(new_sim_en_words)!=0:
                            sim_list.append(new_sim_en_words)
            if len(sim_list) <6:# if the mention contains too many words, word_n should be smalle
                word_n = 10
            else:
                word_n = 5
            epwords_list = []
            scores_list = []
            for aitem in sim_list:
                temp = list(zip(*aitem[0:word_n]))
                epwords_list.append(list(temp[0]))
                scores_list.append(list(temp[1]))
            combined_words = list(itertools.product(*epwords_list))
            combined_scores = list(itertools.product(*scores_list))
            Final_combined_list = []
            for idx,(c_w,c_s) in enumerate(list(zip(combined_words,combined_scores))):
                if len(c_s)!=0:
                    c_word = " ".join(list(c_w))
                    c_score = sum(c_s)/len(c_s)
                    Final_combined_list.append((c_word,c_score))
            #---------------------------------------------------
            combined_list = sorted(Final_combined_list, key=lambda x: x[1], reverse=True)[0:20]
            keyword2SearchResult[keyword] = combined_list
        data["plausible_en_mentions"] = keyword2SearchResult
    write_json_to_file(all_data,output_file)