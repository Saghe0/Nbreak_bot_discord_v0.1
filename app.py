import discord 
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import os
import random
import requests

load_dotenv()

intents = discord.Intents.all()
intents.message_content = True
intents.members = True

class NbreakBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents, help_command=None)
    
    async def setup_hook(self):
        """Se ejecuta cuando el bot se está configurando"""
        # Cargar cogs (módulos)
        await self.load_cogs()
        print(f"Bot configurado como {self.user}")
    
    async def load_cogs(self):
        """Carga todos los cogs automáticamente"""
        cogs_to_load = [
            'cogs.general',
            'cogs.moderation',
            #'cogs.exp',
            'cogs.nbreak_bot_tickets_test',
            #'suggestions'
        ]
        
        for cog in cogs_to_load:
            try:
                await self.load_extension(cog)
                print(f"✅ Cog cargado: {cog}")
            except Exception as e:
                print(f"❌ Error al cargar: {cog}: {e}")
    
    async def on_ready(self):
        """Evento cuando el bot está listo"""
        print(f"🤖 {self.user} está conectado y listo!")
        
        # Sincronizar comandos slash
        try:
            synced = await self.tree.sync()
            print(f"🔄 Sincronizados {len(synced)} comandos slash")
        except Exception as e:
            print(f"❌ Error sincronizando comandos: {e}")

# Función principal
async def main():
    bot = NbreakBot()
    
    # Obtener token desde variable de entorno
    token = os.getenv("token")
    if not token:
        print("❌ Token no encontrado. Revisar tu archivo .env")
        return
    
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        print("\n🛑 Bot detenido manualmente")
    except Exception as e:
        print(f"❌ Error ejecutando el bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())





