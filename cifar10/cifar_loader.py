""" Code to build a cifar10 data loader """


import torch
import torchvision.transforms as transforms
import torchvision.datasets as datasets
import cifar10.cifar_resnets as cifar_resnets

import config
import os
import re


###############################################################################
#                           PARSE CONFIGS                                     #
###############################################################################

DEFAULT_DATASETS_DIR = config.DEFAULT_DATASETS_DIR
RESNET_WEIGHT_PATH   = config.RESNET_WEIGHT_PATH
DEFAULT_BATCH_SIZE   = config.DEFAULT_BATCH_SIZE
DEFAULT_WORKERS      = config.DEFAULT_WORKERS
CIFAR10_MEANS        = config.CIFAR10_MEANS
CIFAR10_STDS         = config.CIFAR10_STDS

###############################################################################
#                          END PARSE CONFIGS                                  #
###############################################################################


##############################################################################
#                                                                            #
#                               MODEL LOADER                                 #
#                                                                            #
##############################################################################

def load_pretrained_cifar_resnet(flavor=32, use_gpu=False):
    """ Helper fxn to initialize/load the pretrained cifar resnet """

    # Resolve load path
    valid_flavor_numbers = [110, 1202, 20, 32, 44, 56]
    assert flavor in valid_flavor_numbers
    weight_path = os.path.join(RESNET_WEIGHT_PATH, 'resnet%s.th' % flavor)


    # Resolve CPU/GPU stuff
    if use_gpu:
        map_location = None
    else:
        map_location = (lambda s, l: s)


    # need to modify the resnet state dict to be proper

    bad_state_dict = torch.load(weight_path, map_location=map_location)
    correct_state_dict = {re.sub(r'^module\.', '', k): v for k, v in
                          bad_state_dict['state_dict'].items()}


    classifier_net = eval("cifar_resnets.resnet%s" % flavor)()
    classifier_net.load_state_dict(correct_state_dict)

    return classifier_net



##############################################################################
#                                                                            #
#                               DATA LOADER                                  #
#                                                                            #
##############################################################################

def load_cifar_data(train_or_val, extra_args=None, dataset_dir=None,
                    normalize=False, batch_size=None):
    """ Builds a CIFAR10 data loader for either training or evaluation of
        CIFAR10 data. See the 'DEFAULTS' section in the fxn for default args
    ARGS:
        train_or_val: string - one of 'train' or 'val' for whether we should
                               load training or validation datap
        extra_args: dict - if not None is the kwargs to be passed to DataLoader
                           constructor
        dataset_dir: string - if not None is a directory to load the data from
        normalize: boolean - if True, we normalize the data by subtracting out
                             means and dividing by standard devs
    """

    ##################################################################
    #   DEFAULTS                                                     #
    ##################################################################
    # dataset directory
    dataset_dir = dataset_dir or DEFAULT_DATASETS_DIR
    batch_size = batch_size or DEFAULT_BATCH_SIZE

    # Extra arguments for DataLoader constructor
    constructor_kwargs = {'batch_size': batch_size,
                          'shuffle': True,
                          'num_workers': DEFAULT_WORKERS,
                          'pin_memory': False}
    constructor_kwargs.update(extra_args or {})

    # transform chain

    transform_list = [transforms.RandomHorizontalFlip(),
                      transforms.RandomCrop(32, 4),
                     transforms.ToTensor()]
    if normalize:
        normalizer = transforms.Normalize(mean=CIFAR10_MEANS,
                                          std=CIFAR10_STDS)
        transform_list.append(normalizer)


    transform_chain = transforms.Compose(transform_list)
    # train_or_val validation
    assert train_or_val in ['train', 'val']

    ##################################################################
    #   Build DataLoader                                             #
    ##################################################################
    return torch.utils.data.DataLoader(
            datasets.CIFAR10(root=dataset_dir, train=train_or_val=='train',
                             transform=transform_chain, download=True),
            **constructor_kwargs)




