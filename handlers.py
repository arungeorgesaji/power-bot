import discord
from discord.ext import commands
from features import * 
from typing import Optional

class DiscordBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def handle_ai_response(self, ctx, prompt):
        async with ctx.typing():
            response = await ask_question(prompt)
            
        if not response:
            return await ctx.send("Sorry, I couldn't get a response from the AI service.")
            
        try:
            reply = response['choices'][0]['message']['content']
            await ctx.send(reply)
        except (KeyError, IndexError) as e:
            await ctx.send("Received malformed response from AI service")
            print(f"Error parsing response: {e}\nFull response: {response}")

    async def add_warning(self, guild_id: int, user_id: int, reason: str):
        if guild_id not in self.warnings:
            self.warnings[guild_id] = {}
        if user_id not in self.warnings[guild_id]:
            self.warnings[guild_id][user_id] = []
            
        self.warnings[guild_id][user_id].append(reason)
        return len(self.warnings[guild_id][user_id])

class DiscordHandlers:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ask')
    async def ask_command(self, ctx, *, question):
        await self.bot.handle_ai_response(ctx, question)

    @commands.command(name='joke')
    async def joke_command(self, ctx):
        await self.bot.handle_ai_response(ctx, "Tell me a funny joke")

    @command.command(name='warn')
    @command.has_permissions(kick_members=True) 
    async def warn(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        warning_count = await self.bot.add_warning(ctx.guild.id, member.id, reason)
        
        embed = discord.Embed(
            title="⚠️ User Warned",
            description=f"{member.mention} has been warned.",
            color=discord.Color.orange()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Total Warnings", value=warning_count, inline=True)
        embed.set_footer(text=f"Moderator: {ctx.author}")
        
        await ctx.send(embed=embed)
        try:
            await member.send(f"You've been warned in {ctx.guild.name} for: {reason}")
        except discord.Forbidden:
            pass  

    @commands.command(name='warnings')
    @commands.has_permissions(kick_members=True)
    async def warnings(self, ctx, member: discord.Member):
        warnings = self.bot.warnings.get(ctx.guild.id, {}).get(member.id, [])
        
        if not warnings:
            await ctx.send(f"{member.display_name} has no warnings.")
            return
            
        embed = discord.Embed(
            title=f"⚠️ Warnings for {member.display_name}",
            color=discord.Color.orange()
        )
        
        for i, warning in enumerate(warnings, 1):
            embed.add_field(name=f"Warning #{i}", value=warning, inline=False)
            
        await ctx.send(embed=embed)

    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                title="👢 User Kicked",
                description=f"{member.mention} has been kicked from the server.",
                color=discord.Color.red()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.set_footer(text=f"Moderator: {ctx.author}")
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("I don't have permission to kick this user.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        try:
            await member.ban(reason=reason, delete_message_days=1)
            embed = discord.Embed(
                title="🔨 User Banned",
                description=f"{member.mention} has been banned from the server.",
                color=discord.Color.dark_red()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.set_footer(text=f"Moderator: {ctx.author}")
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("I don't have permission to ban this user.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @commands.command(name='clearwarns')
    @commands.has_permissions(kick_members=True)
    async def clear_warnings(self, ctx, member: discord.Member):
        if ctx.guild.id in self.bot.warnings and member.id in self.bot.warnings[ctx.guild.id]:
            del self.bot.warnings[ctx.guild.id][member.id]
            await ctx.send(f"Cleared all warnings for {member.mention}")
        else:
            await ctx.send(f"{member.display_name} has no warnings to clear.")

def setup_discord_bot(token):
    intents = discord.Intents.default()
    intents.message_content = True
    intents.memebers = True
    
    bot = DiscordBot(command_prefix='!', intents=intents)
    bot.add_cog(DiscordHandlers(bot))
    
    return bot
