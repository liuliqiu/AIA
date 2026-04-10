import lark_oapi as lark
from loguru import logger
import json
import asyncio
from typing import Optional
from config import get_lark_config
from utils.message_queue import prompt_queue
from schema import ChatMessage


class LarkBot:
    def __init__(self, app_id: str, app_secret: str):
        """
        初始化飞书机器人

        Args:
            app_id: 飞书应用的 App ID
            app_secret: 飞书应用的 App Secret
        """
        self.client = (
            lark.Client.builder()
            .app_id(app_id)
            .app_secret(app_secret)
            .log_level(lark.LogLevel.INFO)
            .build()
        )

    def send_text_message(
        self,
        receive_id: str,
        content: str,
        receive_id_type: str = "open_id",
        msg_type: str = "text",
    ) -> Optional[lark.api.im.v1.CreateMessageResponse]:
        """
        发送文本消息

        Args:
            receive_id: 接收者的ID（open_id/user_id/email/chat_id）
            content: 消息内容
            receive_id_type: 接收者ID类型，可选值："open_id", "user_id", "email", "chat_id"
            msg_type: 消息类型，默认为"text"

        Returns:
            CreateMessageResponse 对象或 None（发送失败时）
        """
        try:
            # 构建请求
            request = (
                lark.api.im.v1.CreateMessageRequest.builder()
                .receive_id_type(receive_id_type)
                .request_body(
                    lark.api.im.v1.CreateMessageRequestBody.builder()
                    .receive_id(receive_id)
                    .msg_type(msg_type)
                    .content(json.dumps({"text": content}))
                    .build()
                )
                .build()
            )

            # 发送请求
            response = self.client.im.v1.message.create(request)

            # 检查响应
            if not response.success():
                logger.error(
                    f"发送消息失败: code={response.code}, msg={response.msg}, "
                    f"log_id={response.get_log_id()}"
                )
                return None

            return response.data

        except Exception as e:
            logger.error(f"发送消息时发生异常: {e}")
            return None


def handle_im_message(data: lark.im.v1.p2_im_message_receive_v1.P2ImMessageReceiveV1):
    ## P2ImMessageReceiveV1 为接收消息 v2.0；CustomizedEvent 内的 message 为接收消息 v1.0。
    message = data.event.message
    text = json.loads(message.content)["text"]
    chat_id = message.chat_id
    loop = asyncio.get_event_loop()
    loop.create_task(prompt_queue.put(ChatMessage(text=text, chat_id=chat_id)))
    # result = self.handle_text_message(text)
    # self.reply_bot.send_text_message(chat_id, text, "chat_id")
    logger.info(f"[handle_im_message], data: {lark.JSON.marshal(data, indent=4)}")


class WebSocketClient(lark.ws.Client):
    def __init__(self):
        config = get_lark_config()
        event_handler = (
            lark.EventDispatcherHandler.builder(
                config.encrypt_key, config.verification_token
            ).register_p2_im_message_receive_v1(handle_im_message)
            # .register_p1_customized_event("im.message.receive_v1", handle_event)
            .build()
        )
        super().__init__(
            config.app_id,
            config.app_secret,
            event_handler=event_handler,
            log_level=lark.LogLevel.DEBUG,
        )
        # event_handler.register_p2_im_message_receive_v1(self.handle_im_message)
        # self.handle_text_message = handle_text_message
        self.reply_bot = LarkBot(config.app_id, config.app_secret)

    def start(self, loop=None):
        """
        overrider super & not sleep
        """
        try:
            loop.run_until_complete(self._connect())
        except ClientException as e:
            logger.error(self._fmt_log("connect failed, err: {}", e))
            raise e
        except Exception as e:
            logger.error(self._fmt_log("connect failed, err: {}", e))
            loop.run_until_complete(self._disconnect())
            if self._auto_reconnect:
                loop.run_until_complete(self._reconnect())
            else:
                raise e

        loop.create_task(self._ping_loop())

    def handle_event(self, data: lark.CustomizedEvent) -> None:
        logger.info(f"[handle_event], data: {lark.JSON.marshal(data, indent=4)}")


if __name__ == "__main__":

    def not_change(v):
        return v

    client = WebSocketClient()
    client.start()
