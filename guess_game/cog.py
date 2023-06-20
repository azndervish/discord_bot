import os
from discord.ext import commands
import openai
import time
import discord_utils

openai.api_key = os.environ['OPENAI_API_KEY']

# Guess game constants
with open("guess_game/init_prompt.txt", "r") as f:
    GUESS_INIT_PROMPT = f.read()
GUESS_INIT_PROMPT_REPLACE_WORD="sandwich" 
GUESS_SOLUTION_INDEX_FILE="/tmp/guess_solution_index.txt"
GUESS_SOLUTION_FILE="guess_game/solutions.txt"


class GuessingGameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guess_solution = ""
        self.guess_hints = []
        self.guess_hints_index = 0
        self.guess_init_in_progress = False

    @commands.command(help="Initialize the guessing game.")
    async def guess_init(self, ctx):
        try:
            if self.guess_init_in_progress:
                await discord_utils.return_response(ctx, "A new game is being created. Please wait")
                return

            self.guess_init_in_progress = True
            self.guess_solution = get_line_by_index(get_guess_game_solution_index(), GUESS_SOLUTION_FILE)
            modified_prompt = GUESS_INIT_PROMPT.replace(GUESS_INIT_PROMPT_REPLACE_WORD, self.guess_solution)
            guess_messages = [{"role": "user", "content": modified_prompt }]
            await discord_utils.return_response(ctx, "Setting up a new Guessing game. Please wait while ChatGPT does magic.")
            response = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=guess_messages)
            initial_response = response['choices'][0]['message']['content']
            self.guess_hints = extract_hints(initial_response)
            self.guess_hints_index = 1
            await discord_utils.return_response(ctx, self.guess_hints[0])
            self.guess_init_in_progress = False
        except Exception as e:
            await discord_utils.return_response(ctx, str(e))

    @commands.command(help="Make a guess in the guessing game.")
    async def guess(self, ctx):
        try:
            if discord_utils.strip_command(ctx.message.content).lower().strip() == self.guess_solution.lower().strip():
                await discord_utils.return_response(ctx, f'"{self.guess_solution}" is the correct answer!')
            elif self.guess_hints_index >= len(self.guess_hints):
                await discord_utils.return_response(ctx, f'Out of guesses. The correct answer was "{self.guess_solution}"')
            else:
                current_hint = self.guess_hints[self.guess_hints_index]
                self.guess_hints_index += 1
                await discord_utils.return_response(ctx, current_hint)
        except Exception as e:
            await discord_utils.return_response(ctx, str(e))

async def setup(bot):
    await bot.add_cog(GuessingGameCog(bot))

def get_line_by_index(index, file_path):
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
            if 0 <= index < len(lines):
                return lines[index].strip()
    except Exception:
        pass
    return ""

def extract_hints(input_string):
    lines = input_string.split('\n')
    num_lines = len(lines)
    hints = []

    for i in range(num_lines):
        if len(lines[i].strip()) != 0 and (i + 1 == len(lines) or len(hints) == 9 or len(lines[i + 1].strip()) != 0):
            hints.append(lines[i].strip())
            if len(hints) == 10:
                break

    return hints

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
            output = int(f.read())
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
    return lines[adjusted_index].strip()

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
