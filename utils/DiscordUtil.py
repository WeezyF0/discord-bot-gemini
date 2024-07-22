import configs.DefaultConfig as defaulConfig
def is_me(ctx):
    return ctx.author.id == int(defaulConfig.DISCORD_OWNER_ID)
