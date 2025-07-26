import orderedDataStore
import discordEmbeds
import discord

def createDescription(topRollers, page):
    description_string = ""
    rank = (page-1) * 10
    for Roller in topRollers:
        rank += 1
        User = orderedDataStore.get_user(Roller["id"])["name"]

        description_string += f"**{rank}. {User}** - {Roller['value']:,}\n"

    return description_string


def NextPage(data_name, page_num, entries):
    return orderedDataStore.NextLeaderPage(data_name=data_name, page_num=page_num, entries=entries)

def CreateLeaderEmbed(top_rollers, name, page):
    description = createDescription(top_rollers, page)
    embed = discordEmbeds.leaderEmbed(page, name, description)

    return embed


class ButtonView(discord.ui.View):
    def __init__(self, *, data_name, timeout=180, page=1, leader_pages=[], most_recent_pages=None, name="Fall Back"):
        super().__init__(timeout=timeout)
        self.name = name
        self.data_name = data_name
        self.page = page
        self.leaderPages = leader_pages
        self.mostRecentPage = most_recent_pages

    def next_page(self):
        self.page += 1

        if self.page <= len(self.leaderPages):
            embed = self.leaderPages[self.page - 1]
        else:
            nextPage = NextPage(self.data_name, self.page, self.mostRecentPage)
            if not nextPage:
                self.page -= 1
                return None

            self.mostRecentPage = nextPage
            embed = CreateLeaderEmbed(self.mostRecentPage['orderedDataStoreEntries'], self.name, self.page)

            self.leaderPages.append(embed)

        return embed


    
    def previous_page(self):
        self.page -= 1
        embed = self.leaderPages[self.page-1]
        
        return embed

    @discord.ui.button(label="Back", style=discord.ButtonStyle.success, emoji="⬅️")
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page - 1 < 1:
            await interaction.response.defer()
            return

        embed = self.previous_page()
        
        await interaction.response.edit_message(embed=embed)


    
    @discord.ui.button(label="Next", style=discord.ButtonStyle.success, emoji="➡️")
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = self.next_page()

        if not embed:
            await interaction.response.defer()

        await interaction.response.edit_message(embed=embed)
