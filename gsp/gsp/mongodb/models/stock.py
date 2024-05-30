import mongoengine as me
from gsp.mongodb.models.history import History


class Stock(me.Document):
    name = me.StringField(required=True)
    area = me.StringField(required=True)
    history = me.ListField(me.ReferenceField(History), required=True)

    meta = {"collection": "stocks"}  # Optional: Specify the collection name
