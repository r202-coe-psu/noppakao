import mongoengine as me
import datetime

class LevelConfig(me.Document):
    meta = {"collection": "configs"}
    config_id = me.StringField(required=True, unique=True, default="level_config")
    level_exp_table = me.DictField(required=True, default={
        1: 100,
        2: 200,
        3: 300,
        4: 400,
        5: 500,
    })

    def __str__(self):
        return f"LevelConfig(level={self.level}, score={self.score})"