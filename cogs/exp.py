import discord
from discord.ext import commands
from dotenv import load_dotenv

class ExpBar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.usuarios = {}
        #_____________________________EXPERIENCIA Y BARRA DE EXPERIENCIA = ESTUDIAR_____________________________

        #Datos de self.usuarios: experiencia y nivel
        # Función para calcular experiencia necesaria por nivel
        def experiencia_necesaria(nivel):
        # Se puede ajustar la fórmula según prefieras
            return 5 * nivel

        # Función para crear la barra de experiencia
        def barra_experiencia(exp_actual, exp_necesaria):
            porcentaje = exp_actual / exp_necesaria
            barras = int(porcentaje * 20)  # 20 caracteres en la barra
            barra = '🟩' * barras + '⬜' * (20 - barras)
            return barra

        @bot.event
        async def on_message(message):
            #No farmee exp el bot
            if message.author.bot:
                return 
            
            #Para definir el usurario en nivel 1 y guardar los datos
            user_id = message.author.id
            if user_id not in self.usuarios:
                self.usuarios[user_id] = {'level': 1, 'exp': 0}

            # Añadir experiencia por cada letra en el mensaje
            exp_ganada = len(message.content)
            self.usuarios[user_id]['exp'] += exp_ganada

            nivel_actual = self.usuarios[user_id]['level']
            exp_actual = self.usuarios[user_id]['exp']
            exp_necesaria = experiencia_necesaria(nivel_actual)

            # Ver si sube de nivel
            while exp_actual >= exp_necesaria and nivel_actual < 20:  # Limitar a nivel 20
                exp_actual -= exp_necesaria
                nivel_actual += 1
                self.usuarios[user_id]['level'] = nivel_actual
                self.usuarios[user_id]['exp'] = exp_actual
                exp_necesaria = experiencia_necesaria(nivel_actual)
                await message.channel.send(f"¡Congratulations {message.author.mention}! You have leveled up {nivel_actual}.")

            await bot.process_commands(message)

        @commands.command(name='level', help='Show you level and EXP actual')
        async def mi_nivel(self, ctx):
            user_id = ctx.author.id
            if user_id not in self.usuarios:
                self.usuarios[user_id] = {'level': 1, 'exp': 0}
            nivel = self.usuarios[user_id]['level']
            exp = self.usuarios[user_id]['exp']
            exp_necesaria = experiencia_necesaria(nivel)
            barra = barra_experiencia(exp, exp_necesaria)
            await ctx.send(f"{ctx.author.mention} Level: {nivel}\nEXP: {exp}/{exp_necesaria}\n{barra}")

async def setup(bot):
    await bot.add_cog(ExpBar(bot))