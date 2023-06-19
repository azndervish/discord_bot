import os
import discord
from discord.ext import commands
import openai
import time
import json
import re

DISCORD_MAX_LENGTH = 2000
DISCORD_API_KEY=os.environ['DISCORD_API_KEY']
# Configure your OpenAI API key
openai.api_key = os.environ['OPENAI_API_KEY']
COMMAND_PREFIX = '!'

# Guess game constants
with open("guess_game/solutions.txt", "r") as f:
    GUESS_INIT_PROMPT = f.read()
GUESS_INIT_PROMPT_REPLACE_WORD="sandwich" 
GUESS_SOLUTION_INDEX_FILE="/tmp/guess_solution_index.txt"

# Create a new bot instance
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)
bot.guess_hints = []

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')

# Command: Ping
@bot.command(help="Check if the bot is responsive.")
async def ping(ctx):
    print(ctx)
    await ctx.send('Pong!')

# Command: Ask AI
@bot.command(help="Ask the AI a question.")
async def ask(ctx):
    question = ctx.message.content
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": strip_command(question)}
        ]
    )
    await return_openai_response(ctx, response)

# Command: Init Guessing Game
@bot.command(help="Initialize the guessing game.")
async def guess_init(ctx):
    try:
        bot.guess_solution = get_line_by_index(get_guess_game_solution_index(), GUESS_SOLUTION_INDEX_FILE)
        modified_prompt = GUESS_INIT_PROMPT.replace(GUESS_INIT_PROMPT_REPLACE_WORD, bot.guess_solution)
        guess_messages = [{"role": "user", "content": modified_prompt }]
        response = openai.ChatCompletion.create( model='gpt-3.5-turbo', messages=guess_messages )
        initial_response = response['choices'][0]['message']['content']
        bot.guess_hints = extract_hints(initial_response)
        bot.guess_hints_index = 1
        await return_response(ctx, bot.guess_hints[0])
        await return_response(ctx, "\n\n".join([bot.guess_hints, modified_prompt, initial_response]))
    except Exception as e:
        await return_response(ctx, e)


# Command: Make a guess in the Guessing Game
@bot.command(help="Make a guess in the guessing game.")
async def guess(ctx):
    try:
        if ctx.message.content.lower() == bot.guess_solution.lower():
            await return_response(ctx, f'"{bot.guess_solution}" is the correct answer!')
        elif bot.guess_hints_index >= len(bot.guess_hints):
            await return_response(ctx, f'Out of guesses. The correct answer was "{bot.guess_solution}"')
        else:
            current_hint = bot.guess_hints[bot.guess_hints_index]
            bot.guess_hints_index += 1
            await return_response(ctx, current_hint)
    except Exception as e:
        await return_response(ctx, e)

def strip_command(content: str) -> str:
    """
    Strips the command prefix from the content string.

    Args:
        content (str): The content string to strip the command prefix from.

    Returns:
        str: The content string with the command prefix removed.
    """
    return re.sub(r'^!\w+\s', '', content)

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

def get_guess_game_solution_index() -> int:
    """
    Retrieves the current index of the guess game solution.
    This will increment the index counter for the next game.

    Returns:
        int: The current index of the guess game solution.
    """
    output = 0
    try:
        with open(GUESS_SOLUTION_INDEX_FILE, "r") as f:
            return int(f.read())
    except Exception as e:
        pass
    write_guess_game_solution_index(output + 1)
    return output


def write_guess_game_solution_index(new_index: int) -> None:
    """
    Writes the new index of the guess game solution to a file.

    Args:
        new_index (int): The new index to be written.

    Returns:
        None
    """
    try:
        with open(GUESS_SOLUTION_INDEX_FILE, "w") as f:
            f.write(str(new_index))
    except:
        pass

def get_line_by_index(index: int, file_location: str) -> str:
    """
    Retrieves the line at the specified index in a file.

    If the index is greater than the number of lines in the file, the function
    loops around to the beginning of the file.

    Args:
        index (int): The index of the line to retrieve.

    Returns:
        str: The line at the specified index.
    """
    lines = []
    with open(file_location, "r") as file:
        lines = file.readlines()

    num_lines = len(lines)
    if num_lines == 0:
        return ""

    adjusted_index = index % num_lines
    return lines[adjusted_index]

def extract_hints(input_string):
    """
    Extracts hints from the given input string.

    Args:
        input_string (str): The input string containing multiple lines.

    Returns:
        list: A list of hints extracted from the input string. The number of hints extracted can vary, but it
        will not exceed 10. If there are fewer than 10 hints available in the input string, all available hints
        will be returned.

    """
    lines = input_string.split('\n')
    num_lines = len(lines)
    hints = []

    for i in range(num_lines):
        if len(lines[i].strip()) != 0 and (i+1==len(lines) or len(hints)==9 or len(lines[i + 1].strip()) != 0):
            hints.append(lines[i].strip())
            if len(hints) == 10:
                break

    return hints


# Run the bot with your token
bot.run(DISCORD_API_KEY)