import os
from discord.ext import commands
import openai
import discord_utils

openai.api_key = os.environ['OPENAI_API_KEY']

# game constants
with open("adventure_game/init_prompt.txt", "r") as f:
    INIT_PROMPT = f.read()
with open("adventure_game/join_prompt.txt", "r") as f:
    JOIN_PROMPT = f.read()

TWIST_ITERATIONS = 7

class AdventureGameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chat_context = []
        self.init_in_progress = False
        self.action_queue = []
        self.twist_counter = 0

    @commands.command(help="Initialize the Adventure game. Provide a scenario description.")
    async def adv_init(self, ctx):
        try:
            if self.init_in_progress :
                await discord_utils.return_response(ctx, "A new adventure game is being created. Please wait")
                return

            self.init_in_progress = True
            modified_prompt = f'{INIT_PROMPT}\n\n{discord_utils.strip_command(ctx.message.content)}'
            self.chat_context = [{"role": "user", "content": modified_prompt }]
            await discord_utils.return_response(ctx, "Setting up a new Adventure game. Please wait while ChatGPT does magic.")
            response = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=self.chat_context)
            initial_response = response['choices'][0]['message']['content']
            self.chat_context.append([{"role": "assistant", "content": initial_response }])
            await discord_utils.return_response(ctx, initial_response)
            self.init_in_progress = False
        except Exception as e:
            await discord_utils.return_response(ctx, str(e))

    @commands.command(help="Submit an action to the adventure game.")
    async def adv(self, ctx):
        try:
            self.action_queue.append(discord_utils.strip_command(ctx.message.content))
            if self.twist_counter >= TWIST_ITERATIONS:
                self.action_queue.append("Add a twist to the story.")
            else:
                self.twist_counter += 1

            user_content = "\n".join(self.action_queue)
            self.action_queue = []
            self.chat_context.append({"role": "user", "content": user_content})
            response = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=self.chat_context)
            initial_response = response['choices'][0]['message']['content']
            self.chat_context.append([{"role": "assistant", "content": initial_response }])
            await discord_utils.return_response(ctx, initial_response)
        except Exception as e:
            await discord_utils.return_response(ctx, str(e))

    @commands.command(help="Queue up an action. Queued actions are submitted when 'adv' is used.")
    async def advq(self, ctx):
        try:
            self.action_queue.append(discord_utils.strip_command(ctx.message.content))
            await discord_utils.return_response(ctx, str(self.action_queue))
        except Exception as e:
            await discord_utils.return_response(ctx, str(e))

    @commands.command(help="Adds a player character to the game. Give a description of the new character.")
    async def adv_join(self, ctx):
        try:
            description = discord_utils.strip_command(ctx.message.content)
            user_content = f'{JOIN_PROMPT}\n\n{description}'
            self.chat_context.append({"role": "user", "content": user_content})
            response = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=self.chat_context)
            initial_response = response['choices'][0]['message']['content']
            self.chat_context.append([{"role": "assistant", "content": initial_response }])
            await discord_utils.return_response(ctx, initial_response)
        except Exception as e:
            await discord_utils.return_response(ctx, str(e))

async def setup(bot):
    await bot.add_cog(AdventureGameCog(bot))
