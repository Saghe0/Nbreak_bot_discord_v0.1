import discord
from discord.ext import commands
from cogs.nbreak_bot_tickets_test.views import TicketView, CloseTicketView

intents = discord.Intents.all()
intents.message_content = True
intents.members = True

class NbreakBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents, help_command=None)
    
    async def setup_hook(self):
        self.add_view(TicketView())
        self.add_view(CloseTicketView())  # Registra la View como persistente
        await self.load_cogs()
        print(f"Bot configurado como {self.user}")

    async def load_cogs(self):
        cogs_to_load = [
            'cogs.general',
            'cogs.moderation',
            # 'cogs.exp',
            'cogs.nbreak_bot_tickets_test'
            # 'suggestions'
        ]
        for cog in cogs_to_load:
            try:
                await self.load_extension(cog)
                print(f"✅ Cog cargado: {cog}")
            except Exception as e:
                print(f"❌ Error al cargar: {cog}: {e}")

    async def on_ready(self):
        print(f"🤖 {self.user} está conectado y listo!")
        try:
            synced = await self.tree.sync()
            print(f"🔄 Sincronizados {len(synced)} comandos slash")
        except Exception as e:
            print(f"❌ Error sincronizando comandos: {e}")