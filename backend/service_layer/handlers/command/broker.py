import logging
from uuid import UUID

from backend.core import exceptions
from backend.domain import commands
from backend.domain.models import OutgoingBrokerMessage
from backend.service_layer.uow import AbstractUnitOfWork
from backend.core.config import settings, tz_now

logger = logging.getLogger(__name__)

# async def get_account_id_by_auth_token(
#     cmd: commands.GetAccountIdByAuthToken,
#     uow: AbstractUnitOfWork,
# ) -> UUID | None:
#     async with uow:
#         try:
#             model = await uow.account_repository.get_by_token(cmd.auth_token)
#             return model.id if model.is_active is True else None
#         except exceptions.AccountNotFound:
#             return None


# def get_messages_to_be_send_to_broker(cmd, uow, handle_message):
#     queryset = BrokerMessageOutgoing.objects.filter(
#         has_executed=False,
#         has_execution_stopped=False,
#         next_retry_at__lte=int(datetime.now(timezone.utc).timestamp()),
#     ).all()

#     return PositiveCommandResult([x.to_broker for x in queryset])


async def send_message_to_broker(
    cmd: commands.SendMessageToBroker,
    uow: AbstractUnitOfWork,
) -> None:
    async with uow:
        broker_message = OutgoingBrokerMessage(
            app=settings.app_name,
            key=cmd.message.key,
            body=cmd.message.to_broker,
            next_retry_at=tz_now(cmd.delay)
        )

        await uow.broker_message_repository.add(broker_message)
        await uow.commit()


# def mark_outgoing_broker_message_as_executed(cmd, uow, handle_message):
#     with uow:
#         BrokerMessageOutgoing.objects.filter(pk__in=cmd.ids).update(has_executed=True)
#         uow.commit()

#     return PositiveCommandResult({})


# def schedule_next_retry_for_broker_message(cmd, uow, handle_message):
#     with uow:
#         BrokerMessageOutgoing.objects.filter(pk__in=cmd.ids).update(
#             count_of_retries=F("count_of_retries") + 1,
#             next_retry_at=int(datetime.now(timezone.utc).timestamp())
#             + F("seconds_to_next_retry"),
#             seconds_to_next_retry=F("seconds_to_next_retry") * 2,
#         )

#         BrokerMessageOutgoing.objects.filter(
#             pk__in=cmd.ids, count_of_retries__gte=settings.RABBIT_PUBLISH_RETRY_COUNT
#         ).update(has_execution_stopped=True)

#         uow.commit()

#     return PositiveCommandResult({})


# # ****** MESSAGE FROM BROKER ******


# def consume_message_from_broker(cmd, uow, handle_message):
#     with uow:
#         # Проверяем есть ли сообщение с данным id
#         if BrokerMessageIncoming.objects.filter(pk=cmd.message_id).count() > 0:
#             raise exceptions.MessageBrokerDuplication

#         # Регистрируем сообщение в БД
#         BrokerMessageIncoming.objects.create(
#             id=cmd.message_id,
#             app=cmd.app_id,
#             key=cmd.key,
#             body=cmd.body,
#         )

#         uow.commit()

#     logger.info(f"Consumed {cmd.message_id} - {cmd.app_id}.{cmd.key}")

#     uow.push_message(commands.CreateFlowItemsFromTrigger(cmd.app_id, cmd.key, cmd.body))
#     return PositiveCommandResult({})


# def mark_incoming_broker_message_as_executed(cmd, uow, handle_message):
#     with uow:
#         BrokerMessageIncoming.objects.filter(pk=cmd.id).update(has_executed=True)
#         uow.commit()

#     return PositiveCommandResult({})


# def create_flow_items_from_trigger(cmd, uow, handle_message):
#     # Находим все активные потоки с нужными триггерами
#     trigger = f"{cmd.app_id}.{cmd.key}"
#     flows = Flow.objects.filter(trigger=trigger, is_active=True)

#     # Если триггер не найден в потоках, значит либо
#     # такого триггера нет, либо это внутреннее сервисное
#     # событие. В данном случае отправляемся искать
#     # обработчик такого события

#     if not flows:
#         return PositiveCommandResult({})

#     # Если триггер найден продолжаем обработку
#     flowitems_to_be_created = []
#     flows_to_be_disactivated = []

#     # На основе каждого потока создаем экземпляр
#     for flow in flows.all():
#         flow_item = FlowItem()
#         flow_item.flow = flow
#         flow_item.process = flow.process
#         flow_item.input = cmd.body
#         flow_item.is_active = True
#         flow_item.success = False
#         flow_item.message_if_fail = flow.message_if_fail

#         # Проверяем start_condition у процесса
#         input_vars = {f"input__{k}": v for k, v in flow_item.input.items()}

#         start_condition = flow.process.get("start_condition")
#         start_condition_ok = start_condition is None

#         if start_condition:
#             try:
#                 # print("###############")
#                 # print("EVALUATING START CONDITION", start_condition)
#                 # print("INPUT VARS", input_vars)
#                 # print("###############")
#                 start_condition_ok = eval(
#                     start_condition,
#                     {
#                         "__builtins__": {
#                             "int": int,
#                             "str": str,
#                             "__import__": __import__,
#                             "datetime": datetime,
#                         }
#                     },
#                     input_vars,
#                 )
#                 # print("START_CONDITION_OK = ", start_condition_ok)
#             except (NameError, SyntaxError) as e:
#                 # print("EXCEPTION:", e)
#                 pass

#         # Если стартовые условия выполнены, стартуем экземпляр процесса
#         if start_condition_ok is True:
#             flowitems_to_be_created.append(flow_item)

#             # Если процесс не множественный, дезактивируем процесс
#             if flow.is_multiple is False:
#                 flow.is_active = False
#                 flows_to_be_disactivated.append(flow)

#     with uow:
#         created_flow_items = FlowItem.objects.bulk_create(flowitems_to_be_created)
#         Flow.objects.bulk_update(flows_to_be_disactivated, ["is_active"])
#         uow.commit()

#     # Публикуем событие о том, что создан новый экземпляр потока
#     for item in created_flow_items:
#         uow.push_message(events.FlowItemCreated(item))

#     return PositiveCommandResult({})

