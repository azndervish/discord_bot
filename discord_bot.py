import os
import discord
from discord.ext import commands
import openai
import discord_utils
import guess_game.cog

DISCORD_API_KEY=os.environ['DISCORD_API_KEY']
# Configure your OpenAI API key
openai.api_key = os.environ['OPENAI_API_KEY']
COMMAND_PREFIX = '!'

# Create a new bot instance
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')

# Command: Ping
@bot.command(help="Check if the bot is responsive.")
async def ping(ctx):
    await ctx.send('Pong!')

# Command: Ask AI
@bot.command(help="Ask the AI a question.")
async def ask(ctx):
    question = ctx.message.content
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": discord_utils.strip_command(question)}
        ]
    )
    await discord_utils.return_openai_response(ctx, response)

def main():
    bot.add_cog(guess_game.cog.GuessingGameCog(bot))
    # Run the bot with your token
    bot.run(DISCORD_API_KEY)

main()