
import sys, os
import pdb
import json
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_path + '/..')
from plastering.inferencers.quiver import DummyQuiver
from plastering.inferencers.zodiac_new import ZodiacInterface
#from plastering.inferencers.zodiac_interface import ZodiacInterface
from plastering.metadata_interface import *
from plastering.workflow import *
from plastering.helper.common import *

EXP_NUM = 4

# construct a framework dict for referneces.
f_class_dict = {
    'zodiac': ZodiacInterface,
    'quiver': DummyQuiver
}

target_buildings = ['ebu3b']
target_building = target_buildings[0]
source_buildings = [target_building]
building_sentence_dict, building_label_dict, building_tagsets_dict = \
    data_loader(target_building, source_buildings)
target_srcids = list(building_tagsets_dict[target_building].keys())

base_config = {
    'target_building': target_building,
    'target_srcids': target_srcids,
    'source_buildings': source_buildings
}
zodiac_config = deepcopy(base_config)
quiver_config = deepcopy(base_config)
ebu3b_ttl = '/home/jbkoh/repo/plastering_merged/groundtruth/ebu3b_brick.ttl'
#building_ttl = 'groundtruth/{0}_brick.ttl'.format(target_building)
building_ttl = ebu3b_ttl
quiver_config['config'] = {
    'ground_truth_ttl': building_ttl
}

f_graph = {
    'zodiac': (zodiac_config, {
        'quiver': (quiver_config, {
            'zodiac': (deepcopy(zodiac_config), {})})
    })
}

for exp_id in range(0, EXP_NUM):
    # Select labeled srcids (Not all the data are labeled yet.)
    labeled_list = LabeledMetadata.objects(building=target_building)
    target_srcids = [labeled['srcid'] for labeled in labeled_list]

    workflow = Workflow(target_srcids, target_building,
                        f_class_dict, f_graph)
    workflow.learn_auto()
    history = [{
        'metrics': hist['metrics'],
        'learning_srcids': len(hist['total_training_srcids'])
    } for hist in workflow.history]
    with open('result/quiver_zodiac_{0}_{1}.json'
              .format(target_building, exp_id), 'w') as fp:
        json.dump(history, fp)
