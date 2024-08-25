from tortoise import Model, fields

from models.event import EventState


class EventModel(Model):
    id = fields.IntField(pk=True)
    coefficient = fields.DecimalField(max_digits=4, decimal_places=2, description="Коэффициент")
    deadline = fields.DatetimeField(description="Дедлайн")
    state = fields.CharEnumField(EventState, description="Состояние", default=EventState.NEW)
