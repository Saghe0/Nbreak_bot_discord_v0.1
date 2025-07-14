import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

from .storage import load_tickets_data, save_tickets_data
from .views import TicketView, CloseTicketView, ConfirmCloseView


class NbreakBotTicketsTest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # Aquí van los comandos slash, usando @app_commands.command o @app_commands.describe
    # Comando para configurar el panel de tickets
    @app_commands.command(name='setup_tickets', description='Config panel tickets')
    @app_commands.describe(channel='Channel where the ticket panel will be placed')
    async def setup_tickets(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        # Verificar permisos de administrador
        if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
                return
            
        if channel is None:
            channel = interaction.channel
            
            # Crear embed para el panel 
        embed = discord.Embed(
            title="🎫 System Tickets",
            description="Need help? Create a ticket!\n\nClick the button below to create a private ticket where you can receive personalized help from our team.",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="📋 Instructions / How to use",
            value="• Click on '🎫 Create Ticket'\n• A private channel will be created for you\n• Describe your problem in detail\n• Wait for the staff to help you\n• You can attach images (optinal)",
            inline=False
        )
        embed.set_footer(text="Ticket System | You can only have one ticket open at a time.")
            
        # Enviar panel con botón
        view = TicketView()
        await channel.send(embed=embed, view=view)
            
        await interaction.response.send_message(f"✅ Panel tickets configured in {channel.mention}", ephemeral=True)

        # Comando para ver tickets abiertos (solo staff)
    @app_commands.command(name='tickets', description='Can see all tickets opened')
    async def view_tickets(self, interaction: discord.Interaction):
        # Verificar si es staff
        is_staff = any(role.name in ['Admin', 'Moderador', 'Staff'] for role in interaction.user.roles)
        if not is_staff:
            await interaction.response.send_message("❌ You dont have permission to view this information.", ephemeral=True)
            return
            
        tickets_data = load_tickets_data()
        guild_id = str(interaction.guild.id)
            
        if guild_id not in tickets_data or not tickets_data[guild_id]:
            await interaction.response.send_message("📋 There are no open tickets currently..", ephemeral=True)
            return
            
        embed = discord.Embed(
            title="🎫 Tickets Opens",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
            
        for user_id, ticket_data in tickets_data[guild_id].items():
            user = interaction.guild.get_member(int(user_id))
            channel = interaction.guild.get_channel(ticket_data['channel_id'])
                
            if user and channel:
                created_at = datetime.fromisoformat(ticket_data['created_at'])
                embed.add_field(
                    name=f"👤 {user.display_name}",
                    value=f"Channel: {channel.mention}\nCreate: {created_at.strftime('%d/%m/%Y %H:%M')}",
                    inline=True
                )
            
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Comando para forzar cierre de ticket (solo staff)
    @app_commands.command(name='force_close', description='Force close of ticket')
    @app_commands.describe(user='User whose ticket you want to close')
    async def force_close_ticket(self, interaction: discord.Interaction, user: discord.Member):
        # Verificar si es staff
        is_staff = any(role.name in ['Admin', 'Moderador', 'Staff'] for role in interaction.user.roles)
        if not is_staff:
            await interaction.response.send_message("❌ You dont have permission to use this command.", ephemeral=True)
            return
            
        tickets_data = load_tickets_data()
        guild_id = str(interaction.guild.id)
        user_id = str(user.id)
            
        if guild_id not in tickets_data or user_id not in tickets_data[guild_id]:
            await interaction.response.send_message(f"❌ {user.mention} you dont have an open ticket.", ephemeral=True)
            return
            
        try:
            # Obtener canal del ticket
            channel_id = tickets_data[guild_id][user_id]['channel_id']
            channel = interaction.guild.get_channel(channel_id)
                
            if channel:
                await channel.delete()
                
            # Eliminar datos
            del tickets_data[guild_id][user_id]
            save_tickets_data(tickets_data)
                
            await interaction.response.send_message(f"✅ Ticket of {user.mention} forcibly closed.", ephemeral=True)
                
        except Exception as e:
            await interaction.response.send_message(f"❌ Error to closed of ticket: {str(e)}", ephemeral=True)

    # Añadiendo los comandos 

async def setup(bot):
    await bot.add_cog(NbreakBotTicketsTest(bot))