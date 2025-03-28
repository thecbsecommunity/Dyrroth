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
ALLOWED_GUILD_ID = 948219858447921154

@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.id != ALLOWED_GUILD_ID:
            print(f"Leaving unauthorized server: {guild.name} ({guild.id})")
            await guild.leave()  # Leave the server automatically

    print(f'Bot is running in {bot.get_guild(ALLOWED_GUILD_ID).name}')

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
        footer = "Try checking errors with /get_logs or start with /start"
        color = discord.Color.red()
    elif service_status['ActiveState'] == "activating":
        reply = f"{service} is currently activating! <:pickachu_thinks:1350514416084582450>"
        footer =  "If activating takes too long use /get_logs to see if there are any errors."
        color = discord.Color.light_gray()
    elif service_status['ActiveState'] == "invalid":
        reply = f"{service} does not exists/is not enabled yet! Use /get_logs for more info <:pickachu_thinks:1350514416084582450>"
        footer = f"Exception: {service_status['SubState']}"

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


@bot.tree.command(name="enable", description="Enable a systemd service")
@discord.app_commands.describe(service="Service name")
async def enable(interaction: discord.Interaction, service: str):
    await interaction.response.defer()
    embed = discord.Embed(
        title = "Enabling service...",
    )
    color = discord.Color.dark_green()
    manager = psystemd.SystemdServiceManager()
    if manager.enable(service):
        time.sleep(2)
        embed.description = f"Enabled the service {service}"
        embed.set_footer(text = "Use /status to verify the status of the service.")
        await interaction.followup.send(embed=embed)
    else:
        embed.description = f"Enabling the service failed!"
        embed.set_footer(text="Are you running the bot as root? Use /status to verify the status of the service.")
        await interaction.followup.send(embed=embed)


@bot.tree.command(name="disable", description="Disable a systemd service")
@discord.app_commands.describe(service="Service name")
async def disable(interaction: discord.Interaction, service: str):
    await interaction.response.defer()
    embed = discord.Embed(
        title = "Disabling service...",
    )
    color = discord.Color.dark_green()
    manager = psystemd.SystemdServiceManager()
    if manager.disable(service):
        time.sleep(2)
        embed.description = f"Disabled the service {service}"
        embed.set_footer(text = "Use /status to verify the status of the service.")
        await interaction.followup.send(embed=embed)
    else:
        embed.description = f"Disabling the service failed!"
        embed.set_footer(text="Are you running the bot as root? Use /status to verify the status of the service.")
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

@bot.tree.command(name="get_logs", description="Get the logs produced by a systemd service")
@discord.app_commands.describe(service="Service name")
async def get_logs(interaction: discord.Interaction, service: str):
    await interaction.response.defer()
    embed = discord.Embed(
        title="Errors are as above:",
        color = discord.Color.red()
    )

    manager = psystemd.SystemdServiceManager()
    time.sleep(1)
    embed.description = manager.get_journalctl_logs(service)['Logs']
    # service_errors = manager.get_errors(service)
    # embed.description = f"Received: {service_errors['Result']}"
    # embed.set_footer(text=f"ExecError: {service_errors['ExecMainStatus']}, ExecMainCode {service_errors['ExecMainCode']}")
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="reload", description="Reloads the systemd service daemon")
async def reload(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(
        description = "Triggered a daemon reload <:yes3:1350514445633323068>",
        colour=discord.Color.dark_green()
    )

    os.system('systemctl daemon-reload')

    embed.set_footer(text="Should take a few seconds to start.")
    await interaction.followup.send(embed=embed)

@bot.event
async def setup_hook():
    await bot.tree.sync()
    print("Slash commands synced.")

bot.run(TOKEN)