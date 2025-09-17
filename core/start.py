# Copyright @ISmartCoder
# Updates Channel t.me/TheSmartDev

from telethon import TelegramClient, events, Button
from telethon.errors import FloodWaitError, PeerIdInvalidError
from utils.logger import LOGGER       # Ensure LOGGER is defined in utils/logger.py
from config import COMMAND_PREFIX, UPDATE_CHANNEL_URL
import asyncio
import html

def setup_start_handler(app: TelegramClient):
    # Create regex pattern for all command prefixes
    pattern = '|'.join(rf'\{prefix}start$' for prefix in COMMAND_PREFIX)

    @app.on(events.NewMessage(pattern=pattern, incoming=True))
    async def start_message(event):
        try:
            chat_id = event.chat_id

            # Initial animation message
            animation_message = await event.respond("<b>Starting Smart OTP ⚙️...</b>", parse_mode='html')
            await asyncio.sleep(0.3)
            await app.edit_message(animation_message, "<b>Generating Session Keys Please Wait...</b>", parse_mode='html')
            await asyncio.sleep(0.3)
            await app.delete_messages(chat_id, animation_message)

            # Get user full name
            full_name = "User"
            if event.sender:
                first_name = getattr(event.sender, 'first_name', '') or ""
                last_name = getattr(event.sender, 'last_name', '') or ""
                full_name = f"{first_name} {last_name}".strip() or "User"

            # Prepare response message
            if event.is_private:
                response_text = (
                    f"**Hi {full_name}! Welcome To This Bot**\n"
                    "**━━━━━━━━━━━━━━━━━━━━━━**\n"
                    "**Smart OTP**: The ultimate toolkit on Telegram, offering various countries OTP instantly.\n"
                    "**━━━━━━━━━━━━━━━━━━━━━━**\n"
                    f"**Don't forget to [Join Here]({UPDATE_CHANNEL_URL}) for updates!**"
                )
            else:
                chat_entity = await event.get_chat()
                group_name = getattr(chat_entity, 'title', 'this group')
                response_text = (
                    f"**Hi! Welcome {group_name} To This Bot**\n"
                    "**━━━━━━━━━━━━━━━━━━━━━━**\n"
                    "**Smart OTP**: The ultimate toolkit on Telegram, offering various countries OTP instantly.\n"
                    "**━━━━━━━━━━━━━━━━━━━━━━**\n"
                    f"**Don't forget to [Join Here]({UPDATE_CHANNEL_URL}) for updates!**"
                )

            # Send response with button
            await event.respond(
                response_text,
                parse_mode='md',
                buttons=[[Button.url("Updates Channel", UPDATE_CHANNEL_URL)]],
                link_preview=False
            )

            LOGGER.info(f"Sent /start message to {full_name} (ID: {event.sender_id}) in chat {chat_id}")

        except FloodWaitError as e:
            LOGGER.warning(f"Flood wait error: Waiting {e.seconds} seconds")
            await asyncio.sleep(e.seconds + 1)
            await event.respond(
                response_text,
                parse_mode='md',
                buttons=[[Button.url("Updates Channel", UPDATE_CHANNEL_URL)]],
                link_preview=False
            )
        except PeerIdInvalidError:
            LOGGER.error(f"Invalid peer ID for /start command in chat {chat_id}")
        except Exception as e:
            LOGGER.error(f"Error in /start handler: {e}")
