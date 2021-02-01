# We want to remove the isolate entities, which exist in label_en and category_label_en but not exist predictions to other entities. This process is optinal.
from tqdm import tqdm
import pickle
import os
import bz2
from data_process.gen_uris_in_KB import clear_uri2mention,generate_mention2uri
from whoosh.analysis import StemmingAnalyzer,FancyAnalyzer,LanguageAnalyzer,StemFilter,RegexTokenizer
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

    sub_pred_obj_dir = "data_process/spo_dir"
    bz_dir = "data_process/DBpedia_bz"
    if not os.path.exists(sub_pred_obj_dir):
        os.makedirs(sub_pred_obj_dir)
    #----------Gen subject predict and object pickles------------------------
    # for file in tqdm(used_file_name):
    #     filename = os.path.join(bz_dir, file + ".ttl.bz2")
    #     source_file = bz2.open(filename, "r")
    #     count = 0
    #     subject_set = set()
    #     predicate_set = set()
    #     object_set = set()
    #
    #     for line in source_file:
    #         triple = line.decode().strip().split()
    #         if triple[0] == '#':
    #             continue
    #         count += 1
    #         subject_set.add(triple[0])
    #         predicate_set.add(triple[1])
    #         object_set.add(triple[2])
    #     print(file, count, '----------------------')
    #     print('\t subject:', len(subject_set))
    #     print('\t predicate:', len(predicate_set))
    #     print('\t object:', len(object_set))
    #     pickle.dump(subject_set, open("{}/{}-subject.pk".format(sub_pred_obj_dir,file), 'wb'))
    #     pickle.dump(predicate_set, open("{}/{}-predicate.pk".format(sub_pred_obj_dir,file), 'wb'))
    #     pickle.dump(object_set, open("{}/{}-object.pk".format(sub_pred_obj_dir,file), 'wb'))
    # # #----------------------Finished SPO process--------------------------
    # exit()
    uri_dict_file = "data_process/FinalData/uri2mention.pk"
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

    pickle.dump(new_uri_dict,open("uri2mention_dis2.pk",'wb'))
    print("new_uris:",len(new_uri_dict))
    new_uri2mention_dict = clear_uri2mention(new_uri_dict, "uri2mention_dis2.pk")
    mention2uri_dict = generate_mention2uri(new_uri2mention_dict, "mention2uri_dis2.pk")
    print(mention2uri_dict['river'])
