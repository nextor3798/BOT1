import sys
import os
from dotenv import load_dotenv 
sys.path.append("C:\\Users\\Admin\\AppData\\Local\\Packages\\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\\LocalCache\\local-packages\\Python313\\site-packages")
import discord # type: ignore
import openai # type: ignore
openai.api_key = "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"
from discord import app_commands # type: ignore
import random
from discord.ext import commands, tasks # type: ignore
from keep_alive import keep_alive # type: ignore

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True  # Activer l'intention de lecture des messages

bot = commands.Bot(command_prefix="!", intents=intents)


TICKET_CATEGORY_ID = 1371081335095169054  # Remplace par l'ID de la catégorie des tickets

@bot.tree.command(name="ticket", description="Créer un ticket de support")
async def ticket(interaction: discord.Interaction):
    guild = interaction.guild
    category = discord.utils.get(guild.categories, id=TICKET_CATEGORY_ID)

    # Créer un salon avec le nom du ticket
    channel = await guild.create_text_channel(f"ticket-{interaction.user.name}", category=category)

    # Définir les permissions pour que seul l'utilisateur et l'équipe du serveur aient accès
    await channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
    await channel.set_permissions(guild.default_role, read_messages=False)

    # Envoyer un message de confirmation
    await interaction.response.send_message(f"🎫 Ton ticket a été créé ici : {channel.mention}", ephemeral=True)
    await channel.send(f"👋 Bonjour <@{interaction.user.id}>, ton ticket est ouvert ! L'équipe va te répondre bientôt.")

