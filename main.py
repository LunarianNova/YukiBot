import asyncio
import math
import random
import discord
import sqlite3

import discord_ui
from discord.ext import commands
from discord_ui import UI, LinkButton, Button, SlashOption, AutocompleteInteraction

with open('token.txt') as fp:
    token = fp.read()

intents = discord.Intents.default()
client = commands.Bot(command_prefix="y?", intents=intents)
ui = UI(client)
client.remove_command("help")


def update_account(player):
    db = sqlite3.connect('Beta.db')
    cursor = db.cursor()
    cursor.execute(
        f'''UPDATE main SET maxhealth = {player.maxhealth}, maxdamage = {player.maxdamage}, health = {player.health}, 
            area = {player.area}, xp = {player.xp}, coins = {player.coins}, level = {player.level}, deaths = {player.deaths},
            equipped = "{player.equipped}", inventory = "{player.inventory}", name="{player.name}",
            kills = "{player.kills}" WHERE playerid={player.playerid}''')
    db.commit()
    db.close()


def open_account(user: discord.User, new=False, return_all=False):
    if not return_all:
        if not new:
            db = sqlite3.connect('Beta.db')
            cursor = db.cursor()
            cursor.execute(
                f'''SELECT userid, health, maxdamage, coins, xp, deaths, area, maxhealth, level, equipped, inventory, name, playerid, ismain, kills FROM main WHERE userid={user.id}''')
            plrs = cursor.fetchall()
            if not plrs:
                cursor.execute("SELECT * FROM main ORDER BY playerid DESC LIMIT 1;")
                result = cursor.fetchone()
                cursor.execute(
                    f'''INSERT INTO main (userid, health, maxdamage, coins, xp, deaths, area, maxhealth, level, equipped, inventory, name, ismain, kills) VALUES({user.id}, 25, 5, 10, 0, 0, 1, 25, 1, "Basic Sword, Basic Shield, Basic Armor", "Basic Shield, Basic Sword", "Player {str(int(result[0]) + 1)}", 1, "0, 0, 0, 0, 0, 0, 0, 0, 0, 0")''')
                cursor.execute(
                    f'''SELECT userid, health, maxdamage, coins, xp, deaths, area, maxhealth, level, equipped, inventory, name, playerid, ismain, kills FROM main WHERE userid={user.id}''')
                plr = cursor.fetchone()
            else:
                for player in plrs:
                    if player[13] == 1:
                        plr = player
            db.commit()
            db.close()
            result = Player(plr[11], plr[1], plr[2], plr[3], plr[4], plr[5], plr[6], plr[7], plr[8], plr[0],
                            plr[9], plr[10], plr[12], plr[14])
            return result
        db = sqlite3.connect('Beta.db')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM main ORDER BY playerid DESC LIMIT 1;")
        result = cursor.fetchone()
        cursor.execute(
            f'''INSERT INTO main (userid, health, maxdamage, coins, xp, deaths, area, maxhealth, level, equipped, inventory, name, ismain, kills) VALUES({user.id}, 25, 5, 10, 0, 0, 1, 25, 1, "Basic Sword, Basic Shield, Basic Armor", "Basic Shield, Basic Sword", "Player {str(int(result[0]) + 1)}", 1, "0, 0, 0, 0, 0, 0, 0, 0, 0, 0")''')
        cursor.execute(
            f'''SELECT userid, health, maxdamage, coins, xp, deaths, area, maxhealth, level, equipped, inventory, name, playerid, kills FROM main WHERE userid={user.id}''')
        plr = cursor.fetchone()
        db.commit()
        db.close()
        result = Player(plr[11], plr[1], plr[2], plr[3], plr[4], plr[5], plr[6], plr[7], plr[8], plr[0],
                        plr[9], plr[10], plr[12], plr[13])
        return result
    db = sqlite3.connect('Beta.db')
    cursor = db.cursor()
    cursor.execute(
        f'''SELECT userid, health, maxdamage, coins, xp, deaths, area, maxhealth, level, equipped, inventory, name, playerid, kills FROM main WHERE userid={user.id}''')
    players = []
    plrs = cursor.fetchall()
    for plr in plrs:
        players.append(Player(plr[11], plr[1], plr[2], plr[3], plr[4], plr[5], plr[6], plr[7], plr[8], plr[0],
                              plr[9], plr[10], plr[12], plr[13]))
    db.commit()
    db.close()
    return players


def xp_for_level(level):
    return int(round(math.pow(level, 2.8) + 100))


# Initialize a player
class Player:
    def __init__(self, name, health, maxdamage, coins, xp, deaths, area, maxhealth, level, userid, equipped, inventory,
                 playerid, kills):
        self.name = name
        self.health = health
        self.maxdamage = maxdamage
        self.coins = coins
        self.xp = xp
        self.deaths = deaths
        self.area = area
        self.maxhealth = maxhealth
        self.level = level
        self.userid = userid
        self.equipped = equipped
        self.inventory = inventory
        self.playerid = playerid
        self.kills = kills


class Enemy:
    def __init__(self, name, health, attack, coins, xp, tohit, lvlmult):
        self.name = name
        self.health = health
        self.attack = attack
        self.coins = coins
        self.xp = xp
        self.tohit = tohit
        self.lvlmult = lvlmult


