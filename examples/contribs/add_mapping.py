# -*- coding: utf-8 -*-

from aws_vapor.dsl import (
    Template, Parameter, Mapping, Condition, Resource, Output,
    Attributes, Intrinsics, Pseudos,
    UserData, CfnInitMetadata
)


def recipe(t):
    t.mappings(Mapping('RegionToAMI')
        .add_category('us-east-1').add_item('AMI', 'ami-xxxxxxxx')
    , merge=True)
