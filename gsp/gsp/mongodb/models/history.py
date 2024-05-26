import mongoengine as me


class History(me.Document):
    date = me.DateField(required=True)
    name = me.StringField(required=True)
    close = me.FloatField(required=True)
    volume = me.FloatField(required=True)
    open = me.FloatField(required=True)
    high = me.FloatField(required=True)
    low = me.FloatField(required=True)