class CloseTicketView(discord.ui.View):
    def __init__(self, channel):
        super().__init__(timeout=None)
        self.channel = channel

    @discord.ui.button(label="🔒 Fermer le Ticket", style=discord.ButtonStyle.danger)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Vérifie si l'utilisateur a un rôle staff avant de fermer le ticket"""
        staff_roles = ["Staff", ""]  # Remplace par les noms exacts des rôles staff

        # Vérifier si l'utilisateur a un rôle staff
        user_roles = [role.name for role in interaction.user.roles]
        if not any(role in user_roles for role in staff_roles):
            await interaction.response.send_message("❌ Seuls les membres du staff peuvent fermer un ticket.", ephemeral=True)
            return

        # Fermer le ticket si l'utilisateur est autorisé
        await interaction.response.send_message("🔒 Ticket fermé. Ce salon va être supprimé dans quelques secondes.", ephemeral=True)
        await self.channel.delete()

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Ouvrir un Ticket", style=discord.ButtonStyle.primary)
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, id=TICKET_CATEGORY_ID)

        # Créer un salon privé
        channel = await guild.create_text_channel(f"ticket-{interaction.user.name}", category=category)
        await channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
        await channel.set_permissions(guild.default_role, read_messages=False)

        # Envoyer un message avec le bouton pour fermer le ticket
        await channel.send(f"<@{interaction.user.id}>", view=CloseTicketView(channel))

        await interaction.response.send_message(f"🎫 Ton ticket a été créé ici : {channel.mention}", ephemeral=True)
        
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Dictionnaire de réponses automatiques
    dialogues = {
        "bonjour": [
            "👋 Salut ! Comment va notre explorateur aujourd'hui ?",
            "🌴 Bienvenue sur l'île ! Que puis-je faire pour toi ?",
            "Hey ! Toujours prêt pour l'aventure ?",
            "Coucou ! Tu veux discuter ?",
            "Hello ! Content de te voir ici."
        ],
        "salut": [
            "Salut à toi !",
            "Hello ! Comment puis-je t'aider ?",
            "Hey hey !",
            "Bienvenue sur le serveur !"
        ],
        "ca va": [
            "Oui, et toi ?",
            "Super bien, merci !",
            "Toujours la pêche sur l'île !",
            "Je vais bien, prêt à discuter !"
        ],
        "merci": [
            "Avec plaisir !",
            "De rien, c'est normal !",
            "Toujours là pour aider !",
            "N'hésite pas si tu as d'autres questions."
        ],
        "île commu": [
            "🌊 L'île va super bien ! Et toi ?",
            "🏝️ Toujours prête à accueillir les plus courageux !",
            "🔥 Une île pleine de mystère et de fun !",
            "L'île communautaire, c'est la famille !"
        ],
        "raconte moi une blague": [
            "😂 Pourquoi les poissons ne vont jamais à l'école ? Parce qu'ils ont peur des filets !",
            "🤣 Qu'est-ce qu'un pirate préfère boire ? Du rhum ! Toujours du rhum !",
            "😆 Pourquoi les tortues aiment les réseaux sociaux ? Parce qu'elles prennent leur temps pour poster !",
            "Pourquoi les mouettes volent au bord de la mer ? Parce que sinon ce seraient des poulettes !"
        ],
        "donne moi un conseil": [
            "💡 Un vrai aventurier ne recule jamais devant les défis !",
            "🔥 Même les tempêtes passent. Tiens bon, tout va s'arranger !",
            "💙 Respire un bon coup, détends-toi, et continue d’avancer !",
            "N'oublie pas de t'hydrater et de prendre soin de toi !"
        ],
        "j'ai un coup de blues": [
            "💙 Je suis là pour toi ! Imagine-toi sur une plage, les vagues caressent le sable...",
            "🌞 Parfois la pluie tombe, mais derrière chaque nuage, il y a toujours le soleil !",
            "🌴 Si tu veux parler, je suis là pour toi ! Même les plus forts ont besoin d'un boost parfois !",
            "Courage, les beaux jours reviennent toujours !"
        ],
        "recommande moi un jeu": [
            "🎮 Tu devrais essayer *Sea of Thieves* ! Parfait pour une aventure en mer !",
            "🕹️ Pourquoi pas *Minecraft* ? Une île paradisiaque, tu peux l’explorer à l’infini !",
            "⚔️ *Zelda: Wind Waker* serait un bon choix, naviguer entre les îles, c’est génial !",
            "Test *Animal Crossing*, c'est détente et fun !"
        ],
        "tu fais quoi": [
            "Je veille sur le serveur et je discute avec les membres !",
            "J'attends qu'on me parle pour aider ou rigoler !",
            "Je prépare des cocotiers virtuels pour l'équipe !"
        ],
        "quel est ton film préféré": [
            "🎬 J’adore *Pirates des Caraïbes* !",
            "📽️ *Moana*, elle est prête pour l’aventure comme toi !",
            "🍿 *Cast Away* : une vraie histoire de survie !"
        ],
        "coucou": [
            "Coucou à toi !",
            "Coucou ! Comment vas-tu ?",
            "Coucou, prêt pour l'aventure ?"
        ],
        "bonne nuit": [
            "Bonne nuit ! Fais de beaux rêves sur l'île !",
            "Repose-toi bien, à demain !",
            "Bonne nuit, l'aventurier !"
        ],
        "bonne journée": [
            "Merci, toi aussi !",
            "Passe une excellente journée !",
            "Que ta journée soit remplie de soleil !"
        ],
        "aide": [
            "Tu as besoin d'aide ? Pose-moi ta question !",
            "Je suis là pour t'aider, dis-moi tout.",
            "Explique-moi ton souci, je vais essayer de t'aider."
        ],
        "mdr": [
            "Content de t'avoir fait rire !",
            "Haha, je suis drôle parfois !",
            "😂"
        ],
        "lol": [
            "Haha, tu m'as fait sourire !",
            "Toujours dans la bonne humeur ici !",
            "😄"
        ],
        "ok": [
            "Parfait !",
            "Super !",
            "Ça marche !"
        ],
        "test": [
            "Je suis bien là !",
            "Test réussi !",
            "Oui, je fonctionne !"
        ]
        # Ajoute encore plus de mots-clés et réponses ici si tu veux !
    }

    # Cherche un mot-clé dans le message
    for mot, reponses in dialogues.items():
        if mot in message.content.lower():
            await message.channel.send(random.choice(reponses))
            return

    await bot.process_commands(message)

