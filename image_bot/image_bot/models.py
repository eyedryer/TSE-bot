from tortoise import fields
from tortoise.models import Model
from datetime import datetime, timedelta


class Image(Model):
    id = fields.UUIDField(pk=True)
    user_id = fields.BigIntField(index=True)
    channel = fields.BigIntField()
    guild = fields.BigIntField(index=True)
    timestamp = fields.DatetimeField(auto_now_add=True)
    link = fields.CharField(max_length=4000)


class ImageStatistics(Model):
    user_id = fields.UUIDField(index=True)
    guild = fields.BigIntField(index=True)
    period_start = fields.DatetimeField()
    period_end = fields.DatetimeField(auto_now_add=True)
    images_sent = fields.BigIntField(default=0)

    class Meta:
        unique_together = (("user_id", "guild", "period_start", "period_end"),)


class ImageCollectionSettings(Model):
    guild = fields.BigIntField()
    collection_channel = fields.BigIntField()
    target_channel = fields.BigIntField()

    class Meta:
        unique_together = (("guild", "target_channel"),)

class ImageCollectionPeriod(Model):
    guild = fields.BigIntField(primary_key=True)
    last_change = fields.DatetimeField(default=datetime.now())