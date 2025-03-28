import time
import psystemd
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import socket

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.tree.command(name="ping", description="Responds with Pong!")
async def ping(interaction: discord.Interaction):
    embed = discord.Embed(
        color = discord.Color.dark_green(),
        description = f"Pong {round(bot.latency, 1)*1000} ms <:yes3:1350514445633323068>",
        title = "Bot is running!"
    )

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="status", description="Provides status of a service")
@discord.app_commands.describe(service="Service name")
async def status(interaction: discord.Interaction, service: str):
    await interaction.response.defer()
    manager = psystemd.SystemdServiceManager()
    service_status = manager.get_unit_status(service)

    embed = discord.Embed(
        title = "Service status"
    )
    reply = ""
    footer = ""
    color = discord.Color.dark_green()
    if service_status['ActiveState'] == "active":
        reply = f"{service} is currently active and running! <:yes3:1350514445633323068>"
    elif service_status['ActiveState'] == "inactive":
        reply = f"{service} is currently inactive and dead! <:psyduck:980763791375626240>"
        footer = "Try checking errors with /get_errors or start with /start"
        color = discord.Color.red()
    elif service_status['ActiveState'] == "activating":
        reply = f"{service} is currently activating! <:pickachu_thinks:1350514416084582450>"
        footer =  "If activating takes too long use /get_errors to see if there are any errors."
        color = discord.Color.light_gray()

    embed.description = reply
    embed.colour = color
    if footer:
        embed.set_footer(text=footer)

    await interaction.followup.send(embed=embed)

@bot.tree.command(name="start", description="Start a systemd service")
@discord.app_commands.describe(service="Service name")
async def start(interaction: discord.Interaction, service: str):
    await interaction.response.defer()
    embed = discord.Embed(
        title = "Starting service...",
    )

    color = discord.Color.dark_green()
    manager = psystemd.SystemdServiceManager()
    manager.start(service)
    time.sleep(2)
    service_status = manager.get_unit_status(service)['ActiveState']
    additional_text = ""
    if service_status != 'active':
        additional_text = " It may take a few seconds to start..."
        embed.colour = discord.Color.dark_gray()

    reply = f"The service is currently {service_status}."
    embed.description = reply + additional_text
    embed.set_footer(text = "Use /status to verify the status of the service.")
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="restart", description="Restart a systemd service")
@discord.app_commands.describe(service="Service name")
async def start(interaction: discord.Interaction, service: str):
    await interaction.response.defer()
    embed = discord.Embed(
        title = "Restarting service...",
    )

    color = discord.Color.dark_green()
    manager = psystemd.SystemdServiceManager()
    manager.restart(service)
    time.sleep(2)
    service_status = manager.get_unit_status(service)['ActiveState']
    additional_text = ""
    if service_status != 'active':
        additional_text = " It may take a few seconds to restart..."
        embed.colour = discord.Color.dark_gray()

    reply = f"The service is currently {service_status}."
    embed.description = reply + additional_text
    embed.set_footer(text = "Use /status to verify the status of the service.")
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="stop", description="Stop a systemd service")
@discord.app_commands.describe(service="Service name")
async def stop(interaction: discord.Interaction, service: str):
    await interaction.response.defer()
    embed = discord.Embed(
        title = "Stopping service...",
    )

    embed.colour = discord.Color.dark_green()
    manager = psystemd.SystemdServiceManager()
    manager.stop(service)
    time.sleep(2)
    service_status = manager.get_unit_status(service)['ActiveState']
    additional_text = ""
    if service_status != 'inactive':
        additional_text = " It may take a few seconds to stop..."
        embed.colour = discord.Color.dark_gray()

    reply = f"The service is currently {service_status}."
    embed.description = reply + additional_text
    embed.set_footer(text="Use /status to verify the status of the service.")
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="get_errors", description="Get the errors produced by a systemd service")
@discord.app_commands.describe(service="Service name")
async def get_errors(interaction: discord.Interaction, service: str):
    await interaction.response.defer()
    embed = discord.Embed(
        title="Errors are as above:",
        color = discord.Color.red()
    )

    manager = psystemd.SystemdServiceManager()
    time.sleep(1)
    service_errors = manager.get_errors(service)
    embed.description = f"Received: {service_errors['Result']}"
    embed.set_footer(text=f"ExecError: {service_errors['ExecMainStatus']}, ExecMainCode {service_errors['ExecMainCode']}")
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="reload", description="Reloads the systemd service daemon")
@discord.app_commands.describe(hostname="Hostname of the machine")
async def reload(interaction: discord.Interaction, hostname: str):
    if socket.gethostname() == hostname:
        await interaction.response.defer()
    else:
        return

    predefinedHosnames = {"local": "raven", "cloud": "Rc"}
    if hostname in predefinedHosnames:
        hostname = predefinedHosnames[hostname]

    if socket.gethostname() == hostname:
        print("Reloading!")
        os.system('systemctl daemon-reload')


    embed = discord.Embed(
        description = "Triggered a daemon reload <:yes3:1350514445633323068>",
        colour=discord.Color.dark_green()
    )

    embed.set_footer(text="Should take a few seconds to start.")
    await interaction.followup.send(embed=embed)

@bot.event
async def setup_hook():
    await bot.tree.sync()
    print("Slash commands synced.")

bot.run(TOKEN)