import mongoengine as me


class History(me.Document):
    date = me.DateTimeField(required=True)
    open = me.FloatField(required=True)
    high = me.FloatField(required=True)
    low = me.FloatField(required=True)
    close = me.FloatField(required=True)
    adj_close = me.FloatField(required=True)
    volume = me.IntField(required=True)

    meta = {"collection": "histories"}  # Optional: Specify the collection name
