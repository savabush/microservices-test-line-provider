from tortoise import Model, fields

from models.outbox import OutboxState


class Outbox(Model):
    id = fields.IntField(pk=True)
    old_message = fields.JSONField()
    message = fields.JSONField()
    timestamp = fields.DatetimeField(auto_now_add=True)
    status = fields.CharEnumField(OutboxState, default=OutboxState.UNHANDLED)

    class Meta:
        ordering = ["-timestamp"]
