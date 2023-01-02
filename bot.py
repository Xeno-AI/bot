import discord, os, aiohttp, asyncio, time, psutil

TOKEN = os.getenv("TOKEN")
INVITE_LINK = os.getenv("INVITE_LINK")
API_KEY = os.getenv("API_KEY")

bot = discord.Bot()

@bot.event
async def on_ready():
    b_users = []
    for guild in bot.guilds:
        b_users.append(guild.member_count)
    b_users = sum(b_users)
    print(f"[-]: Logged in as {bot.user}")
    print(f"[-]: Bot is running in {len(bot.guilds)} servers")
    print(f"[-]: Bot is accessable by {b_users} users")
    print(f"[-]: Bot is running on {psutil.cpu_count()} cores")
    print(f"[-]: Bot is running on {psutil.virtual_memory().total / 1024 ** 3} GB of RAM")
    while True:
        b_users = []
        for guild in bot.guilds:
            b_users.append(guild.member_count)
        b_users = sum(b_users)

        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.guilds)} servers | {b_users} users"))
        await asyncio.sleep(10)

@bot.command(name="generate", description="Generate an image from a prompt")
async def generate(ctx, prompt):

    async def loading_bar(msg, start):
        while True:
            await asyncio.sleep(0.7)
            if int(time.time() - start) / 15 * 100 < 100:
                bar = f"{round(int(time.time() - start) / 15 * 100, 2)}% [{'=' * int((time.time() - start) / 15 * 39)}{' ' * (39 - int((time.time() - start) / 15 * 39))}] 100%"
                embed = discord.Embed(title="Generating Image", description="Please wait while we generate your image.", color=0x2f3136)
                embed.url = f"https://api.xeno-ai.space/images/{data['task_id']}"
                embed.add_field(name="Progress", value=f"```{bar}```", inline=False)
                embed.add_field(name="Prompt", value=f"```{prompt}```", inline=False)
                embed.set_footer(text="Powered by XenoAI - https://xeno-ai.space")
                embed.color = discord.Color.blurple()
                await msg.edit_original_response(embed=embed)
            else:
                embed = discord.Embed(title="Taking longer then expected", description="Please wait while we generate your image.\nThis can take a minute.", color=0x2f3136)
                embed.url = f"https://api.xeno-ai.space/images/{data['task_id']}"
                embed.add_field(name="Progress", value=f"```100% [{'=' * 39}] 100%```", inline=False)
                embed.add_field(name="Prompt", value=f"```{prompt}```", inline=False)
                embed.set_footer(text="Powered by XenoAI - https://xeno-ai.space")
                embed.color = discord.Color.orange()
                await msg.edit_original_response(embed=embed)
                break

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
        auth = {"Authorization": API_KEY}
        async with session.post("https://api.xeno-ai.space/images", json=data, headers=auth) as resp:
            if resp.status == 200:
                data = await resp.json()
                start_time = time.time()
                while True:
                    if time.time() - start_time > 240:
                        l_bar.cancel()
                        embed = discord.Embed(title="Request Timed out", description="The API took too long to generate your image. Please try again later.")
                        embed.url = f"https://api.xeno-ai.space/images/{data['task_id']}"
                        embed.color = discord.Color.orange()
                        return await msg.edit_original_response(embed=embed)
                    async with session.get(f"https://api.xeno-ai.space/images/{data['task_id']}") as resp:
                        data = await resp.json()
                        if data["status"] == "complete":
                            l_bar.cancel()
                            embed = discord.Embed(title="Generated Image", description=f"Your image has been generated in {round(time.time() - start, 2)} seconds\nImage requested by <@{ctx.user.id}>\nSeed: {data['seed']}")
                            embed.url = f"https://api.xeno-ai.space/images/{data['task_id']}"
                            embed.add_field(name="Prompt", value=f"```{prompt}```", inline=True)
                            embed.set_footer(text="Powered by XenoAI - https://xeno-ai.space")
                            embed.color = discord.Color.blurple()
                            embed.set_image(url=data["image"])
                            view = discord.ui.View()
                            view.add_item(discord.ui.Button(label="Download", row=0, url=data["image"]))
                            view.add_item(discord.ui.Button(label="Invite Bot", row=0, url=INVITE_LINK))
                            await msg.edit_original_response(embed=embed, view=view)
                            break
                        else:
                            continue
            else:
                l_bar.cancel()
                embed = discord.Embed(title="API Offline", description=f"The API is currently offline, please try again later.")
                embed.set_footer(text="Powered by XenoAI - https://xeno-ai.space")
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1051329188361142312/1053017382513299536/x_logo_23.png")
                embed.color = discord.Color.red()
                await msg.edit_original_response(embed=embed)

bot.run(TOKEN)