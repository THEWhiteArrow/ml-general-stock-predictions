import mongoengine as me


class Prediction(me.Document):
    date = me.DateField(required=True)  # ISO format date
    name = me.StringField(required=True)
    close = me.FloatField(required=True)

    meta = {"collection": "predictions"}  # Optional: Specify the collection name
