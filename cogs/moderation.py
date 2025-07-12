# cogs/moderation.py - Moderación con comandos slash
import discord
from discord.ext import commands
from discord import app_commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # COMANDO SLASH DE MODERACIÓN
    @app_commands.command(name='kick', description='Kick a member from the server')
    @app_commands.describe(
        member='The member to be kicked',
        reason='Reason for the kick (optional)'
    )
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        """Comando slash para expulsar miembros"""
        # Verificar permisos
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message("❌ You dont have permission to kick members", ephemeral=True)
            return
        
        # Verificar jerarquía
        if interaction.user.id in ['Staff', 'Moderador']:
            await interaction.response.send_message("❌ You cant kick this member", ephemeral=True)
            return
        
        if reason is None:
            reason = "Reason no specified"
        
        try:
            await member.kick(reason=reason)
            
            embed = discord.Embed(
                title="😛👢 Member kicked",
                color=discord.Color.orange()
            )
            embed.add_field(name="User", value=f"{member.mention} ({member})", inline=False)
            embed.add_field(name="Mod", value=interaction.user.mention, inline=True)
            embed.add_field(name="Reason", value=reason, inline=True)
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ I dont have permission to kick member, please assign me a role", ephemeral=True)
    
    # COMANDO HÍBRIDO DE MODERACIÓN
    @commands.hybrid_command(name='ban', description='Ban members from the server')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = None):

        """Comando híbrido para banear miembros"""
        if reason is None:
            reason = "Reason no specified"
        
        try:
            await member.ban(reason=reason)
            
            embed = discord.Embed(
                title="🔨 HAMMER BAN",
                color=discord.Color.red()
            )
            embed.add_field(name="User", value=f"{member.mention} ({member})", inline=False)
            embed.add_field(name="Mod", value=ctx.author.mention, inline=True)
            embed.add_field(name="Reason", value=reason, inline=True)
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ I dont have permission to BAN member, please assign me a role")
    
    # COMANDO SLASH CON OPCIONES MÚLTIPLES
    @app_commands.command(name='clear', description='Channel messages cleaning')
    @app_commands.describe(
        cantidad='Clean messages quantity (max 100)',
        usuario='Clean messages from a specific user (optional)'
    )
    async def clear(self, interaction: discord.Interaction, cantidad: int, usuario: discord.Member = None):
        """Comando slash para limpiar mensajes"""
        
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ You dont have permission to clean channel", ephemeral=True) #Si no tiene permisos
            return

        if cantidad > 100:
            cantidad = 100
            
        await interaction.response.defer()  # Importante para comandos que toman tiempo


        def check(message):
            if usuario:
                return message.author == usuario
            return True
        
        try:
            deleted = await interaction.followup.channel.purge(limit=cantidad, check=check)
            
            embed = discord.Embed(
                title="🗑️ Messages cleaned",
                description=f"Was clear the {len(deleted)} mensages",
                color=discord.Color.green()
            )
            
            if usuario:
                embed.add_field(name="Specific user", value=usuario.mention, inline=True)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except discord.Forbidden:
            await interaction.followup.send("❌ I dont have permission to CLEAR CHANNEL, please assign me a role", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))