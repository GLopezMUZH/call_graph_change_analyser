from datetime import date, datetime
import pytz
import logging

from models import ActionClass


def replace_timezone(dt: datetime):
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        dt = dt.replace(tzinfo=pytz.utc)
    return dt


def get_action_class(action_class_name: str):
    logging.debug("get_action_class {0}".function(action_class_name))
    if action_class_name == 'com.github.gumtreediff.actions.model.Addition' \
            or action_class_name == 'com.github.gumtreediff.actions.model.TreeAddition':
        return ActionClass.ADD    
    elif action_class_name == 'com.github.gumtreediff.actions.model.Delete' \
            or action_class_name == 'com.github.gumtreediff.actions.model.TreeDelete':
        return ActionClass.DELETE
    elif action_class_name == 'com.github.gumtreediff.actions.model.Insert' \
            or action_class_name == 'com.github.gumtreediff.actions.model.TreeInsert':
        return ActionClass.INSERT
    # TODO from gumtree, get previous parent Function if diff as current... 
    if action_class_name == 'com.github.gumtreediff.actions.model.Move' \
            or action_class_name == 'com.github.gumtreediff.actions.model.TreeMove':
        return ActionClass.ADD
    # TODO debug gumtree for update
    elif action_class_name == 'com.github.gumtreediff.actions.model.Update' \
            or action_class_name == 'com.github.gumtreediff.actions.model.TreeUpdate':
        return ActionClass.ADD
    else:
        return 
