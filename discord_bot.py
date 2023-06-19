import os
import discord
from discord.ext import commands
import openai
import time

DISCORD_MAX_LENGTH = 2000
# Configure your OpenAI API key
openai.api_key = os.environ['OPENAI_API_KEY']

# Prompts:
with open("guess_init_prompt.txt", "r") as f:
    GUESS_INIT_PROMPT = f.read()

# Create a new bot instance
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

guess_messages = []

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
            {"role": "user", "content": question}
        ]
    )
    await return_openai_response(ctx, response)

# Command: Init Guessing Game
@bot.command()
async def guess_init(ctx):
    guess_messages = [{"role": "user", "content": GUESS_INIT_PROMPT}]
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=guess_messages 
    )
    guess_messages.append({"role": "assistant", "content": response['choices'][0]['message']['content']})
    guess_messages.append({"role": "user", "content": "Give me a hint to start."})
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=guess_messages 
    )
    await return_openai_response(ctx, response)

# Command: Make a guess in the Guessing Game
@bot.command()
async def guess(ctx):
    guess_messages.append({"role": "user", "content": ctx.message.content})
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=guess_messages 
    )
    await return_openai_response(ctx, response)

async def return_openai_response(ctx, response):
    answer = response['choices'][0]['message']['content']
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
