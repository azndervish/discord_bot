import os
import discord
from discord.ext import commands
import openai
import time
import json
import re

DISCORD_MAX_LENGTH = 2000
# Configure your OpenAI API key
openai.api_key = os.environ['OPENAI_API_KEY']

# Prompts:
with open("guess_init_prompt.txt", "r") as f:
    GUESS_INIT_PROMPT = f.read()

# Create a new bot instance
COMMAND_PREFIX = '!'
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')

# Command: Ping
@bot.command()
async def ping(ctx):
    print(ctx)
    await ctx.send('Pong!')

# Command: Ask AI
@bot.command()
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
@bot.command()
async def guess_init(ctx):
    guess_messages = [{"role": "user", "content": GUESS_INIT_PROMPT}]
    response = openai.ChatCompletion.create( model='gpt-3.5-turbo', messages=guess_messages )
    initial_response = response['choices'][0]['message']['content']
    guess_messages.append({"role": "assistant", "content": initial_response})
    with open("/tmp/guess_messages.json", "w") as f:
        json.dump(guess_messages, f)
    output = []
    for line in initial_response.split('\n'):
        if "solution" not in line.lower():
            output.append(line)
    await ctx.send("\n".join(output))
    await ctx.send(guess_messages)

# Command: Make a guess in the Guessing Game
@bot.command()
async def guess(ctx):
    try:
        with open("/tmp/guess_messages.json", "r") as f:
            guess_messages = json.loads(f.read())
        guess_messages.append({"role": "user", "content": strip_command(ctx.message.content)})
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=guess_messages 
        )
        await return_openai_response(ctx, response)
        await ctx.send(guess_messages)
    except Exception as e:
        await guess_init(ctx)

def strip_command(content):
    return re.sub(r'^!\w+\s', '', content)

async def return_openai_response(ctx, response):
    answer = response['choices'][0]['message']['content']
    await return_response(ctx, answer)

async def return_response(ctx, answer):
    last_sent_index = 0
    while last_sent_index < len(answer):
        end_index = last_sent_index + DISCORD_MAX_LENGTH
        if end_index > len(answer):
            end_index = len(answer)
        await ctx.send(answer[last_sent_index:end_index])
        last_sent_index = end_index
        time.sleep(1)

# Run the bot with your token
bot.run(os.environ['DISCORD_API_KEY'])
