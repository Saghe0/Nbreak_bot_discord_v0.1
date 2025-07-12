# cogs/general.py - Comandos generales con slash commands
import discord
from discord.ext import commands
from discord import app_commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # COMANDO TRADICIONAL (con prefijo !)
    @commands.command(name='ping')
    async def ping_traditional(self, ctx):
        """Comando tradicional: !ping"""
        latencia = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong! Your latency is: {latencia}ms")
    
    # COMANDO SLASH PURO
    @app_commands.command(name='ping', description='Displays the BOT latency')
    async def ping_slash(self, interaction: discord.Interaction):
        """Command slash: /ping"""
        latencia = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"🏓 Pong! Your latency is: {latencia}ms")
    
    # COMANDO SLASH CON PARÁMETROS
    @app_commands.command(name='say', description='Makes the bot say something')
    @app_commands.describe(message='The message you wanna the bot to say')
    async def say(self, interaction: discord.Interaction, message: str):
        """Comando slash con parámetros"""
        await interaction.response.send_message(f"📢 {message}")
    
    # COMANDO SLASH CON OPCIONES
    @app_commands.command(name='info', description='Server or user information')

    @app_commands.describe(target='Whats information do you wanna to see?', user='User specific (optional)')
    
    async def info(
        self, 
        interaction: discord.Interaction, 
        target: str = 'server',
        user: discord.Member = None
    ):
        """Comando slash con opciones"""
        if target.lower() == 'server':
            guild = interaction.guild
            embed = discord.Embed(
                title=f"📊 Information of {guild.name}",
                color=discord.Color.blue()
            )
            embed.add_field(name="👥 Members", value=guild.member_count, inline=True)
            embed.add_field(name="📁 Channels", value=len(guild.channels), inline=True)
            embed.add_field(name="🏷️ Roles", value=len(guild.roles), inline=True)
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
            
            await interaction.response.send_message(embed=embed)
        
        elif target.lower() == 'user':
            target_user = user or interaction.user
            embed = discord.Embed(
                title=f"👤 Information of {target_user.display_name}",
                color=discord.Color.green()
            )
            embed.add_field(name="📅 Account created", value=target_user.created_at.strftime("%d/%m/%Y"), inline=True)
            embed.add_field(name="📥 Join to server", value=target_user.joined_at.strftime("%d/%m/%Y"), inline=True)
            embed.add_field(name="🆔 ID", value=target_user.id, inline=True)
            embed.set_thumbnail(url=target_user.avatar.url if target_user.avatar else target_user.default_avatar.url)
            
            await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))