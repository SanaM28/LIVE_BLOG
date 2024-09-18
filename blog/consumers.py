from channels.generic.websocket import AsyncWebsocketConsumer
import json


class BlogConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "blog_updates"
        # Join the WebSocket group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the WebSocket group
        await self.channel_layer.group_discard("blog_updates", self.channel_name)

    async def blog_post_update(self, event):
        # Handle the blog_post_update message type
        data = event["data"]  # Extract the data from the event
        await self.send(
            text_data=json.dumps(
                {
                    "type": "blog_post_update",
                    "id": data["id"],
                    "title": data["title"],
                    "description": data["description"],
                    "timestamp": data["timestamp"],
                    "status": data["status"],
                }
            )
        )

    async def blog_post_edit(self, event):
        # Handle post updates
        data = event["data"]  # Extract the data from the event
        await self.send(
            text_data=json.dumps(
                {
                    "type": "blog_post_edit",
                    "id": data["id"],
                    "title": data["title"],
                    "description": data["description"],
                    "timestamp": data["timestamp"],
                    "status": data["status"],
                }
            )
        )

    async def blog_delete_post(self, event):
        # Handle the blog_delete_post message type
        data = event["data"]
        await self.send(
            text_data=json.dumps(
                {
                    "type": "blog_delete_post",
                    "id": data["id"],
                }
            )
        )

    # # New code for handling real-time comments

    # async def receive(self, text_data):
    #     text_data_json = json.loads(text_data)
    #     if text_data_json.get('type') == 'new_comment':
    #         await self.channel_layer.group_send(
    #             self.group_name,
    #             {
    #                 'type': 'new_comment',
    #                 'data': text_data_json
    #             }
    #         )

    async def new_comment(self, event):
        data = event["data"]
        print(data)
        await self.send(
            text_data=json.dumps(
                {
                    "type": "new_comment",
                    "post_id": data["post_id"],
                    "user": data["user"],
                    "content": data["content"],
                    "timestamp": data["timestamp"],
                }
            )
        )

    # New function to handle blog post notifications
    async def notification(self, event):
        message = event["data"]

        print("message is:", message)
        await self.send(
            text_data=json.dumps(
                {
                    "type": "notification",
                    "message": message,
                }
            )
        )

    # async def send_comment_notification(self, event):
    #     message = event["message"]
    #     post_id = event["post_id"]

    #     await self.send(
    #         text_data=json.dumps(
    #             {
    #                 "type": "send_comment_notification",
    #                 "message": message,
    #                 "post_id": post_id,
    #             }
    #         )
    #     )
