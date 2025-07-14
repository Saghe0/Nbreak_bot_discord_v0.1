import asyncio
import discord
from datetime import datetime
from .storage import load_tickets_data, save_tickets_data

class ConfirmCloseView(discord.ui.View):
    # ...implementación igual...
    def __init__(self, ticket_owner):
        super().__init__(timeout=30)
        self.ticket_owner = ticket_owner
            
    @discord.ui.button(label='✅ Yes, close', style=discord.ButtonStyle.red)
    async def confirm_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
        # Eliminar datos del ticket
            tickets_data = load_tickets_data()
            guild_id = str(interaction.guild.id)
                    
            if guild_id in tickets_data and self.ticket_owner in tickets_data[guild_id]:
                del tickets_data[guild_id][self.ticket_owner]
                save_tickets_data(tickets_data)

            # Enviar mensaje de cierre
            embed = discord.Embed(
                title="🔒 Ticket Closed",
                description="This ticket will be deleted in 5 seconds.",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )

            await interaction.response.edit_message(content=None, embed=embed, view=None)
            
            await asyncio.sleep(5)  # Espera 5 segundos antes de eliminar el canal
            await interaction.channel.delete()

        except Exception as e:
            try:
                await interaction.response.send_message(f"❌ Error al cerrar el ticket: {str(e)}", ephemeral=True)
            except discord.InteractionResponded:
                await interaction.followup.send(f"❌ Error al cerrar el ticket: {str(e)}", ephemeral=True)
            
    @discord.ui.button(label='❌ Cancel', style=discord.ButtonStyle.gray)
    async def cancel_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="✅ Close cancel.", view=None)

class CloseTicketView(discord.ui.View):
    # ...implementación igual...
    def __init__(self):
        super().__init__(timeout=None)
            
    @discord.ui.button(label='🔒 Close Ticket', style=discord.ButtonStyle.red, custom_id='close_ticket')
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Verificar si es el usuario del ticket o staff
        tickets_data = load_tickets_data()
        guild_id = str(interaction.guild.id)
        channel_id = interaction.channel.id

        # Buscar el ticket
        ticket_owner = None
        for user_id, ticket_data in tickets_data.get(guild_id, {}).items():
            if ticket_data['channel_id'] == channel_id:
                ticket_owner = user_id
                break
                
        if not ticket_owner:
            await interaction.response.send_message("❌ No information was found for this ticket.", ephemeral=True)
            return
                
        # Verificar permisos
        is_owner = str(interaction.user.id) == ticket_owner
        # Verisica si el usuario es staff mediante cada uno de los roles del servidor
        is_staff = any(role.name in ['Admin', 'Moderador', 'Staff'] for role in interaction.user.roles) 
        #_____________________________^^^^^^^^^^^^^^^^^^^^^^^^^^^Cambia estos nombres según como esten en el servidor 

        # ¿Puede cerrar el ticket?
        if not (is_owner or is_staff):
            await interaction.response.send_message("❌ You dont have permission to close this ticket..", ephemeral=True)
            return
            
        # Confirmar cierre
        confirm_view = ConfirmCloseView(ticket_owner)
        await interaction.response.send_message(
            "⚠️ Are you sure you want to close this ticket?", view=confirm_view, ephemeral=True )


class TicketView(discord.ui.View):
    # ...implementación igual, pero usando load_tickets_data/save_tickets_data importados...
    def __init__(self):
        super().__init__(timeout=None)  # Vista persistente
            
    @discord.ui.button(label='🎫 Create Ticket', style=discord.ButtonStyle.green, custom_id='create_ticket')
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        print("Botón Create Ticket pulsado")  # <-- Agrega esto
        try:
                # Cargar datos de tickets
            tickets_data = load_tickets_data()
            user_id = str(interaction.user.id)
            guild_id = str(interaction.guild.id)
                    
            # Verificar si el usuario ya tiene un ticket abierto
            if guild_id in tickets_data and user_id in tickets_data[guild_id]:
                ticket_channel_id = tickets_data[guild_id][user_id]['channel_id']
                ticket_channel = interaction.guild.get_channel(ticket_channel_id)
                if ticket_channel:
                    await interaction.response.send_message(f"❌ You already have an open ticket: {ticket_channel.mention}", ephemeral=True)
                    return
                else:
                    # Elimina el canal y para limpiar datos
                    del tickets_data[guild_id][user_id]
                    save_tickets_data(tickets_data)
                    
            # Crear canal de ticket
            try:
                # Buscar o crear categoría para tickets
                category = discord.utils.get(interaction.guild.categories, name="🎫 Tickets")
                if not category:
                    category = await interaction.guild.create_category("🎫 Tickets")
                        
                # Configurar permisos para el canal solo el usuario y staff puede ver y leer el ticket excluyendo al resto de usuarios
                overwrites = {
                    interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True, mention_everyone=False, add_reactions=True),
                    interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                }
                # Agregar permisos para roles de staff (opcional)
                staff_roles = ['Admin', 'Moderador', 'Staff']  # Cambiar estos nombres de ejemplo para el servidor del Discord
                for role_name in staff_roles:
                    role = discord.utils.get(interaction.guild.roles, name=role_name)
                    if role:
                        overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                        
                onwer_role = "Owner" # Para que el dueño del servidor pueda ver el ticket y gestionarlo
                role = discord.utils.get(interaction.guild.roles, name=onwer_role)
                if role:
                    overwrites[role] = discord.PermissionOverwrite(read_messages=True, read_message_history=True, manage_messages=True, send_messages=True)
                        
                # Crear canal para el ticket nuevo 
                channel_name = f"ticket-{interaction.user.name.lower()}"
                ticket_channel = await interaction.guild.create_text_channel(
                    name=channel_name,
                    category=category,
                    overwrites=overwrites
                )

                # Guardar datos del ticket
                if guild_id not in tickets_data:
                    tickets_data[guild_id] = {}
                tickets_data[guild_id][user_id] = {
                    'channel_id': ticket_channel.id,
                    'created_at': datetime.now().isoformat(),
                    'status': 'open'
                }
                save_tickets_data(tickets_data)
                    # Enviar mensaje de bienvenida en el canal del ticket
                embed = discord.Embed(
                    title="🎫 Ticket Created",
                    description=f"¡Hey {interaction.user.mention}!\n\nThank you for creating a ticket. " \
                    "\n\nPlease describe your issue or question in detail.\n\nWhile an authorized staff member support you, please dont delete this channel.",
                    color=discord.Color.green(),
                    timestamp=datetime.now())

                embed.set_footer(text=f"Ticket created for {interaction.user}", icon_url=interaction.user.display_avatar.url)
                        
                from .views import CloseTicketView              # Vista para cerrar ticket
                close_view = CloseTicketView()
                await ticket_channel.send(embed=embed, view=close_view)
                # Responder al usuario
                await interaction.response.send_message(f"✅ Your ticket has been created: {ticket_channel.mention}", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"❌ Error creating ticket: {str(e)}", ephemeral=True)
        except Exception as e:
            print(f"Error en create_ticket: {str(e)}")
            try:
                await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)
            except Exception:
                pass
