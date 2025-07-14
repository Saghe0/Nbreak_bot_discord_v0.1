import discord 
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import os

from bot import NbreakBot


load_dotenv()

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
