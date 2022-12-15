import discord, os, aiohttp, asyncio, time, psutil

TOKEN = os.getenv("DISCORD_TOKEN")

bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"[-]: Logged in as {bot.user}")
    for guild in bot.guilds:
        print(f"[-]: {guild.name} ({guild.id})")
    print(f"[-]: Loaded {len(bot.guilds)} guilds succesfully")
    while True:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.xeno-ai.space/stats") as resp:
                data = await resp.json()
                if resp.status == 200:
                    await asyncio.sleep(10)
                    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.guilds)} servers", status=discord.Status.dnd))
                    await asyncio.sleep(10)
                    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"/generate", status=discord.Status.dnd))
                    await asyncio.sleep(10)
                    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{data['total_generations']} generations", status=discord.Status.dnd))
                    await asyncio.sleep(10)
                    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{round(data['database_size_mb'] / 1024, 2)} GB", status=discord.Status.dnd))

@bot.command(name="generate", description="Generate an image from a prompt")
async def generate(ctx, prompt):

    async def loading_bar(msg, start):
        while True:
            await asyncio.sleep(2)
            if int(time.time() - start) / 13 * 100 < 100:
                bar = f"{round(int(time.time() - start) / 13 * 100, 2)}% [{'=' * int((time.time() - start) / 13 * 25)}{' ' * (25 - int((time.time() - start) / 13 * 25))}] 100%"
                embed = discord.Embed(title="Generating Image", description="Please wait while we generate your image.", color=0x2f3136)
                embed.add_field(name="Prompt", value=f"```{prompt}```", inline=False)
                embed.add_field(name="Progress", value=f"```{bar}```", inline=False)
                embed.set_footer(text="Powered by XenoAI - https://xeno-ai.space")
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1051329188361142312/1053017382513299536/x_logo_23.png")
                embed.color = discord.Color.blurple()
                await msg.edit_original_response(embed=embed)
            else:
                start = time.time()

    async def upload(interaction):
        if ctx.author != interaction.user:
            return await interaction.response.send_message("You cannot do this", ephemeral=True)
        channel = bot.get_channel(1043953820125896715)
        await channel.send(f"**Prompt** {prompt}\n{data['output']}")
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="D1", row=0, url=data["images"][0]))
        view.add_item(discord.ui.Button(label="D2", row=0, url=data["images"][1]))
        view.add_item(discord.ui.Button(label="D3", row=0, url=data["images"][2]))
        view.add_item(discord.ui.Button(label="Invite Bot", row=0, url=os.getenv("INVITE_LINK")))
        btnend = discord.ui.Button(label="Upload to Xeno-AI", row=1, style=discord.ButtonStyle.primary)
        btnend.disabled = True
        view.add_item(btnend)
        await interaction.response.edit_message(embed=embed, view=view)

    embed = discord.Embed(title="Generating Image", description="Please wait while we generate your image.")
    embed.add_field(name="Prompt", value=f"```{prompt}```", inline=False)
    embed.set_footer(text="Powered by XenoAI - https://xeno-ai.space")
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1051329188361142312/1053017382513299536/x_logo_23.png")
    embed.color = discord.Color.blurple()
    msg = await ctx.respond(embed=embed)
    start = time.time()
    l_bar = asyncio.create_task(loading_bar(msg, start))
    async with aiohttp.ClientSession() as session:
        data = {"prompt": prompt}
        auth = {"Authorization": os.getenv("AI_TOKEN")}
        async with session.post("https://api.xeno-ai.space/images", json=data, headers=auth) as resp:
            if resp.status == 200:
                l_bar.cancel()
                data = await resp.json()
                embed = discord.Embed(title="Generated Image", description=f"Your image has been generated in {round(time.time() - start, 2)} seconds")
                embed.add_field(name="Prompt", value=f"```{prompt}```", inline=False)
                embed.add_field(name="Requested by", value=f"```{ctx.author.name}```", inline=True)
                embed.add_field(name="API Version", value=f"```{data['version']}```", inline=True)
                embed.set_footer(text="Powered by XenoAI - https://xeno-ai.space")
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1051329188361142312/1053017382513299536/x_logo_23.png")
                embed.color = discord.Color.blurple()
                embed.set_image(url=data["output"])
                view = discord.ui.View()
                view.add_item(discord.ui.Button(label="D1", row=0, url=data["images"][0]))
                view.add_item(discord.ui.Button(label="D2", row=0, url=data["images"][1]))
                view.add_item(discord.ui.Button(label="D3", row=0, url=data["images"][2]))
                view.add_item(discord.ui.Button(label="Invite Bot", row=0, url=os.getenv("INVITE_LINK")))
                upload_btn = discord.ui.Button(label="Upload to Xeno-AI", row=1, style=discord.ButtonStyle.primary)
                upload_btn.callback = upload
                view.add_item(upload_btn)
                await msg.edit_original_response(embed=embed, view=view)
            else:
                l_bar.cancel()
                embed = discord.Embed(title="Error", description=f"An error occurred while generating your image. We are experiencing a lot of traffic right now, please try again in a few seconds. This issue will be resolved soon.")
                embed.set_footer(text="Powered by XenoAI - https://xeno-ai.space")
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1051329188361142312/1053017382513299536/x_logo_23.png")
                embed.color = discord.Color.orange()
                await msg.edit_original_response(embed=embed)

@bot.command(name="stats", description="Get the vps stats")
async def stats(ctx):
    await ctx.defer()
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.xeno-ai.space/stats") as resp:
            if resp.status == 200:
                data = await resp.json()
                embed = discord.Embed(title="Stats", description=f"Here are the stats of the vps")
                embed.add_field(name="RAM Usage", value=f"```{round(psutil.virtual_memory().used / 1024 / 1024 / 1024, 2)}GB / {round(psutil.virtual_memory().total / 1024 / 1024 / 1024, 2)}GB```", inline=False)
                embed.add_field(name="CPU Usage", value=f"```{psutil.cpu_percent()}% / 100%```", inline=False)
                embed.add_field(name="Generations", value=f"```{data['total_generations']}```", inline=True)
                embed.add_field(name="Database Size", value=f"```{round(data['database_size_mb'] / 1024, 2)}GB```", inline=True)
                embed.set_footer(text="Powered by XenoAI - https://xeno-ai.space")
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1051329188361142312/1053017382513299536/x_logo_23.png")
                embed.color = discord.Color.blurple()
                await ctx.respond(embed=embed)

bot.run(TOKEN)