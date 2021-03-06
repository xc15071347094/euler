# Copyright 2020 Alibaba Group Holding Limited. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import json
import urllib
import zipfile
import tqdm

from tf_euler.python.dataset.sage_util import *
from tf_euler.python.dataset.base_dataset import DataSet

current_dir = os.path.dirname(os.path.realpath(__file__))
ppi_dir = os.path.join(current_dir, 'ppi')


class ppi(DataSet):

    def __init__(self, data_dir=ppi_dir, data_type='all'):
        super(ppi, self).__init__(data_dir, data_type)
        self.source_url = 'http://snap.stanford.edu/graphsage/ppi.zip'
        self.origin_files = ['ppi-class_map.json',
                             'ppi-feats.npy',
                             'ppi-G.json',
                             'ppi-id_map.json',
                             'ppi-walks.txt']
        self.max_node_id = 56944
        self.train_node_type = ['train']
        self.train_edge_type = ['train']
        self.total_size = 56944
        self.all_node_type = -1
        self.all_edge_type = ['train', 'train_removed']
        self.id_file = os.path.join(data_dir, 'ppi_test.id')
        self.feature_idx = 'feature'
        self.feature_dim = 50
        self.label_idx = 'label'
        self.label_dim = 121
        self.num_classes = 121
        self.test_start_num = 51420

    def download_data(self, source_url, out_dir):
        ppi_zip_dir = os.path.join(out_dir, 'ppi.zip')
        out_dir = os.path.join(out_dir, '..')
        DataSet.download_file(source_url, ppi_zip_dir)
        with zipfile.ZipFile(ppi_zip_dir) as ppi_zip:
            print('unzip data..')
            ppi_zip.extractall(out_dir)

    def convert2json(self, convert_dir, out_dir):
        prefix = os.path.join(convert_dir, 'ppi')
        G, feats, id_map, walks, class_map = load_data(prefix)
        out_test = open(self.id_file, 'w')
        with open(out_dir, 'w') as out:
            buf = {}
            buf["nodes"] = []
            buf["edges"] = []
            for node_id in tqdm.tqdm(G.nodes()):
                node_buf = {}
                idx = id_map[node_id]
                node_buf['id'] = idx
                node_buf['type'] = get_node_type(G.node[node_id])
                if node_buf['type'] == 'test':
                    out_test.write(str(idx) + '\n')
                node_buf['weight'] = len(G[node_id])
                node_buf['features'] = [{}, {}]
                node_buf['features'][0]['name'] = 'label'
                node_buf['features'][0]['type'] = 'dense'
                node_buf['features'][0]['value'] = class_map[node_id]
                node_buf['features'][1]['name'] = 'feature'
                node_buf['features'][1]['type'] = 'dense'
                node_buf['features'][1]['value'] = list(feats[idx])
                buf["nodes"].append(node_buf)
                for dst_id in G[node_id]:
                    ebuf = {"src": idx,
                            "dst": id_map[dst_id],
                            "type": get_edge_type(G[node_id][dst_id]),
                            "weight": 1,
                            "features": []
                            }
                    buf["edges"].append(ebuf)
            out.write(json.dumps(buf))
        out_test.close()
