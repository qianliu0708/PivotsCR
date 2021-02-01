from whoosh.qparser import QueryParser
from whoosh.fields import *
from whoosh.index import open_dir
import pickle
from tqdm import tqdm
from whoosh import scoring
from whoosh.analysis import StemmingAnalyzer
from whoosh import qparser
import timeout_decorator
import json

def read_json(input_file):
    with open(input_file, "r", encoding="utf-8-sig") as f:
        content = f.read()
        return json.loads(content)
def write_json_to_file(json_object, json_file, mode='w', encoding='utf-8'):
    with open(json_file, mode, encoding=encoding) as outfile:
        json.dump(json_object, outfile, indent=4, sort_keys=True, ensure_ascii=False)

@timeout_decorator.timeout(5, use_signals=True)
def SearchQuery(searcher,query,TopN):
    results=[]
    try:
        results = searcher.search(query, limit=TopN)
        return results
    except:
        print("ignore:",query)
        pass
    return results
def ComputeRecall(QALD_dict):
    right_examples = 0
    label_uri_count = 0
    right_uri_count = 0
    find_uri_count = 0
    for id,info in tqdm(QALD_dict.items()):
        label_uri_count+=len(info['uri'])
        Flag = True
        total_uri = []
        for hit in info['search_result']:
            total_uri.extend(hit[1].split(" "))
        total_uri = list(set(total_uri))
        find_uri_count+=len(total_uri)
        for uri in info['uri']:
            if uri not in total_uri:
                Flag = False
            else:
                right_uri_count+=1
        if Flag:
            right_examples+=1
    pre = right_uri_count/find_uri_count
    recall = right_uri_count/label_uri_count
    f1 = 2*pre*recall/(pre+recall)
    print(pre,recall,f1)
    return (pre,recall,f1)
import os
import torch
if __name__ == '__main__':
    Score = "bm25"  # bm25, tfidf, tf
    Pivots_N = 10    # number of plausible English mentions
    Search_N = 500  # number of searched entities for each plausible English mention
    InputIndexDir = "data_process/DBIndex2"
    input_data_file = "Release/output_toy_de.json"
    output_data_file = "Release/output_toy_de_search.json"
    #------------------------------------------------------
    if Score == "bm25":
        myscore = scoring.BM25F()
    elif Score =="tfidf":
        myscore = scoring.TF_IDF()
    elif Score == "tf":
        myscore = scoring.Frequency()
    elif Score == "multi":
        myscore = scoring.MultiWeighting(scoring.BM25F(), id=scoring.Frequency(), keys=scoring.TF_IDF())
    else:
        myscore = scoring.BM25F()

    #---------------Input Query----------------------
    schema = Schema(title=TEXT(stored=True, analyzer=StemmingAnalyzer()),
                    content=TEXT(stored=True))
    All_Result = []
    ix = open_dir(InputIndexDir)
    sf = torch.nn.Softmax(dim=0)
    alldata = read_json(input_data_file)
    with ix.searcher(weighting=myscore) as searcher:
        parser = QueryParser("title", ix.schema,group=qparser.OrGroup)
        for item in tqdm(alldata):
            search_result= {}
            for keyword,plau_en_mentions in item['plausible_en_mentions'].items():
                per_uris = []
                per_search_result =[]
                for (word, score) in plau_en_mentions[0:Pivots_N]:
                    query = parser.parse(word)
                    results = SearchQuery(searcher, query, Search_N)
                    hit_score = [hit.score for hit in results]
                    new_score = sf(torch.Tensor(hit_score)).tolist()
                    new_score = [score * s for s in new_score]
                    hit_title = [hit['title'] for hit in results]
                    hit_content = [hit['content'] for hit in results]
                    per_search_result.extend(list(zip(hit_title, hit_content, new_score)))
                for c_result in per_search_result:
                    for auri in c_result[1].split(" "):
                        per_uris.append((auri, c_result[2]))
                searched = sorted(per_uris, key=lambda x: x[1], reverse=True)
                searched_uris = []
                searched_scores = []
                for (uri,score) in searched:
                    if uri not in searched_uris:
                        searched_uris.append(uri)
                        searched_scores.append(score)
                    if len(searched_uris)>=1000:
                        break
                search_result[keyword] = list(zip(searched_uris,searched_scores))
            item['xel_cr_results'] = search_result
        write_json_to_file(alldata,output_data_file)