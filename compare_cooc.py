#! /bin/env python
# encoding=utf-8
# author: nickgu 
# 

import sys
import annoy
import pydev

class ItemIndex:
    def __init__(self, filename):
        self.index = annoy.AnnoyIndex(f=100, metric='dot')

        fd = file(filename)
        for line in fd.readlines():
            row = line.strip().split(' ')
            if len(row)!=101:
                continue
            key = row[0]
            if key == '':
                continue

            key = int(key)
            vec = map(lambda x:float(x), row[1:])

            self.index.add_item(key, vec)
        
        self.index.build(32)
        
class CoocDict: 
    def __init__(self):
        self.cooc_dict = {}
        self.total_edge = 0

    def add(self, a, b):
        if a not in self.cooc_dict:
            self.cooc_dict[a] = {}
        self.cooc_dict[a][b] = self.cooc_dict[a].get(b, 0) + 1
        self.total_edge += 1

if __name__=='__main__':
    # usage:
    #  compare_cooc.py <ori_input> <w2v_embeddings>

    window_size = 2

    if len(sys.argv)!=3:
        print >> sys.stderr, 'compare_cooc.py <ori_input> <w2v_embeddings>'
        sys.exit(-1)
    emb_dict = ItemIndex(sys.argv[2])

    cooc_dict = CoocDict()
    for line in file(sys.argv[1]).readlines():
        terms = line.strip().split(' ')
        
        for idx in range(len(terms)-window_size):
            a = terms[idx]
            for j in range(window_size):
                b = terms[idx + j + 1]

                cooc_dict.add(a, b)
                cooc_dict.add(b, a)
    
    pydev.log('load cooc over.')

    hit = 0
    total = 0
    for key in cooc_dict.cooc_dict:
        if key == '':
            continue

        values = sorted(cooc_dict.cooc_dict[key].iteritems(), key=lambda x:-x[1])[:20]
        recalls, dis = emb_dict.index.get_nns_by_item(int(key), n=50, include_distances=True)

        total += len(values)
        for cooc, count in values:
            if int(cooc) in set(recalls):
                hit += 1
        
    print 'recall : %.2f%% (%d/%d)' % (hit*100./total, hit, total) 
    




