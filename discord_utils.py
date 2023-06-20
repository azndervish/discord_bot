import discord
import time
import re

DISCORD_MAX_LENGTH = 2000

async def return_openai_response(ctx: discord.ext.commands.Context, response: dict) -> None:
    """
    Processes the OpenAI response and sends it as a message.

    Args:
        ctx (discord.ext.commands.Context): The context object representing the command invocation.
        response (dict): The OpenAI response containing the generated message.

    Returns:
        None
    """
    answer = response['choices'][0]['message']['content']
    await return_response(ctx, answer)

async def return_response(ctx, answer):
    """
    Sends the response message in chunks to avoid exceeding Discord's maximum message length.

    Args:
        ctx (discord.ext.commands.Context): The context object representing the command invocation.
        answer (str): The response message to be sent.

    Returns:
        None
    """
    last_sent_index = 0
    while last_sent_index < len(answer):
        end_index = last_sent_index + DISCORD_MAX_LENGTH
        if end_index > len(answer):
            end_index = len(answer)
        await ctx.send(answer[last_sent_index:end_index])
        last_sent_index = end_index
        time.sleep(1)

def strip_command(content: str) -> str:
    """
    Strips the command prefix from the content string.

    Args:
        content (str): The content string to strip the command prefix from.

    Returns:
        str: The content string with the command prefix removed.
    """
    if ' ' not in content:
        # if there is no space, then there's no arguments.
        return ""
    return re.sub(r'^![^\s]+\s', '', content)