@bot.tree.command(name="serveurs", description="Affiche le nombre de serveurs")
async def serveurs(interaction: discord.Interaction):
    await interaction.response.send_message(f"🔗 Je suis connecté à {len(bot.guilds)} serveur(s) !")

@bot.tree.command(name="kick", description="Expulse un membre du serveur")
@app_commands.describe(member="Le membre à expulser", reason="La raison de l'expulsion")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    if interaction.user.guild_permissions.kick_members:
        await member.kick(reason=reason)
        await interaction.response.send_message(f"👢 {member.mention} a été expulsé du serveur !")
    else:
        await interaction.response.send_message("❌ Tu n'as pas la permission d'expulser des membres.", ephemeral=True)

@bot.tree.command(name="ban", description="Bannit un membre du serveur")
@app_commands.describe(member="Le membre à bannir", reason="La raison du bannissement")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    if interaction.user.guild_permissions.ban_members:
        await member.ban(reason=reason)
        await interaction.response.send_message(f"🚫 {member.mention} a été banni du serveur !")
    else:
        await interaction.response.send_message("❌ Tu n'as pas la permission de bannir des membres.", ephemeral=True)

@bot.tree.command(name="unban", description="Débannit un membre du serveur")
@app_commands.describe(member="Le membre à débannir")
async def unban(interaction: discord.Interaction, member: discord.User):
    if interaction.user.guild_permissions.ban_members:
        guild = interaction.guild
        banned_users = await guild.bans()
        for ban_entry in banned_users:
            if ban_entry.user.id == member.id:
                await guild.unban(member)
                await interaction.response.send_message(f"🔓 {member.mention} a été débanni du serveur !")
                return
        await interaction.response.send_message(f"❌ {member.mention} n'est pas banni.")
    else:
        await interaction.response.send_message("❌ Tu n'as pas la permission de débannir des membres.", ephemeral=True)

