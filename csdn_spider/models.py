from peewee import *

db = MySQLDatabase('spider', host="127.0.0.1", port=3306, user="root", password="root")


class BaseModel(Model):
    class Meta:
        database = db


class Topic(BaseModel):
    title = CharField()
    content = TextField(default='')
    id = IntegerField(primary_key=True)
    author = CharField()
    create_time = DateTimeField()
    answer_nums = IntegerField(default=0)
    click_nums = IntegerField(default=0)
    praised_nums = IntegerField(default=0)
    jtl = FloatField(default=0.0)
    score = IntegerField(default=0)
    status = CharField()
    last_time = DateTimeField()


class Answer(BaseModel):
    topic_id = IntegerField()
    author = CharField()
    content = TextField(default='')
    create_time = DateTimeField()
    praised_nums = IntegerField(default=0)


class Author(BaseModel):
    name = CharField()
    id = CharField(primary_key=True)
    click_nums = IntegerField(default=0)
    original_nums = IntegerField(default=0)
    forward_nums = IntegerField(default=0)
    rate = IntegerField(default=-1)
    answer_nums = IntegerField(default=0)
    praised_nums = IntegerField(default=0)
    desc = TextField(null=True)
    industry = CharField(null=True)
    location = CharField(null=True)
    follower_nums = IntegerField(default=0)
    following_nums = IntegerField(default=0)


if __name__ == '__main__':
    db.create_tables([Topic, Answer, Author])
