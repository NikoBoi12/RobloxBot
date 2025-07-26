import discord

def leaderEmbed(pageNum, name, description):
    embed = discord.Embed(
        title=f"🏆 Top {name}",
        color=discord.Color.purple()
    )
    embed.description = description
    embed.set_footer(text=f"Page {pageNum}")
    
    return embed