# Event when the bot starts
@client.event
async def on_ready():
    print("Ready!")
    print(client.user.name)
    await client.change_presence(activity=discord.Game("/help"))
    # Make tables
    db = sqlite3.connect('Beta.db')
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS main(
            playerid INTEGER PRIMARY KEY AUTOINCREMENT,
            userid BIGINT,
            health BIGINT,
            maxdamage BIGINT,
            coins BIGINT,
            xp BIGINT,
            deaths BIGINT,
            area BIGINT,
            maxhealth BIGINT,
            level BIGINT,
            equipped TEXT,
            inventory TEXT,
            name TEXT,
            ismain TINYINT,
            kills TEXT
            )''')
    db.commit()
    db.close()


async def isitme(ctx):
    return ctx.author.id == 803766890023354438


@client.command()
@commands.check(isitme)
async def sql(ctx, *, sqlcode):
    db = sqlite3.connect('Beta.db')
    cursor = db.cursor()
    cursor.execute(f'''{sqlcode}''')
    await ctx.send("SQL Executed\n" + str(cursor.fetchall()))
    db.commit()
    db.close()


# Basic help command
@ui.slash.command(name="help", description="An outdated help command")
async def help(ctx):
    def make_embed(commands):
        embed = discord.Embed(title="Help for YukiBot", color=0xff0099)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.add_field(name="\u200b",
                        value=commands)
        return embed

    page1 = ''':question: **General Commands**
            **about:** Get random info about the bot
            **profile:** View a user's stats and their profile
            **top (category):** View the top 10 users on the Earth
            **info (item):** Get stats and sell value of an item
            **sell (item):** Sell for the amount in /info
            **shop:** Opens the shop
            **buy (item):** Buy a listing in the shop
    
            :crossed_swords: **Combat Commands**
            **fight:** Fight an enemy to gain xp and coins
            **heal (amount):** Heal yourself from your battle scars
            
            :mechanical_arm: **Gear Commands**
            **inv:** View your inventory
            **unequip (location):** Unequip a piece of gear
            **equip (item) (location):** Equip a piece of gear'''
    page2 = ''':disguised_face: **Character Commands**
            **characters:** View all your characters
            **new:** Make a new character
            **delete (num):** Delete specified character
            **rename (name):** Rename current character
            **change (num):** Change active character'''
    message = await ctx.send(embed=make_embed(page1), components=[Button("Page 1"), Button("Page 2")])
    try:
        btn = await message.wait_for("button", client, by=ctx.author, timeout=20)
    except asyncio.TimeoutError:
        return
    while True:
        await btn.respond()
        if btn.component.label.lower() == "page 1":
            page = page1
        elif btn.component.label.lower() == "page 2":
            page = page2
        await message.edit(embed=make_embed(page), components=[Button("Page 1"), Button("Page 2")])
        try:
            btn = await message.wait_for("button", client, by=ctx.author, timeout=20)
        except asyncio.TimeoutError:
            return


# Generate an enemy with paramaters from fight()
def generate_enemy(area):
    areadict = {1: [17, 23, 4, 13, 18, ["Rabbit", "Squirrel", "Woodchuck", "Garden Snake"], 8, 14, 30, 5],
                "1g": [15, 20, 0, 52, 72, ["Living Gem"], 32, 56, 30, 5],
                2: [40, 54, 8.5, 50, 64, ["Giant Spider", "Horse", "Baby Bear", "Commoner", "Lesser Spirit"], 200, 220,
                    20, 2],
                "2g": [40, 50, 0, 200, 256, ["Golden Capsule"], 800, 880,
                       20, 2],
                3: [85, 100, 18, 130, 150, ["Orc", "Spirit", "Mother Bear", "Knight", "Cultist"], 800, 860, 12, 1.6],
                "3g": [100, 120, 0, 520, 600, ["Diamond"], 3200, 3440, 12, 1.6],
                "1b": [70, 70, 10, 250, 250, ["Orc"], 50, 50, 0, 4],
                "2b": [130, 130, 20, 250, 250, ["Greater Spirit"], 150, 150, 0, 2]}
    rand = random.randint(1, 100)
    if rand <= 2:
        try:
            int(area)
            area = str(area) + "g"
        except:
            pass
    enemylist = areadict.get(area)
    name = random.choice(enemylist[5])
    coins = random.randint(enemylist[3], enemylist[4])
    health = random.randint(enemylist[0], enemylist[1])
    attack = enemylist[2]
    xp = random.randint(enemylist[6], enemylist[7])
    enemy = Enemy(name, health, attack, coins, xp, enemylist[8], enemylist[9])
    return enemy


def handle_items(items):
    bonuses = {"tohit": 0, "togethit": 0, "xp": 0, "enemydamage": 0}
    for item in items.split(", "):
        if item.lower() == "basic shield" or item.lower() == "brass armor" or item.lower() == "brass sword":
            bonuses["togethit"] += 5
        elif item.lower() == "wood armor" or item.lower() == "aluminium armor":
            bonuses["enemydamage"] -= 1
        elif item.lower() == "thorn armor" or item.lower() == "brass armor":
            bonuses["enemydamage"] -= 2
        elif item.lower() == "wood shield" or item.lower() == "aluminium shield" or item.lower() == "serrated shield":
            bonuses["togethit"] += 10
        elif item.lower() == "brass shield":
            bonuses["togethit"] += 15
        elif item.lower() == "aluminium sword" or item.lower() == "brass shield" or item.lower() == "aluminium shield" or item.lower() == "aluminium armor":
            bonuses["xp"] += 0.05
    return bonuses


# I can make the code a dict
@ui.slash.command(name="top", description="Get the top players of a category", options=[
    SlashOption(str, "criteria", "the criteria", True,
                choices=[{"name": "kills", "value": "kills"}, {"name": "coins", "value": "coins"},
                         {"name": "level", "value": "level"}, {"name": "deaths", "value": "deaths"},
                         {"name": "damage", "value": "damage"}])])
async def top(ctx, criteria):
    def new_sort(e):
        return e[0]

    db = sqlite3.connect('Beta.db')
    cursor = db.cursor()
    if criteria == "deaths":
        cursor.execute('SELECT deaths, userid, name FROM main ORDER BY deaths DESC LIMIT 10')
    elif criteria == "level":
        cursor.execute('SELECT level, userid, name FROM main ORDER BY level DESC LIMIT 10')
    elif criteria == "coins":
        cursor.execute('SELECT coins, userid, name FROM main ORDER BY coins DESC LIMIT 10')
    elif criteria == "damage":
        cursor.execute('SELECT maxdamage, userid, name FROM main ORDER BY maxdamage LIMIT 10')
    elif criteria == "kills":
        cursor.execute('SELECT kills, userid, name FROM main ORDER BY maxdamage LIMIT 10')
    else:
        await ctx.send("I'm sorry, your input is not a valid criteria")
        return
    users = cursor.fetchall()
    users = list(users)
    embed = discord.Embed(title=f"Top Players in '{criteria}'", color=0xff0099)
    if criteria == "kills":
        for i in range(0, len(users)):
            kills = 0
            user = list(users[i])
            killsper = user[0].split(", ")
            for a in killsper:
                kills += int(a)
            user[0] = kills
            users[i] = user
    users.sort(key=new_sort, reverse=True)
    for i in range(0, 9):
        try:
            user = await client.fetch_user(users[i][1])
            embed.add_field(name=str(i + 1) + ": " + user.name + "#" + user.discriminator + " - " + str(users[i][2]),
                            value=users[i][0], inline=False)
        except:
            pass
    await ctx.send(embed=embed)
    db.commit()
    db.close()


@commands.cooldown(1, 10, commands.BucketType.user)
@ui.slash.command(name="fight", description="Fight to progress",
                  options=[SlashOption(int, "area", "optional argument for the area to fight in (1, 2, etc)", False)])
async def fight(ctx, area=None):
    plr = open_account(ctx.author)
    item_bonuses = handle_items(plr.equipped)

    def get_attack(minhit, max):
        if max != 0:
            attack = random.randint(1, 100)
            if attack > minhit:
                damage = math.ceil((attack / 100) * max)
                if attack >= 96:
                    critical = 1 + random.randint(20, 100) / 100.0
                    damage = int(round(damage * critical))
                return damage
            return 0
        return 0

    def make_embed(footer):
        embed = discord.Embed(title=f"{enemy.name}   HP: {health}/{enemy.health}",
                              description=f"{plr.name}: {plr.health}/{plr.maxhealth}", color=0xff0099)
        embed.add_field(name="Attack", value="High chance of hitting, enemy also gets an attack", inline=False)
        embed.add_field(name="Counter", value="A good chance you counter the next attack, a small chance you lose "
                                              "attack opportunity", inline=False)
        embed.add_field(name="Auto", value="Automatically does attacks, however, your damage is halved", inline=False)
        embed.set_footer(text=footer)
        return embed

    if not area:
        buttons = []
        for i in range(plr.area - 3, plr.area + 1):
            if i > 0:
                buttons.append(Button(label="Area " + str(i), color="green", new_line=False))
        buttons.append(Button(label="Area " + str(plr.area) + " Boss", color="red", new_line=False))
        message = await ctx.send("<@" + str(ctx.author.id) + ">", components=buttons, hidden=True)
        try:
            btn = await message.wait_for("button", client, by=ctx.author, timeout=20)
        except asyncio.TimeoutError:
            return
        area = int(btn.component.label.lower().split(" ")[1])
        if btn.component.label.lower().endswith("boss"):
            boss = True
            enemy = generate_enemy(str(area) + "b")
        else:
            boss = False
            enemy = generate_enemy(area)
        health = enemy.health
        dmg = "Get ready"
        eph = await btn.respond(embed=make_embed(dmg),
                                components=[Button(label="Attack", color="red"), Button(label="Counter"),
                                            Button(label="Auto", color="green")], hidden=True)
    else:
        if area <= plr.area:
            boss = False
            enemy = generate_enemy(area)
            health = enemy.health
            dmg = "Get ready"
            eph = await ctx.send(embed=make_embed(dmg),
                                 components=[Button(label="Attack", color="red"), Button(label="Counter"),
                                             Button(label="Auto", color="green")], hidden=True)
        else:
            await ctx.send("You haven't reached that area!", hidden=True)
            return
    while health > 0 and plr.health > 0:
        try:
            btn = await eph.wait_for("button", client, by=ctx.author, timeout=20)
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond and died", hidden=True)
            plr.health = 0
        else:
            tohit = round((32 * area) - (2 * plr.level) + ((10 * math.pow(1.35, area)) - 15)) - item_bonuses["tohit"]
            if boss:
                tohit += 15
            dmg = get_attack(tohit, plr.maxdamage)
            edmg = get_attack(enemy.tohit + (plr.level * enemy.lvlmult) + item_bonuses["togethit"],
                              enemy.attack + item_bonuses["enemydamage"])
            if btn.component.label.lower() == "attack":
                health -= dmg
                plr.health -= edmg
                if dmg == 0:
                    dmg = "You missed!"
                else:
                    if dmg > plr.maxdamage:
                        dmg = "You dealt " + str(dmg) + " damage, CRITICAL!"
                    else:
                        dmg = "You dealt " + str(dmg) + " damage"
                if edmg == 0:
                    dmg += "\nEnemy " + "missed!"
                else:
                    if edmg > enemy.attack:
                        dmg += "\nEnemy dealt " + str(edmg) + " damage, CRITICAL!"
                    else:
                        dmg += "\nEnemy dealt " + str(edmg) + " damage"
            elif btn.component.label.lower() == "counter":
                outcome = random.randint(1, 100)
                if edmg == 0:
                    health -= dmg
                    dmgstr = "The enemy missed, you counter attack\n"
                    if dmg == 0:
                        dmgstr += "You missed!"
                    else:
                        if dmg > plr.maxdamage:
                            dmgstr += "You dealt " + str(dmg) + " damage, CRITICAL!"
                        else:
                            dmgstr += "You dealt " + str(dmg) + " damage"
                    dmg = dmgstr
                elif outcome <= 10:
                    dmg = "You repelled " + str(math.ceil(edmg / 4)) + " damage\nBut took " + str(
                        math.ceil(edmg / 2)) + " damage"
                    health -= math.ceil(edmg / 4)
                    plr.health -= math.ceil(edmg / 2)
                elif 42 >= outcome > 10:
                    dmg = "You repelled " + str(math.ceil(edmg / 2)) + " damage!"
                    health -= math.ceil(edmg / 2)
                else:
                    dmg = "You failed and took " + str(edmg) + " damage"
                    plr.health -= edmg
            elif btn.component.label.lower() == "auto":
                health -= dmg / 2
                plr.health -= edmg
                while health > 0 and plr.health > 0:
                    dmg = get_attack(tohit, plr.maxdamage)
                    edmg = get_attack(enemy.tohit + (plr.level * enemy.lvlmult) + item_bonuses["togethit"],
                                      enemy.attack + item_bonuses["enemydamage"])
                    health -= dmg / 2
                    plr.health -= edmg
            await eph.edit(embed=make_embed(dmg),
                           components=[Button(label="Attack", color="red"), Button(label="Counter"),
                                       Button(label="Auto", color="green")])
            await btn.respond()
    if health <= 0:
        if plr.health <= 0:
            plr.health = 1
        if boss:
            plr.area += 1
            await ctx.send("<@" + str(ctx.author.id) + "> Has defeated the area " + str(
                area) + " boss and moved on to area " + str(area + 1) + "!")
        await on_victory(plr, enemy, eph, area)
    elif plr.health <= 0:
        await on_death(plr, enemy, eph, health)


async def common(ctx):
    plr = open_account(ctx.author)
    while plr.xp >= xp_for_level(plr.level + 1):
        plr.level += 1
        plr.maxhealth += 5
        plr.health += 5
        plr.xp -= xp_for_level(plr.level)
        update_account(plr)
        await ctx.send("<@" + str(plr.userid) + "> Levelled up!\n+5 Max Health\nNew Level: " + str(plr.level))


@ui.slash.command(name="profile", description="Get someone's profile",
                  options=[SlashOption(discord.Member, "user", "a user", False)])
async def profile(ctx, user: discord.Member = None):
    if user is None:
        user = ctx.author
    kills = 0
    plr = open_account(user)
    nextlevel = xp_for_level(plr.level + 1)
    left = ":right_facing_fist:"
    right = ":left_facing_fist:"
    if "sword" in plr.equipped.split(', ')[0].lower():
        left = ":dagger:"
    if "sword" in plr.equipped.split(', ')[1].lower():
        right = ":dagger:"
    if "shield" in plr.equipped.split(', ')[0].lower():
        left = ":shield:"
    if "shield" in plr.equipped.split(', ')[1].lower():
        right = ":shield:"
    killsper = plr.kills.split(", ")
    for a in killsper:
        kills += int(a)
    embed = discord.Embed(title=f"{plr.name}'s Profile", color=0xff0099)
    embed.set_thumbnail(url=user.avatar_url)
    embed.add_field(name="Progression",
                    value=f":arrow_up: Level: {plr.level}\n:star: XP: {plr.xp}/{nextlevel}\n:door: Area: {plr.area}",
                    inline=False)
    embed.add_field(name="Stats",
                    value=f":hearts: Health: {plr.health}/{plr.maxhealth}\n"
                          f":crossed_swords: Max Damage: {plr.maxdamage}\n:coin: Coins: {plr.coins}\n"
                          f":skull: Deaths: {plr.deaths}\n:skull_crossbones: Kills: {kills}",
                    inline=True)
    embed.add_field(name="Gear",
                    value=f"{left} Left Hand: {plr.equipped.split(', ')[0]}\n"
                          f"{right}  Right Hand: {plr.equipped.split(', ')[1]}\n"
                          f":mechanical_arm: Armor: {plr.equipped.split(', ')[2]}",
                    inline=True)
    await ctx.send(embed=embed)


@ui.slash.command(name="heal", description="Heal yourself",
                  options=[SlashOption(int, "amount", "optional amount of health to heal", False)])
async def heal(ctx, amount=None):
    plr = open_account(ctx.author)
    if amount is None:
        amount = plr.maxhealth - plr.health
    amount = int(amount)
    if plr.health < plr.maxhealth:
        if plr.coins >= math.ceil(amount / 2):
            plr.coins -= math.ceil(amount / 2)
            plr.health += amount
            await ctx.send("I've healed " + ctx.author.display_name + " for " + str(amount) + " points!\n-" + str(
                math.ceil(amount / 2)) + " Coins", hidden=True)
            update_account(plr)
        else:
            await ctx.send(ctx.author.display_name + " you don't have enough to heal, I can't do this for free!",
                           hidden=True)
    else:
        await ctx.send("You can't fool me " + ctx.author.display_name + ", you don't need healing.", hidden=True)


@ui.slash.command(name="inv", description="View your inventory", options=[
    SlashOption(str, "public", "brag and display your inventory to everyone", False,
                choices=[{"name": "False", "value": "False"}, {"name": "True", "value": "True"}])])
async def inv(ctx, public="False"):
    plr = open_account(ctx.author)
    embed = discord.Embed(title=f"{ctx.author.display_name}'s Inventory", color=0xff0099)
    itemstring, matstring = "", ""
    if public == "False":
        public = False
    else:
        public = True
    items = {}
    for item in plr.inventory.split(", "):
        try:
            items[item] += 1
        except KeyError:
            items[item] = 1
    items = dict(sorted(items.items(), key=lambda item: item[1], reverse=True))
    for item in items.keys():
        if "shield" in item.lower():
            itemstring += ":shield: **" + item + "**: " + str(items[item]) + "\n"
        elif "sword" in item.lower():
            itemstring += ":dagger: **" + item + "**: " + str(items[item]) + "\n"
        elif "armor" in item.lower():
            itemstring += ":mechanical_arm: **" + item + "**: " + str(items[item]) + "\n"
        else:
            if len(item.lower()) > 2:
                matstring += "**" + item + "**: " + str(items[item]) + "\n"
    if itemstring == '':
        itemstring = "None"
    if matstring == '':
        matstring = "None"
    embed.add_field(name="Items", value=itemstring)
    embed.add_field(name="Materials", value=matstring)
    await ctx.send(embed=embed, hidden=not public)


@ui.slash.command(name="unequip", description="Unequip from a slot", options=[
    SlashOption(str, "slot", "slot to unequip from", True,
                choices=[{"name": "right", "value": "right"}, {"name": "left", "value": "left"},
                         {"name": "armor", "value": "armor"}])])
async def unequip(ctx, slot=None):
    plr = open_account(ctx.author)
    left, right, armor = plr.equipped.split(", ")
    items = plr.inventory.split(", ")
    if slot is None:
        await ctx.send("Please specify a hand to unequip", hidden=True)
        return
    elif slot.lower() == "right":
        plr.equipped = left + ", None, " + armor
        item = right
        await ctx.send("Successfully unequipped " + right + " from right hand", hidden=True)
    elif slot.lower() == "left":
        plr.equipped = "None, " + right + ", " + armor
        item = left
        await ctx.send("Successfully unequipped " + left + " from left hand", hidden=True)
    elif slot.lower() == "armor":
        plr.equipped = left + ", " + right + ", None"
        item = armor
        await ctx.send("Successfully unequipped " + armor + " from armor slot", hidden=True)
    else:
        await ctx.send("That is not a valid location, please specify 'left', 'right', or 'armor'", hidden=True)
        return
    if items[0] != '':
        items.append(item)
        plr.inventory = ", ".join(items)
    else:
        plr.inventory = item
    handle_equip(plr, item, True)


def handle_equip(player, item, is_unequip):
    bonuses = {"health": 0, "damage": 0}
    if item.lower() == "basic sword" or item.lower() == "serrated shield":
        bonuses["damage"] += 1
    elif item.lower() == "basic armor":
        bonuses["health"] += 5
    elif item.lower() == "brass armor":
        bonuses["health"] += 15
    elif item.lower() == "wood sword" or item.lower() == "aluminium sword":
        bonuses["damage"] += 2
    elif item.lower() == "wood armor" or item.lower() == "aluminium armor":
        bonuses["health"] += 10
    elif item.lower() == "thorn armor":
        bonuses["health"] -= 5
        bonuses["damage"] += 2
    elif item.lower() == "spiky sword":
        bonuses["damage"] += 3
    elif item.lower() == "brass sword":
        bonuses["damage"] += 4
    if is_unequip:
        player.maxhealth -= bonuses["health"]
        player.health -= bonuses["health"]
        player.maxdamage -= bonuses["damage"]
    else:
        player.maxhealth += bonuses["health"]
        player.health += bonuses["health"]
        player.maxdamage += bonuses["damage"]
    update_account(player)


@ui.slash.command(name="rename", description="Rename your active character",
                  options=[SlashOption(str, "name", "new name for character", True)])
async def rename(ctx, *, name=None):
    if name is None:
        await ctx.send("Please provide a name!", hidden=True)
        return
    plr = open_account(ctx.author)
    if len(name) > 32:
        await ctx.send("Your new name needs to be less than 32 characters!", hidden=True)
        return
    await ctx.send(f"'{plr.name}' was renamed to '{name}'", hidden=True)
    plr.name = name
    update_account(plr)


@ui.slash.command(name="new", description="Make a new character")
async def new(ctx):
    db = sqlite3.connect('Beta.db')
    cursor = db.cursor()
    cursor.execute(
        f'''SELECT userid, health, maxdamage, coins, xp, deaths, area, maxhealth, level, equipped, inventory, name, ismain FROM main WHERE userid={ctx.author.id}''')
    plrs = cursor.fetchall()
    if len(plrs) < 5:
        for player in plrs:
            if player[12] == 1:
                cursor.execute(f'''UPDATE main SET ismain=0 WHERE playerid = {player[0]}''')
        db.commit()
        db.close()
        open_account(ctx.author, True)
        await ctx.send("Created new character! Use /characters to view your characters")
    else:
        await ctx.send("You can't have more than 5 characters! Please delete one")
        db.commit()
        db.close()


async def char_option_generator(ctx):
    chars = open_account(ctx.author, return_all=True)
    count = 1
    options = []
    for char in chars:
        options.append({"name": str(count) + ". " + char.name, "value": str(count)})
        count += 1
    return options


async def inv_option_generator(ctx):
    char = open_account(ctx.author)
    options = []
    items = char.inventory.split(", ")
    for item in items:
        options.append({"name": item, "value": item.lower()})
    return options


async def item_option_generator(ctx):
    options = []
    items = ['Basic Armor', 'Basic Shield', 'Basic Sword', 'Wood Armor', 'Wood Shield', 'Wood Sword', 'Aluminium Armor',
             'Aluminium Shield', 'Aluminium Sword', 'Thorn Armor', 'Serrated Shield', 'Spiky Sword', 'Brass Armor',
             'Brass Shield', 'Brass Sword']
    for item in items:
        options.append({"name": item, "value": item.lower()})
    return options


@ui.slash.command(name="equip", description="Equip an item",
                  options=[SlashOption(str, "item", "item to equip", True, choice_generator=inv_option_generator),
                           SlashOption(str, "slot", "slot to equip to", True,
                                       choices=[{"name": "right", "value": "right"}, {"name": "left", "value": "left"},
                                                {"name": "armor", "value": "armor"}])])
async def equip(ctx, item, slot):
    plr = open_account(ctx.author)
    left, right, armor = plr.equipped.split(", ")
    hand = slot
    item = item.lower()
    split = plr.inventory.lower().split(", ")
    if item in split:
        if hand is None:
            await ctx.send("Your syntax is wrong, the correct syntax is 'equip basic sword right'", hidden=True)
            return
        elif hand.lower() == "right":
            if right != "None":
                await unequip(ctx, "right")
            if "armor" in item.lower():
                await ctx.send("You can't equip armor in your hand!", hidden=True)
                return
            plr.equipped = left + ", " + item.title() + ", " + armor
            await ctx.send("Successfully equipped " + item.title() + " to right hand", hidden=True)
        elif hand.lower() == "left":
            if left != "None":
                await unequip(ctx, "left")
            if "armor" in item.lower():
                await ctx.send("You can't equip armor in your hand!", hidden=True)
                return
            plr.equipped = item.title() + ", " + right + ", " + armor
            await ctx.send("Successfully equipped " + item.title() + " to left hand", hidden=True)
        elif hand.lower() == "armor":
            if armor != "None":
                await unequip(ctx, "armor")
            if "armor" in item.lower():
                plr.equipped = left + ", " + right + ", " + item.title()
                await ctx.send("Successfully equipped " + item.title() + " to armor slot", hidden=True)
            else:
                await ctx.send("You can only equip armor in your armor slot!", hidden=True)
                return
        else:
            await ctx.send("That is not a valid location, the correct syntax is 'equip basic sword right'", hidden=True)
            return
    else:
        await ctx.send("You do not possess that item, the correct syntax is 'equip basic sword right'", hidden=True)
        return
    player = open_account(ctx.author)
    split = player.inventory.lower().split(", ")
    split.remove(item)
    split = ", ".join(split).title()
    plr.inventory = split
    handle_equip(plr, item, False)


@ui.slash.command(name="delete", description="Delete an existing character", options=[
    SlashOption(str, "char", "character to delete", True, choice_generator=char_option_generator)])
async def delete(ctx, char):
    try:
        int(char)
    except:
        await ctx.send("Your character has to be a value from /characters, ex: '/delete 3'", hidden=True)
        return
    char = int(char) - 1
    db = sqlite3.connect('Beta.db')
    cursor = db.cursor()
    cursor.execute(
        f'''SELECT playerid, userid, health, maxdamage, coins, xp, deaths, area, maxhealth, level, equipped, inventory, name, ismain FROM main WHERE userid={ctx.author.id} ORDER BY playerid ASC''')
    plrs = cursor.fetchall()
    for player in plrs:
        if player[13] == 1:
            plr = player
    if plrs[char] == plr:
        await ctx.send("You cannot delete your currently active character!", hidden=True)
        db.commit()
        db.close()
        return
    cursor.execute("DELETE FROM main WHERE playerid=?", (plrs[char][0],))
    db.commit()
    db.close()
    await ctx.send("Successfully deleted '" + plrs[char][12] + "', id " + str(plrs[char][0]), hidden=True)


@ui.slash.command(name="change", description="Change active character", options=[
    SlashOption(str, "char", "character to change to", True, choice_generator=char_option_generator)])
async def change(ctx, char):
    try:
        int(char)
    except:
        await ctx.send("Your character has to be a value from /characters, ex: '/change 3'", hidden=True)
        return
    char = int(char) - 1
    db = sqlite3.connect('Beta.db')
    cursor = db.cursor()
    cursor.execute(
        f'''SELECT playerid, userid, health, maxdamage, coins, xp, deaths, area, maxhealth, level, equipped, inventory, name, ismain FROM main WHERE userid={ctx.author.id} ORDER BY playerid ASC''')
    plrs = cursor.fetchall()
    for player in plrs:
        if player[13] == 1:
            plr = player
    if plrs[char] == plr:
        await ctx.send("This character is already active!", hidden=True)
        db.commit()
        db.close()
        return
    cursor.execute("UPDATE main SET ismain=1 WHERE playerid=?", (plrs[char][0],))
    cursor.execute("UPDATE main SET ismain=0 WHERE playerid=?", (plr[0],))
    db.commit()
    db.close()
    await ctx.send("Successfully changed to '" + plrs[char][12] + "', id " + str(plrs[char][0]), hidden=True)


@ui.slash.command(name="characters", description="View all of your characters")
async def characters(ctx):
    chars = open_account(ctx.author, return_all=True)
    embed = discord.Embed(title=f"{ctx.author.display_name}'s Characters", color=0xff0099)
    embed.set_thumbnail(url=ctx.author.avatar_url)
    count = 1
    db = sqlite3.connect('Beta.db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM main WHERE userid=? AND ismain=1", (ctx.author.id,))
    result = cursor.fetchone()
    db.commit()
    db.close()
    for plr in chars:
        active = ""
        if plr.playerid == result[0]:
            active = ":white_check_mark: "
        embed.add_field(name=active + str(count) + ". " + plr.name,
                        value=f":arrow_up: Level: {plr.level}\n:door: Area: {plr.area}\n:crossed_swords: "
                              f"Max Damage: {plr.maxdamage}\n:skull: Deaths: {plr.deaths}",
                        inline=False)
        count += 1
    await ctx.send(embed=embed)


@ui.slash.command(name="info", description="Gain information such as stats about a certain item", options=[
    SlashOption(str, "item", "item you need information on", True, choice_generator=item_option_generator),
    SlashOption(str, "public", "display info to everyone", False,
                choices=[{"name": "False", "value": "False"}, {"name": "True", "value": "True"}])])
async def info(ctx, item, public=False):
    public = bool(public)
    items = {
        "basic sword": "Sword made of paper, given to adventurers when they sign up, as paper is cheap and adventurers die often\n\n+1 Max Damage\nSells for: 0 coins",
        "basic shield": "Shield made of paper, given to adventurers when they sign up, as paper is cheap and adventurers die often\n\n+5 Dodge\nSells for: 0 coins",
        "basic armor": "Armor made of paper, does virtually nothing\n\n+5 Max Health\nSells for: 0 coins",
        "wood sword": "Sword made from the trees in the backyard of the guild\n\n+2 Max Damage\nSells for: 50 coins",
        "wood shield": "Shield made from the trees in the backyard of the guild\n\n+10 Dodge\nSells for: 50 coins",
        "wood armor": "Armor made from the trees in the backyard of the guild\n\n+10 Health\n-1 Enemy Damage\nSells for: 50 coins",
        "aluminium sword": "Sword made from cheap aluminium, enchanted with basic abilities\n\n+2 Max Damage\n+5% EXP\nSells for: 250 coins",
        "aluminium shield": "Shield made from cheap aluminium, enchanted with basic abilities\n\n+5 Dodge\n+5% EXP\nSells for: 250 coins",
        "aluminium armor": "Armor made from cheap aluminium, enchanted with basic abilities\n\n+10 Health\n+5% EXP\n-1 Enemy Damage\nSells for: 250 coins",
        "spiky sword": "Expertly crafted aluminium, with spikes for added coolness\n\n+3 Max Damage\nSells for: 200 coins",
        "serrated shield": "Heavier than most, this shield can also be used as a weapon\n\n+10 Dodge\n+1 Max Damage\nSells for: 200 coins",
        "thorn armor": "Armor made from literal thorns, enchanted to not decay, harmful to you and enemies\n\n-5 Health\n+2 Max Damage\n-2 Enemy Damage\nSells for: 200 coins",
        "brass sword": "Sword crafted from brass, fabled for making you faster\n\n+4 Damage\n+5 Dodge\nSells for: 1250 coins",
        "brass shield": "Shield crafted from brass, despite being heavy, you feel lighter with it\n\n+15 Dodge\n+5% EXP\nSells for: 1250 coins",
        "brass armor": "Armor crafted from brass, You feel lighter with it on\n\n+15 Max Health\n+5 Dodge\n-2 Enemy Damage\nSells for: 1250 coins"}
    common = ["basic sword", "basic shield", "basic armor", "wood sword", "wood shield", "wood armor", "spiky sword",
              "serrated shield", "thorn armor"]
    rare = ["aluminium sword", "aluminium shield", "aluminium armor", "brass sword", "brass shield", "brass armor"]
    rarity = "Rare" if item.lower() in rare else "Common" if item.lower() in common else "Unknown"
    if item.lower() in items:
        embed = discord.Embed(title=f"Info for {item.title()} ({rarity})",
                              description=items.get(item.lower()),
                              color=0xff0099)
        await ctx.send(embed=embed, hidden=not public)
    else:
        await ctx.send("That item does not exist!", hidden=True)


@ui.slash.command(name="sell", description="Sell an item",
                  options=[SlashOption(str, "item", "item to sell", True, choice_generator=inv_option_generator)])
async def sell(ctx, item):
    values = {"Basic Armor": 0, "Basic Shield": 0, "Baisc Sword": 0, "Wood Sword": 50, "Wood Shield": 50,
              "Wood Armor": 50, "Aluminium Sword": 250, "Aluminium Shield": 250, "Aluminium Armor": 250,
              "Spiky Sword": 200, "Serrated Shield": 200, "Thorn Armor": 200,
              "Brass Sword": 1250, "Brass Shield": 1250, "Brass Armor": 1250}
    plr = open_account(ctx.author)
    if item.title() in values.keys():
        if item.lower() in plr.inventory.lower().split(", "):
            items = plr.inventory.lower().split(", ")
            items.remove(item.lower())
            plr.inventory = (", ".join(items)).title()
            plr.coins += values.get(item.title())
            update_account(plr)
            await ctx.send("Sold " + item.title() + " for " + str(values.get(item.title())) + " coins", hidden=True)
        else:
            await ctx.send("You don't own this item!", hidden=True)
    else:
        await ctx.send("That item does not exist or can't be sold!", hidden=True)


@ui.slash.command(name="about", description="Random info on the bot")
async def about(ctx):
    db = sqlite3.connect('Beta.db')
    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) FROM main')
    users = cursor.fetchone()
    db.commit()
    db.close()
    embed = discord.Embed(title=f"YukiBot Info", color=0xff0099)
    embed.add_field(name="General",
                    value="Created by Yukiko#9966\nMade on August 14th, 2022\n921 lines of code\n17 Commands\n"
                          "" + str(users[0]) + " Users",
                    inline=False)
    embed.set_thumbnail(url=client.user.avatar_url)
    embed.set_footer(text="YukiBot ver. b0.7")
    await ctx.send(embed=embed)


@ui.slash.command(name="shop", description="Listing of all items you can buy")
async def shop(ctx):
    def make_embed(items):
        embed = discord.Embed(title="YukiBot Public Shop", color=0xff0099)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.add_field(name="Crafting", value=items)
        return embed

    page1 = "**Basic Anvil**: 500 coins\n" if True else ""
    page1 += "**Aluminium**: 500 coins\n**Log**: 50 coins"
    page2 = "Hey, this isn't a real thing!"
    message = await ctx.send(embed=make_embed(page1), components=[Button("Page 1"), Button("Page 2")])
    try:
        btn = await message.wait_for("button", client, by=ctx.author, timeout=20)
    except asyncio.TimeoutError:
        return
    while True:
        await btn.respond()
        if btn.component.label.lower() == "page 1":
            page = page1
        elif btn.component.label.lower() == "page 2":
            page = page2
        await message.edit(embed=make_embed(page), components=[Button("Page 1"), Button("Page 2")])
        try:
            btn = await message.wait_for("button", client, by=ctx.author, timeout=20)
        except asyncio.TimeoutError:
            return


async def buy_choice_generator(ctx):
    shop = ["Basic Anvil", "Aluminium", "Log"]
    opt = []
    for item in shop:
        opt.append({"name": item, "value": item.lower()})
    return opt


@ui.slash.command(name="buy", description="Buy one of the items that is listed in the shop",
                  options=[SlashOption(str, "item", "item to buy", True, choice_generator=buy_choice_generator)])
async def buy(ctx, item):
    prices = {"basic anvil": 500, "aluminium": 500, "log": 50}
    plr = open_account(ctx.author)
    item = item.lower()
    if item in prices.keys():
        if plr.coins >= prices[item]:
            plr.coins -= prices[item]
            items = plr.inventory.split(", ")
            items.append(item.title())
            plr.inventory = ", ".join(items)
            update_account(plr)
            await ctx.send("You successfully bought 1 " + item.title() + " for " + str(prices[item]) + " coins.",
                           hidden=True)
        else:
            await ctx.send("You don't have the money to buy that item!", hidden=True)
    else:
        await ctx.send("That item does not exist!", hidden=True)
        return


@ui.slash.command(name="duel", description="Duel another player",
                  options=[SlashOption(discord.Member, "player", "the player to duel", True)])
async def duel(ctx, player):
    def get_attack(minhit, max):
        if max != 0:
            attack = random.randint(1, 100)
            if attack > minhit:
                damage = math.ceil((attack / 100) * max)
                if attack >= 96:
                    critical = 1 + random.randint(20, 100) / 100.0
                    damage = int(round(damage * critical))
                return damage
            return 0
        return 0

    if player.id == ctx.author.id:
        await ctx.send("You can't duel yourself!", hidden=True)
        return
    message = await ctx.send("<@" + str(player.id) + ">, <@" + str(ctx.author.id) + "> Has challegened you to a duel!",
                             components=[Button(label="Accept", color="green"), Button(label="Deny", color="red")])
    try:
        btn = await message.wait_for("button", client, by=player, timeout=20)
    except asyncio.TimeoutError:
        await ctx.send(str(player.display_name) + " did not respond")
        return
    if btn.component.label.lower() == "deny":
        await ctx.send(str(player.display_name) + " has denied your request to duel.")
        await btn.respond()
        return
    else:
        await btn.respond()
        plr = open_account(ctx.author)
        item_bonuses = handle_items(plr.equipped)
        plr2 = open_account(player)
        item_bonuses2 = handle_items(plr2.equipped)
        health = plr.maxhealth
        health2 = plr2.maxhealth

        def check_users(inter):
            if inter.author.id in players:
                return True
            return False

        def make_embed(footer):
            embed = discord.Embed(
                title=f"{plr.name}  HP: {health}/{plr.maxhealth}  |\|  {plr2.name}  HP: {health2}/{plr2.health}",
                color=0xff0099)
            embed.add_field(name="Attack", value="High chance of hitting, enemy also gets an attack", inline=False)
            embed.add_field(name="Counter", value="A good chance you counter the next attack, a small chance you lose "
                                                  "attack opportunity", inline=False)
            embed.set_footer(text=footer)
            return embed

        msg = await ctx.send(embed=make_embed("Get ready!"),
                             components=[Button(label="Attack", color="red"), Button(label="Counter")])
        while health >= 0 and health2 >= 0:
            players = [player.id, ctx.author.id]
            try:
                btn = await msg.wait_for("button", client, check=check_users, timeout=20)
            except asyncio.TimeoutError:
                await ctx.send(f"Neither of you responded, stalemate")
                return
            players.remove(btn.author.id)
            await btn.respond()
            try:
                btn2 = await msg.wait_for("button", client, check=check_users, timeout=20)
            except asyncio.TimeoutError:
                name = await client.fetch_user(players[0])
                await ctx.send(f"{name.display_name} did not respond, they lost")
                return

            dmg = get_attack(30 + item_bonuses2["togethit"] + item_bonuses["tohit"],
                             plr.maxdamage + item_bonuses2["enemydamage"])
            dmg2 = get_attack(30 + item_bonuses["togethit"] + item_bonuses2["tohit"],
                              plr.maxdamage + item_bonuses["enemydamage"])
            if btn.component.label.lower() == "attack" and btn2.component.label.lower() == "counter":
                outcome = random.randint(1, 100)
                if outcome <= 10:
                    dmg2 = math.ceil(dmg / 4)
                    dmg = math.ceil(dmg / 2)
                elif 42 >= outcome > 10:
                    dmg2 = math.ceil(dmg / 2)
                else:
                    dmg2 = 0
            elif btn.component.label.lower() == "counter" and btn2.component.label.lower() == "attack":
                outcome = random.randint(1, 100)
                if outcome <= 10:
                    dmg = math.ceil(dmg2 / 4)
                    dmg2 = math.ceil(dmg2 / 2)
                elif 42 >= outcome > 10:
                    dmg = math.ceil(dmg2 / 2)
                else:
                    dmg = 0
            health -= dmg2
            health2 -= dmg
            if dmg != 0:
                dmgstr = f"{plr.name} dealt {dmg} damage\n"
                if dmg > plr.maxdamage:
                    dmgstr = f"{plr.name} dealt {dmg} damage, CRITCAL!\n"
            else:
                dmgstr = f"{plr.name} missed!\n"
            if dmg2 != 0:
                if dmg2 > plr2.maxdamage:
                    dmgstr += f"{plr2.name} dealt {dmg2} damage, CRITCAL!"
                else:
                    dmgstr += f"{plr2.name} dealt {dmg2} damage"
            else:
                dmgstr += f"{plr2.name} missed!"
            await msg.edit(embed=make_embed(dmgstr),
                           components=[Button(label="Attack", color="red"), Button(label="Counter")])
            await btn2.respond()
        if health2 <= 0:
            embed = discord.Embed(title=f"{plr.name} Won!  HP: {health}/{plr.maxhealth}",
                                  description=f"{plr2.name}: 0/{plr2.maxhealth}", color=0xff0099)
            await msg.edit(embed=embed)
        elif health <= 0:
            embed = discord.Embed(title=f"{plr2.name} Won!  HP: {health2}/{plr2.maxhealth}",
                                  description=f"{plr.name}: 0/{plr.maxhealth}", color=0xff0099)
            await msg.edit(embed=embed)


async def on_victory(player, enemy, message, area):
    item = random.randint(1, 100)
    item_bonuses = handle_items(player.equipped)
    killsper = player.kills.split(", ")
    killsper[area - 1] = str(int(killsper[area - 1]) + 1)
    player.kills = ", ".join(killsper)
    enemy.xp = int(round(enemy.xp * (1 + item_bonuses["xp"]))) * 2
    xpbonus = (1 + item_bonuses["xp"]) * 2
    embed = discord.Embed(title=f"{enemy.name} has been defeated!  HP: 0/{enemy.health}",
                          description=f"{player.name}: {player.health}/{player.maxhealth}\n\n+{enemy.coins} Coins\n+{enemy.xp} XP ({xpbonus}x)",
                          color=0xff0099)
    if item <= 7:
        if area == 1:
            items = ["Wood Sword", "Wood Shield", "Wood Armor"]
            if item == 2:
                items = ["Aluminium Sword", "Aluminium Shield", "Aluminium Armor"]
        if area == 2:
            items = ["Spiky Sword", "Serrated Shield", "Thorn Armor"]
            if item == 2:
                items = ["Spiky Sword", "Serrated Shield", "Thorn Armor"]
        item = random.choice(items)
        items = player.inventory.split(", ")
        items.append(item)
        if items[0] != '':
            player.inventory = ", ".join(items)
        else:
            player.inventory = item
        embed.add_field(name="You got an item!", value="+1 " + item)
    await message.edit(embed=embed)
    player.xp += enemy.xp
    while player.xp >= xp_for_level(player.level + 1):
        player.level += 1
        player.maxhealth += 5
        player.health += 5
        player.xp -= xp_for_level(player.level)
        update_account(player)
        await message.channel.send(
            "<@" + str(player.userid) + "> Levelled up!\n+5 Max Health\nNew Level: " + str(player.level))
    player.coins += enemy.coins
    update_account(player)


async def on_death(player, enemy, message, health):
    embed = discord.Embed(title=f"You lost to {enemy.name}   HP: {health}/{enemy.health}",
                          description=f"1 Death has been added to your death count and you lost level progress",
                          color=0xff0099)
    player.deaths += 1
    player.xp = 0
    player.health = player.maxhealth
    update_account(player)
    await message.edit(embed=embed)


client.run(token)
