import asyncio
import iterm2


# Default color preset names for light & dark modes
# NOTE(dabrady) Makes it easier to make broad changes
DEFAULT_DARK = 'ayu'
DEFAULT_LIGHT = 'ayu_light'

# Mapping of desired color presets to profiles
# NOTE(dabardy) Makes it easier to make targeted changes
PREFERRED_PROFILE_PRESETS = {
    'main': { 'dark': DEFAULT_DARK, 'light': DEFAULT_LIGHT },
    'sidebar': { 'dark': DEFAULT_DARK, 'light': DEFAULT_LIGHT },
    'emacs': { 'dark': DEFAULT_DARK, 'light': DEFAULT_LIGHT },
}


async def _get_profiles(connection):
    return [
        profile
        for profile in (await iterm2.PartialProfile.async_query(
                connection=connection,
                properties=["Guid", "Name"]
        ))
        # Filter out profiles we don't care about
        if profile.name in PREFERRED_PROFILE_PRESETS
    ]


async def _make_adjuster(connection):
    profiles = await _get_profiles(connection)

    async def adjust_profile_colors(system_theme):
        print(f"Adjusting profiles to {system_theme} color preset")
        for profile in profiles:
            preferred_preset = PREFERRED_PROFILE_PRESETS\
                .get(profile.name, {})\
                .get(system_theme, None)
            if preferred_preset is None:
                continue

            preset = await iterm2.ColorPreset.async_get(connection, preferred_preset)
            await profile.async_set_color_preset(preset)

    return adjust_profile_colors


async def main(connection):
    adjust_profile_colors = await _make_adjuster(connection)

    async with iterm2.VariableMonitor(
            connection, iterm2.VariableScopes.APP, "effectiveTheme", None
    ) as monitor:
        while True:
            system_theme = await monitor.async_get()
            await adjust_profile_colors(system_theme)


iterm2.run_forever(main)
