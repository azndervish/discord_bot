import os
import discord
from discord.ext import commands
import openai
import time

DISCORD_MAX_LENGTH = 2000
# Configure your OpenAI API key
openai.api_key = os.environ['OPENAI_API_KEY']

# Create a new bot instance
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

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
    print(question)
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question}
        ]
    )
    answer = response['choices'][0]['message']['content']
    last_sent_index = 0
    while last_sent_index < len(answer):
        end_index = last_sent_index + DISCORD_MAX_LENGTH
        if end_index > len(answer):
            end_index = len(answer)
        await ctx.send(answer[last_sent_index:end_index])
        last_sent_index = end_index
        time.sleep(2)

# Run the bot with your token
bot.run(os.environ['DISCORD_API_KEY'])