@bot.tree.command(name="mute", description="Mute un membre du serveur")
@app_commands.describe(member="Le membre à mute", reason="La raison du mute")
async def mute(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    if interaction.user.guild_permissions.manage_roles:
        mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if mute_role is None:
            mute_role = await interaction.guild.create_role(name="Muted")
            for channel in interaction.guild.channels:
                await channel.set_permissions(mute_role, speak=False, send_messages=False, read_messages=True)
        await member.add_roles(mute_role, reason=reason)
        await interaction.response.send_message(
            f"🔇 {member.mention} a été mute !\nRaison : {reason if reason else 'Aucune'}"
        )
    else:
        await interaction.response.send_message("❌ Tu n'as pas la permission de mute des membres.", ephemeral=True)

@bot.tree.command(name="unmute", description="Unmute un membre du serveur")
@app_commands.describe(member="Le membre à unmute")
async def unmute(interaction: discord.Interaction, member: discord.Member):
    if interaction.user.guild_permissions.manage_roles:
        mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if mute_role in member.roles:
            await member.remove_roles(mute_role)
            await interaction.response.send_message(f"🔊 {member.mention} a été unmute !")
        else:
            await interaction.response.send_message(f"❌ {member.mention} n'est pas mute.")
    else:
        await interaction.response.send_message("❌ Tu n'as pas la permission de unmute des membres.", ephemeral=True)

@bot.tree.command(name="kick_all", description="Expulse tous les membres du serveur")
async def kick_all(interaction: discord.Interaction):
    if interaction.user.guild_permissions.kick_members:
        for member in interaction.guild.members:
            if not member.bot:
                try:
                    await member.kick(reason="Expulsé par le bot.")
                    await interaction.channel.send(f"👢 {member.mention} a été expulsé du serveur !")
                except discord.Forbidden:
                    await interaction.channel.send(f"❌ Je n'ai pas la permission d'expulser {member.mention}.")
                except discord.HTTPException:
                    await interaction.channel.send(f"❌ Impossible d'expulser {member.mention}.")
    else:
        await interaction.response.send_message("❌ Tu n'as pas la permission d'expulser des membres.", ephemeral=True)

@bot.tree.command(name="ban_all", description="Bannit tous les membres du serveur")
async def ban_all(interaction: discord.Interaction):
    if interaction.user.guild_permissions.ban_members:
        for member in interaction.guild.members:
            if not member.bot:
                try:
                    await member.ban(reason="Banni par le bot.")
                    await interaction.channel.send(f"🚫 {member.mention} a été banni du serveur !")
                except discord.Forbidden:
                    await interaction.channel.send(f"❌ Je n'ai pas la permission de bannir {member.mention}.")
                except discord.HTTPException:
                    await interaction.channel.send(f"❌ Impossible de bannir {member.mention}.")
    else:
        await interaction.response.send_message("❌ Tu n'as pas la permission de bannir des membres.", ephemeral=True)

@bot.tree.command(name="unban_all", description="Débannit tous les membres du serveur")
async def unban_all(interaction: discord.Interaction):
    if interaction.user.guild_permissions.ban_members:
        banned_users = await interaction.guild.bans()
        for ban_entry in banned_users:
            user = ban_entry.user
            try:
                await interaction.guild.unban(user)
                await interaction.channel.send(f"🔓 {user.mention} a été débanni du serveur !")
            except discord.Forbidden:
                await interaction.channel.send(f"❌ Je n'ai pas la permission de débannir {user.mention}.")
            except discord.HTTPException:
                await interaction.channel.send(f"❌ Impossible de débannir {user.mention}.")
    else:
        await interaction.response.send_message("❌ Tu n'as pas la permission de débannir des membres.", ephemeral=True)

@bot.tree.command(name="kick_all_bots", description="Expulse tous les bots du serveur")
async def kick_all_bots(interaction: discord.Interaction):
    if interaction.user.guild_permissions.kick_members:
        for member in interaction.guild.members:
            if member.bot:
                try:
                    await member.kick(reason="Expulsé par le bot.")
                    await interaction.channel.send(f"👢 {member.mention} a été expulsé du serveur !")
                except discord.Forbidden:
                    await interaction.channel.send(f"❌ Je n'ai pas la permission d'expulser {member.mention}.")
                except discord.HTTPException:
                    await interaction.channel.send(f"❌ Impossible d'expulser {member.mention}.")
    else:
        await interaction.response.send_message("❌ Tu n'as pas la permission d'expulser des membres.", ephemeral=True)

@bot.tree.command(name="ban_all_bots", description="Bannit tous les bots du serveur")
async def ban_all_bots(interaction: discord.Interaction):
    if interaction.user.guild_permissions.ban_members:
        for member in interaction.guild.members:
            if member.bot:
                try:
                    await member.ban(reason="Banni par le bot.")
                    await interaction.channel.send(f"🚫 {member.mention} a été banni du serveur !")
                except discord.Forbidden:
                    await interaction.channel.send(f"❌ Je n'ai pas la permission de bannir {member.mention}.")
                except discord.HTTPException:
                    await interaction.channel.send(f"❌ Impossible de bannir {member.mention}.")
    else:
        await interaction.response.send_message("❌ Tu n'as pas la permission de bannir des membres.", ephemeral=True)

@bot.tree.command(name="unban_all_bots", description="Débannit tous les bots du serveur")
async def unban_all_bots(interaction: discord.Interaction):
    if interaction.user.guild_permissions.ban_members:
        banned_users = await interaction.guild.bans()
        for ban_entry in banned_users:
            user = ban_entry.user
            if user.bot:
                try:
                    await interaction.guild.unban(user)
                    await interaction.channel.send(f"🔓 {user.mention} a été débanni du serveur !")
                except discord.Forbidden:
                    await interaction.channel.send(f"❌ Je n'ai pas la permission de débannir {user.mention}.")
                except discord.HTTPException:
                    await interaction.channel.send(f"❌ Impossible de débannir {user.mention}.")
    else:
        await interaction.response.send_message("❌ Tu n'as pas la permission de débannir des membres.", ephemeral=True)

@bot.tree.command(name="clear_all", description="Supprime tous les messages du salon actuel")
async def clear_all(interaction: discord.Interaction):
    if interaction.user.guild_permissions.manage_messages:
        await interaction.channel.purge(limit=None)
        await interaction.response.send_message("🗑️ Tous les messages ont été supprimés !", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Tu n'as pas la permission de supprimer des messages.", ephemeral=True)

@bot.tree.command(name="clear_all_bots", description="Supprime tous les messages des bots dans le salon actuel")
async def clear_all_bots(interaction: discord.Interaction):
    if interaction.user.guild_permissions.manage_messages:
        def is_bot(message):
            return message.author.bot
        deleted = await interaction.channel.purge(limit=None, check=is_bot)
        await interaction.response.send_message(f"🗑️ {len(deleted)} message(s) de bot supprimé(s) !", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Tu n'as pas la permission de supprimer des messages.", ephemeral=True)

@bot.tree.command(name="clear_all_users", description="Supprime tous les messages des utilisateurs dans le salon actuel")
async def clear_all_users(interaction: discord.Interaction):
    if interaction.user.guild_permissions.manage_messages:
        def is_user(message):
            return not message.author.bot
        deleted = await interaction.channel.purge(limit=None, check=is_user)
        await interaction.response.send_message(f"🗑️ {len(deleted)} message(s) d'utilisateur supprimé(s) !", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Tu n'as pas la permission de supprimer des messages.", ephemeral=True)

@bot.tree.command(name="clear_all_except_bots", description="Supprime tous les messages sauf ceux des bots dans le salon actuel")
async def clear_all_except_bots(interaction: discord.Interaction):
    if interaction.user.guild_permissions.manage_messages:
        def is_not_bot(message):
            return not message.author.bot
        deleted = await interaction.channel.purge(limit=None, check=is_not_bot)
        await interaction.response.send_message(f"🗑️ {len(deleted)} message(s) d'utilisateur supprimé(s) !", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Tu n'as pas la permission de supprimer des messages.", ephemeral=True)

@bot.tree.command(name="clear_all_except_users", description="Supprime tous les messages sauf ceux des utilisateurs dans le salon actuel")
async def clear_all_except_users(interaction: discord.Interaction):
    if interaction.user.guild_permissions.manage_messages:
        def is_not_user(message):
            return message.author.bot
        deleted = await interaction.channel.purge(limit=None, check=is_not_user)
        await interaction.response.send_message(f"🗑️ {len(deleted)} message(s) de bot supprimé(s) !", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Tu n'as pas la permission de supprimer des messages.", ephemeral=True)

@bot.tree.command(name="clear_all_except_bots_and_users", description="Supprime tous les messages sauf ceux des bots et des utilisateurs dans le salon actuel")
async def clear_all_except_bots_and_users(interaction: discord.Interaction):
    if interaction.user.guild_permissions.manage_messages:
        def is_not_bot_or_user(message):
            return message.author.bot or not message.author.bot
        deleted = await interaction.channel.purge(limit=None, check=is_not_bot_or_user)
        await interaction.response.send_message(f"🗑️ {len(deleted)} message(s) supprimé(s) !", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Tu n'as pas la permission de supprimer des messages.", ephemeral=True)

@bot.tree.command(name="test", description="Vérifie si le bot est en ligne")
async def test(interaction: discord.Interaction):
    await interaction.response.send_message("✅ Je suis bien en ligne et je peux parler !", ephemeral=True)

@bot.command()
async def ticket_setup(ctx):
    """Commande pour afficher le bouton de création de ticket."""
    view = TicketView()
    await ctx.send("**Tu veux avoir accès au reste du serveur ? Viens te faire vérifier !**", view=view)
    await ctx.message.delete()

@bot.tree.command(name="test_ticket", description="Commande pour tester le système de ticket")
async def test_ticket(interaction: discord.Interaction):
    view = TicketView()
    await interaction.response.send_message("Clique sur le bouton ci-dessous :", view=view, ephemeral=True)


@bot.tree.command(name="test_button", description="Commande pour tester si le bouton s'affiche")
async def test_button(interaction: discord.Interaction):
    view = TicketView()
    await interaction.response.send_message("Clique sur le bouton ci-dessous :", view=view, ephemeral=True)


@bot.tree.command(name="close", description="Fermer un ticket")
async def close(interaction: discord.Interaction):
    """Ferme un ticket en supprimant le salon."""
    if interaction.channel.category_id == TICKET_CATEGORY_ID:
        await interaction.response.send_message("🔒 Fermeture du ticket en cours...", ephemeral=True)
        await interaction.channel.delete()
    else:
        await interaction.response.send_message("❌ Ce n'est pas un ticket valide.", ephemeral=True)



# Liste des salons où la suppression doit s'appliquer (remplace par tes IDs)
SALONS_AUTORISES = [1353723434538111070, 1353723535528296468, 1353723535528296468, 1353723663932719115, 1353723874264481822, 1353723966174265497, 1353724189592522804, 1353724298883239986, 1353724845887848520, 1353724579352416256, 1353724982898982972, 1353725292509663304, 1353725397048492032, 1349074361507774665, 1357760001770262698, 1357761088573407515,
                    1313936922325815349, 1313937151091675269, 1313936610223722496, 1313936610223722496, 1313936772857856080, 1313937127029084160, 1313936849655562282, 1313936800099864606, 1313936683716182116, 1313936724321243197, 1313936876192661504, 1313974516409700393, 1357760533696348432, 
                    1313578832137289758, 1342199151680557196, 1313578926962118657, 1313578796133126255, 1313578956334829609, 1313578860876398622, 1313578895647178874, 1316775777051611136, 1322612666098909195, 1341772031116709950, 1349074140564291718, 1357760409976700968, 1357760933132239130, 
                    1352332565322928128, 1312723908431974444, 1312724477796159519, 1313936639260885093, ]

TICKET_CATEGORY_ID = 1371081335095169054  # ID de la catégorie où les tickets sont créés

@bot.event
async def on_guild_channel_create(channel):
    if isinstance(channel, discord.TextChannel) and channel.category_id == TICKET_CATEGORY_ID:
        async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_create, limit=1):
            creator_id = entry.user.id  # Récupérer l'ID du créateur du salon
            await channel.send(f"""👋 Bonjour, !

Afin de respecter les règles de notre serveur et garantir un environnement sécurisé, nous procédons à une vérification d'âge des membres.  
                               
Pour confirmer votre majorité, veuillez fournir une preuve d'identité avec les informations suivantes visibles :  
- Votre pseudonyme  
- Votre date de naissance  
- Un document officiel (carte d'identité, passeport, permis de conduire) avec les autres informations floutées.  

Vos données resteront confidentielles et utilisées uniquement à des fins de vérification.  

Merci de votre compréhension et de votre coopération.  

Cordialement,  
L'île communautaire.""")

@bot.event
async def on_ready():
    synced_commands = await bot.tree.sync()  # Synchroniser les commandes slash
    print(f"✅ {len(synced_commands)} commandes slash synchronisées !")

keep_alive()  # Démarrer le serveur Flask
bot.run("MTM3MjMxOTAxMTE4MTgyNjE1OQ.GTqo1-.bZA-3Sl1uBsahUyA5pSWrKINRRrv2VeFugS0lA")  # Remplace par ton token