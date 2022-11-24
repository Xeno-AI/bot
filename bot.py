import discord, os, aiohttp, asyncio, json, time

TOKEN = os.getenv("DISCORD_TOKEN")

bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"[-]: Logged in as {bot.user}")
    for guild in bot.guilds:
        print(f"[-]: {guild.name} ({guild.id})")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.guilds)} servers", status=discord.Status.dnd))

@bot.command(name="generate", description="Generate an image from a prompt")
async def generate(ctx, prompt):
    async def loading_bar(msg, start):
        while True:
            await asyncio.sleep(1)
            if int(time.time() - start) / 8 * 100 < 100:
                bar = f"{int(time.time() - start) / 8 * 100}% [{'=' * int((time.time() - start) / 8 * 10)}{'-' * (10 - int((time.time() - start) / 8 * 10))}] 100%"
                embed = discord.Embed(title="Generating Image", description=bar, color=0x2f3136)
                embed.add_field(name="Prompt", value=f"```{prompt}```", inline=False)
                embed.set_footer(text="Powered by XenoAI - https://xeno-ai.space")
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1042097828434034798/1044923201744023572/x_logo_21.png")
                embed.color = discord.Color.blurple()
                await msg.edit_original_response(embed=embed)
            else:
                return True

    async def upload(interaction):
        if ctx.author != interaction.user:
            return await interaction.response.send_message("You cannot do this", ephemeral=True)
        channel = bot.get_channel(1043953820125896715)
        await channel.send(f"**Prompt** {prompt}\n{data['output']}")
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="D1", url=data["images"][0]))
        view.add_item(discord.ui.Button(label="D2", url=data["images"][1]))
        view.add_item(discord.ui.Button(label="D3", url=data["images"][2]))
        btnend = discord.ui.Button(label="Upload to Xeno-AI", style=discord.ButtonStyle.primary)
        btnend.disabled = True
        view.add_item(btnend)
        await interaction.response.edit_message(embed=embed, view=view)

    embed = discord.Embed(title="Generating Image", description="Please wait while we generate your image.")
    embed.add_field(name="Prompt", value=f"```{prompt}```", inline=False)
    embed.set_footer(text="Powered by XenoAI - https://xeno-ai.space")
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1042097828434034798/1044923201744023572/x_logo_21.png")
    embed.color = discord.Color.blurple()
    msg = await ctx.respond(embed=embed)
    start = time.time()
    loading_bar = asyncio.create_task(loading_bar(msg, start))
    async with aiohttp.ClientSession() as session:
        auth = {"Authorization": os.getenv("AI_TOKEN")}
        async with session.post("https://api.xeno-ai.space/images", data={"prompt": prompt}, headers=auth) as resp:
            if resp.status == 200:
                loading_bar.cancel()
                data = await resp.json()
                embed = discord.Embed(title="Generated Image", description=f"Your image has been generated in {round(time.time() - start, 2)} seconds")
                embed.add_field(name="Prompt", value=f"```{prompt}```", inline=False)
                embed.add_field(name="Requested by", value=f"```{ctx.author.name}```", inline=True)
                embed.add_field(name="API Version", value=f"```{data['version']}```", inline=True)
                embed.set_footer(text="Powered by XenoAI - https://xeno-ai.space")
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1042097828434034798/1044923201744023572/x_logo_21.png")
                embed.color = discord.Color.blurple()
                embed.set_image(url=data["output"])
                view = discord.ui.View()
                view.add_item(discord.ui.Button(label="D1", url=data["images"][0]))
                view.add_item(discord.ui.Button(label="D2", url=data["images"][1]))
                view.add_item(discord.ui.Button(label="D3", url=data["images"][2]))
                btnend = discord.ui.Button(label="Upload to Xeno-AI", style=discord.ButtonStyle.primary)
                btnend.callback = upload
                view.add_item(btnend)
                await msg.edit_original_response(embed=embed, view=view)
            else:
                embed = discord.Embed(title="Error", description=f"An error occurred while generating your image. Please try again later.")
                embed.set_footer(text="Powered by XenoAI - https://xeno-ai.space")
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1042097828434034798/1044923201744023572/x_logo_21.png")
                embed.color = discord.Color.red()
                await msg.edit_original_response(embed=embed)

bot.run(TOKEN)