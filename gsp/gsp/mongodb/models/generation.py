import mongoengine as me
import datetime
from gsp.mongodb.models.prediction import Prediction
from lib.logger.setup import setup_logger

logger = setup_logger(__name__)


class Generation(me.Document):
    prediction_date = me.DateField(required=True)  # ISO format date
    name = me.StringField(required=True)
    created_timestamp = me.DateTimeField(default=datetime.datetime.now(datetime.UTC))
    categorical_features = me.ListField(me.StringField(), required=True)
    label_features = me.ListField(me.StringField(), required=True)
    shift_list = me.ListField(me.IntField(), required=True)
    mwm_list = me.ListField(me.IntField(), required=True)
    days_back_to_consider = me.IntField(required=True)
    n_steps = me.IntField(required=True)
    hyper_params = me.DictField(required=False, default={})
    predictions = me.ListField(me.ReferenceField(Prediction, reverse_delete_rule=me.CASCADE), required=True)

    meta = {"collection": "generations"}  # Optional: Specify the collection name
