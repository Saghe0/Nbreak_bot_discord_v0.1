import discord  
from discord.ext import commands
from discord import app_commands
import os
from datetime import datetime

class Suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        @app_commands.command(name='suggest', description='Send a suggestion')
        @app_commands.describe(suggestion='Your suggestion text')
        async def suggest(self, interaction: discord.Interaction, suggestion: str):
            """Command to send a suggestion"""
            channel = self.bot.get_channel(self.suggestions_channel_id)
            if not channel:
                await interaction.response.send_message("❌ Suggestions channel not found.", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="💡 New Suggestion",
                description=suggestion,
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
            
            await channel.send(embed=embed)
            await interaction.response.send_message("✅ Your suggestion has been sent!", ephemeral=True)


        @bot.tree.command(name='setup_suggestions_channel', description='Set the suggestions channel')
        @app_commands.describe(channel='The channel to set for suggestions')
        async def setup_suggestions_channel(interaction: discord.Interaction, channel: discord.TextChannel = None):
            """Command to set the suggestions channel"""
            
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
                return
            
            if channel is None:
                await interaction.response.send_message("❌ Please specify a valid text channel.", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="✅🤔 Suggestions Channel Set",
                description=f"Suggestions will now be sent here {channel.mention}",
                color=discord.Color.green()
            )
            embed.add_field(
                name="Suggestions Channel",
                value="• If you have a suggestion, use the `/suggest` command to send it.",
                inline=False
            )

            self.suggestions_channel_id = channel.id
            await interaction.response.send_message(f"✅ Suggestions channel set to {channel.mention}", ephemeral=True)