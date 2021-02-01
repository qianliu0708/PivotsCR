import os
import bz2
import pickle
from tqdm import tqdm
import json
def get_file_contents(filename, encoding='utf-8'):
    filename=filename.encode('utf-8')
    with open(filename, encoding=encoding) as f:
        content = f.read()
    return content
def read_json_file(filename, encoding='utf-8'):
    contents = get_file_contents(filename, encoding=encoding)
    return json.loads(contents)
def write_json_to_file(json_object, json_file, mode='w', encoding='utf-8'):
    with open(json_file, mode, encoding=encoding) as outfile:
        json.dump(json_object, outfile, indent=4, sort_keys=True, ensure_ascii=False)
def clear_uri2mention(uri2mention_dict,outputfile):
    new_uri2mention_dict = {}
    for uri, mention_list in tqdm(uri2mention_dict.items()):
        new_mention_list = []
        for mention in mention_list:
            mention = mention.replace("_", " ")
            mention = mention.replace(":", " ")
            mention = mention.replace("\"", " ")
            mention = mention.replace("\'", " ")
            mention = mention.replace("-", " ")
            mention = mention.replace(">", "")
            mention = mention.replace("@en", "")
            mention = mention.replace("/", " ")
            mention = mention.replace(",", " ")
            mention = mention.strip()
            new_mention_list.append(mention)
        final_mention_list = []
        if len(new_mention_list) > 1:
            for m1 in new_mention_list:
                Flag = True
                for m2 in new_mention_list:
                    if m1 != m2:
                        if m1 in m2:
                            Flag = False
                if Flag:
                    final_mention_list.append(m1)
        else:
            final_mention_list = new_mention_list
        new_uri2mention_dict[uri] = list(set(final_mention_list))
    pickle.dump(new_uri2mention_dict, open(outputfile, 'wb'))
    return new_uri2mention_dict
def generate_uri2mention_label(file,uri2mention_dict):
    filename = os.path.join(dir, file + ".ttl.bz2")
    source_file = bz2.open(filename, "r")
    for line in source_file:
        triple = line.decode().strip().split()
        if triple[0] == '#':
            continue
        subject = triple[0]
        object = triple[2]
        if subject not in uri2mention_dict:
            uri2mention_dict[subject] = [subject.split("/")[-1].lower().replace(">",""),
                                         object.lower()]
        else:
            uri2mention_dict[subject].append(object.lower())
            uri2mention_dict[subject].append(subject.split("/")[-1].lower().replace(">",""))
    return uri2mention_dict
def generate_uri2mention(file,uri2mention_dict):

    filename = os.path.join(dir, file + ".ttl.bz2")
    source_file = bz2.open(filename, "r")
    for line in source_file:
        triple = line.decode().strip().split()
        if triple[0] == '#':
            continue
        subject = triple[0]
        object = triple[2]
        if object not in uri2mention_dict:
            uri2mention_dict[object] = [object.strip().lower().split("/")[-1].replace(">","")]
    return uri2mention_dict
def generate_mention2uri(uri2mention_dict,output_file):
    mention2uri_dict = {}
    for k,v in tqdm(uri2mention_dict.items()):
        for mention in v:
            if mention in mention2uri_dict:
                if k not in mention2uri_dict[mention]:
                    mention2uri_dict[mention].append(k)
            else:
                mention2uri_dict[mention] = [k]
    pickle.dump(mention2uri_dict,open(output_file,'wb'))
    print(len(mention2uri_dict))
    return mention2uri_dict


def disamb_bz_process(file,orig_uri,all_used_uri):
    filename = os.path.join(dir, file + ".ttl.bz2")
    source_file = bz2.open(filename, "r")
    for line in source_file:
        triple = line.decode().strip().split()
        if triple[0] == '#':
            continue
        subject = triple[0]
        if subject in all_used_uri:
            if object in orig_uri:
                orig_uri.remove(object)
        else:
            if subject in orig_uri:
                orig_uri.remove(subject)
    return orig_uri

def generate_mention2uri(uri2mention_dict,output_file):
    mention2uri_dict = {}
    for k,v in tqdm(uri2mention_dict.items()):
        for mention in v:
            if mention in mention2uri_dict:
                if k in mention2uri_dict[mention]:
                    continue
                else:
                    mention2uri_dict[mention].append(k)
            else:
                mention2uri_dict[mention] = [k]
    pickle.dump(mention2uri_dict,open(output_file,'wb'))
    print(len(mention2uri_dict))
    return mention2uri_dict

if __name__ == '__main__':

    dir = "DBpedia_bz" # folder of download KB files
    
    output_uri2mention_file = "clean_kb_data/uri2mention_orig.pk"
    output_mention2uri_file = "clean_kb_data/mention2uri_orig.pk"
    output_uri2mention_file_dis = "clean_kb_data/uri2mention_dis.pk"
    output_mention2uri_file_dis = "clean_kb_data/mention2uri_dis.pk"

    if os.path.exists(output_mention2uri_file) and os.path.exists(output_uri2mention_file):
        mention2uri_dict = pickle.load(open(output_mention2uri_file,'rb'))
        uri2mention_dict = pickle.load(open(output_uri2mention_file,'rb'))
    else:
        labels = ['labels_en',
                  'category_labels_en']
        used_file_name = [
            'instance_types_en',
            'instance_types_transitive_en'
            # 'infobox_properties_en',
            # 'mappingbased_literals_en',
            # 'mappingbased_objects_en',
            # 'persondata_en',
            # 'infobox_properties_mapped_en',
            # 'article_categories_en',
        ]
        uri2mention_dict = {}
        for file in tqdm(labels):
            uri2mention_dict = generate_uri2mention_label(file, uri2mention_dict)
            print(len(uri2mention_dict))
        for file in tqdm(used_file_name):
            uri2mention_dict = generate_uri2mention(file, uri2mention_dict)
            print(len(uri2mention_dict))
        uri2mention_dict = clear_uri2mention(uri2mention_dict, output_uri2mention_file)
        print("uri2mention",uri2mention_dict['<http://dbpedia.org/ontology/River>'])
        mention2uri_dict = generate_mention2uri(uri2mention_dict, output_mention2uri_file)
        print("mention2uri",mention2uri_dict['river'])
    #------------uri disambiguation--------------
    disambiguation_file_name = ["redirects_en",
                                "disambiguations_en",
                                "uri_same_as_iri_en",
                                "transitive_redirects_en"]

    qald_all_data = read_json_file("qald_data/qald_all.json")
    all_used_uri = []
    for item in qald_all_data:
        all_used_uri.extend(item['uris'])

    orig_uri = set()
    for uri in uri2mention_dict.keys():
        orig_uri.add(uri)
    print(len(orig_uri))

    for filename in tqdm(disambiguation_file_name):
        orig_uri = disamb_bz_process(filename, orig_uri, all_used_uri)
        print(filename, len(orig_uri))

    new_uri2mention_dict = {}
    for uri in orig_uri:
        new_uri2mention_dict[uri] = uri2mention_dict[uri]
    pickle.dump(new_uri2mention_dict,open(output_uri2mention_file_dis,'wb'))
    generate_mention2uri(new_uri2mention_dict, output_mention2uri_file_dis)
