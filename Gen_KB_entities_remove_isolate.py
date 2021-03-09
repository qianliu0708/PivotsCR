# We want to remove the isolate entities, which exist in label_en and category_label_en but not exist predictions to other entities. This process is optinal.
from tqdm import tqdm
import pickle
import os
import bz2
from whoosh.analysis import StemmingAnalyzer,FancyAnalyzer,LanguageAnalyzer,StemFilter,RegexTokenizer
def clear_uri2mention(uri2mention_dict, outputfile):
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
def generate_mention2uri(uri2mention_dict, output_file):
    mention2uri_dict = {}
    for k, v in tqdm(uri2mention_dict.items()):
        for mention in v:
            if mention in mention2uri_dict:
                if k not in mention2uri_dict[mention]:
                    mention2uri_dict[mention].append(k)
            else:
                mention2uri_dict[mention] = [k]
    pickle.dump(mention2uri_dict, open(output_file, 'wb'))
    print(len(mention2uri_dict))
    return mention2uri_dict


if __name__ == '__main__':
    labels = ['labels_en',
              'category_labels_en']
    used_file_name = [
        'article_categories_en',
        'persondata_en',
        'instance_types_en',
        'infobox_properties_en',
        'mappingbased_literals_en',
        'mappingbased_objects_en',
        'infobox_properties_mapped_en',
        'instance_types_transitive_en'
    ]

    sub_pred_obj_dir = "KBs/spo_dir"
    bz_dir = "KBs"
    if not os.path.exists(sub_pred_obj_dir):
        os.makedirs(sub_pred_obj_dir)
    # ----------Gen subject predict and object pickles------------------------
    for file in tqdm(used_file_name):
        filename = os.path.join(bz_dir, file + ".ttl.bz2")
        source_file = bz2.open(filename, "r")
        count = 0
        subject_set = set()
        predicate_set = set()
        object_set = set()

        for line in source_file:
            triple = line.decode().strip().split()
            if triple[0] == '#':
                continue
            count += 1
            subject_set.add(triple[0])
            predicate_set.add(triple[1])
            object_set.add(triple[2])
        print(file, count, '----------------------')
        print('\t subject:', len(subject_set))
        print('\t predicate:', len(predicate_set))
        print('\t object:', len(object_set))
        pickle.dump(subject_set, open("{}/{}-subject.pk".format(sub_pred_obj_dir,file), 'wb'))
        pickle.dump(predicate_set, open("{}/{}-predicate.pk".format(sub_pred_obj_dir,file), 'wb'))
        pickle.dump(object_set, open("{}/{}-object.pk".format(sub_pred_obj_dir,file), 'wb'))
    # # #----------------------Finished SPO process--------------------------
    print("finished spo")
    uri_dict_file = "KBs/clean_kb_data/uri2mention_dis.pk"
    uri_dict = pickle.load(open(uri_dict_file, 'rb'))
    uri_and_itsbz = {}
    for key in uri_dict.keys():
        uri_and_itsbz[key] = []
    for file in tqdm(used_file_name):
        subject = pickle.load(open(os.path.join(sub_pred_obj_dir, file + "-subject.pk"), 'rb'))
        for uri in subject:
            if uri in uri_and_itsbz:
                uri_and_itsbz[uri].append(file)
        object = pickle.load(open(os.path.join(sub_pred_obj_dir, file + "-object.pk"), 'rb'))
        for uri in object:
            if uri in uri_and_itsbz:
                uri_and_itsbz[uri].append(file)
    pickle.dump(uri_and_itsbz, open("test.pk", 'wb'))

    count = 0
    iso_uri = set()
    for key,info in uri_and_itsbz.items():
        if len(info) == 0:
            iso_uri.add(key)
    print("iso_uri",len(iso_uri))
    new_uri_dict = {}
    ana = FancyAnalyzer()
    for uri,mention in tqdm(uri_dict.items()):
        if uri not in iso_uri:
            new_uri_dict[uri] =mention

    output_u2m = "KBs/clean_kb_data/uri2mention_dis_iso.pk"
    output_m2u = "KBs/clean_kb_data/mention2uri_dis_iso.pk"
    # pickle.dump(new_uri_dict,open(output_file,'wb'))
    print("new_uris:",len(new_uri_dict))
    new_uri2mention_dict = clear_uri2mention(new_uri_dict, output_u2m)
    mention2uri_dict = generate_mention2uri(new_uri2mention_dict, output_m2u)
    print(mention2uri_dict['river'])
