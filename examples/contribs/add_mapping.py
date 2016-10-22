# -*- coding: utf-8 -*-

from aws_vapor.dsl import Template
from aws_vapor.dsl import Metadata
from aws_vapor.dsl import Parameter
from aws_vapor.dsl import Mapping
from aws_vapor.dsl import Condition
from aws_vapor.dsl import Resource
from aws_vapor.dsl import Output
from aws_vapor.dsl import Attributes
from aws_vapor.dsl import Intrinsics
from aws_vapor.dsl import Pseudos
from aws_vapor.dsl import UserData
from aws_vapor.dsl import CfnInitMetadata


def recipe(t):
    t.mappings(Mapping('RegionMap')
        .add_category('eu-west-1').add_item('AMI', 'ami-24506250').add_item('TestAZ', 'eu-west-1a')
        .add_category('sa-east-1').add_item('AMI', 'ami-3e3be423').add_item('TestAZ', 'sa-east-1a')
        .add_category('ap-southeast-1').add_item('AMI', 'ami-74dda626').add_item('TestAZ', 'ap-southeast-1a')
        .add_category('ap-southeast-2').add_item('AMI', 'ami-b3990e89').add_item('TestAZ', 'ap-southeast-2a')
        .add_category('ap-northeast-1').add_item('AMI', 'ami-dcfa4edd').add_item('TestAZ', 'ap-northeast-1a')
    , merge=True)
