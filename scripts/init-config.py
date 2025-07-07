from noppakao.models import LevelConfig
import mongoengine as me
import sys
def create_exp_table():

    LevelConfig.objects.delete()
    
    LevelConfig(
        config_id="level_config",
        level_exp_table={
            '1': 100,
            '2': 200,
            '3': 300,
            '4': 400,
            '5': 500,
        }
    ).save()

if __name__ == "__main__":
    try:
        me.connect(db="noppakaodb")
        create_exp_table()
        print("Experience table created successfully.")
    except Exception as e:
        print(f"An error occurred while creating the experience table: {e}")
    finally:
        print("Script execution completed.")