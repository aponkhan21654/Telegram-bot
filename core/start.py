# Copyright @ISmartCoder
# Updates Channel t.me/TheSmartDev

from telethon import TelegramClient, events, Button
from telethon.errors import FloodWaitError, PeerIdInvalidError
from telethon.tl.types import InputPeerUser, InputPeerChannel, InputPeerChat
from utils.logger import LOGGER
from config import COMMAND_PREFIX, UPDATE_CHANNEL_URL
import asyncio
import html

def setup_start_handler(app: TelegramClient):
    # Create regex pattern for all command prefixes
    pattern = '|'.join(rf'\{prefix}start$' for prefix in COMMAND_PREFIX)

    async def safe_send_message(chat_id, message, **kwargs):
        """Safely send message with entity resolution"""
        try:
            # Try to send directly first
            return await app.send_message(chat_id, message, **kwargs)
        except (ValueError, TypeError) as e:
            if "input entity" in str(e).lower() or "could not find" in str(e).lower():
                try:
                    # Try to resolve the entity
                    entity = await app.get_input_entity(chat_id)
                    return await app.send_message(entity, message, **kwargs)
                except Exception as inner_e:
                    LOGGER.error(f"Failed to resolve entity for {chat_id}: {inner_e}")
                    raise inner_e
            else:
                raise e

    @app.on(events.NewMessage(pattern=pattern, incoming=True))
    async def start_message(event):
        try:
            chat_id = event.chat_id
            sender_id = event.sender_id

            # Initial animation message
            try:
                animation_message = await safe_send_message(chat_id, "<b>Starting Smart OTP ⚙️...</b>", parse_mode='html')
                await asyncio.sleep(0.3)
                await app.edit_message(chat_id, animation_message.id, "<b>Generating Session Keys Please Wait...</b>", parse_mode='html')
                await asyncio.sleep(0.3)
                await app.delete_messages(chat_id, animation_message)
            except Exception as anim_error:
                LOGGER.warning(f"Animation failed: {anim_error}")

            # Get user full name
            full_name = "User"
            try:
                if event.sender:
                    first_name = getattr(event.sender, 'first_name', '') or ""
                    last_name = getattr(event.sender, 'last_name', '') or ""
                    full_name = f"{first_name} {last_name}".strip() or "User"
            except Exception as name_error:
                LOGGER.warning(f"Could not get user name: {name_error}")

            # Prepare response message
            if event.is_private:
                response_text = (
                    f"**Hi {html.escape(full_name)}! Welcome To This Bot**\n"
                    "**━━━━━━━━━━━━━━━━━━━━━━**\n"
                    "**Smart OTP**: The ultimate toolkit on Telegram, offering various countries OTP instantly.\n"
                    "**━━━━━━━━━━━━━━━━━━━━━━**\n"
                    f"**Don't forget to [Join Here]({UPDATE_CHANNEL_URL}) for updates!**"
                )
            else:
                try:
                    chat_entity = await event.get_chat()
                    group_name = getattr(chat_entity, 'title', 'this group')
                    response_text = (
                        f"**Hi! Welcome {html.escape(group_name)} To This Bot**\n"
                        "**━━━━━━━━━━━━━━━━━━━━━━**\n"
                        "**Smart OTP**: The ultimate toolkit on Telegram, offering various countries OTP instantly.\n"
                        "**━━━━━━━━━━━━━━━━━━━━━━**\n"
                        f"**Don't forget to [Join Here]({UPDATE_CHANNEL_URL}) for updates!**"
                    )
                except Exception as chat_error:
                    LOGGER.warning(f"Could not get chat info: {chat_error}")
                    response_text = (
                        "**Hi! Welcome To This Bot**\n"
                        "**━━━━━━━━━━━━━━━━━━━━━━**\n"
                        "**Smart OTP**: The ultimate toolkit on Telegram, offering various countries OTP instantly.\n"
                        "**━━━━━━━━━━━━━━━━━━━━━━**\n"
                        f"**Don't forget to [Join Here]({UPDATE_CHANNEL_URL}) for updates!**"
                    )

            # Send response with button
            try:
                await safe_send_message(
                    chat_id,
                    response_text,
                    parse_mode='md',
                    buttons=[[Button.url("Updates Channel", UPDATE_CHANNEL_URL)]],
                    link_preview=False
                )
                LOGGER.info(f"Sent /start message to {full_name} (ID: {sender_id}) in chat {chat_id}")
                
            except FloodWaitError as e:
                LOGGER.warning(f"Flood wait error: Waiting {e.seconds} seconds")
                await asyncio.sleep(e.seconds + 1)
                await safe_send_message(
                    chat_id,
                    response_text,
                    parse_mode='md',
                    buttons=[[Button.url("Updates Channel", UPDATE_CHANNEL_URL)]],
                    link_preview=False
                )
                
        except PeerIdInvalidError:
            LOGGER.error(f"Invalid peer ID for /start command in chat {chat_id}")
        except Exception as e:
            LOGGER.error(f"Error in /start handler: {e}")
            # Try to send error message if possible
            try:
                error_msg = "Sorry, I encountered an error processing your request. Please try again later."
                await safe_send_message(chat_id, error_msg)
            except:
                pass

# Additional utility function for entity resolution
async def resolve_entity(client, peer_id):
    """Safely resolve any Telegram entity"""
    try:
        return await client.get_input_entity(peer_id)
    except ValueError:
        # If entity not found in cache, try different approaches
        try:
            # For user IDs
            if isinstance(peer_id, int) and peer_id > 0:
                return InputPeerUser(peer_id, 0)  # 0 for unknown access_hash
            # You can add more cases for channels/groups if needed
        except:
            pass
        raise ValueError(f"Could not resolve entity for {peer_id}")
