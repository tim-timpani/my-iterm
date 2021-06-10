#!/usr/bin/env python3

import iterm2
import os

SHELL_JOB_NAME = 'zsh'
HOME = os.getenv('HOME')

# Set the default color for the tab to start with
DEFAULT_COLOR = (0xfe, 0xff, 0xff)

# Convenient dictionary of RGB color values
color_names = {
    'dark teal': (0x00, 0x6b, 0x5e),
    'indigo': (0x20, 0x00, 0x70),
    'dark green': (0x00, 0x3d, 0x00),
    'purple': (0xce, 0x93, 0xd8),
    'yellow': (0xff, 0xf5, 0x9d),
    'green': (0x00, 0xc2, 0x00),
    'red': (0xc9, 0x1b, 0x00),
    'orange': (0xd3, 0x86, 0x02),
    'dark red': (0x53, 0x00, 0x00),
    'blue': (0x03, 0x5d, 0xfc),
    'tangerine': (0xfe, 0x64, 0x03)
}

# The color_paths dictionary defines color changes when current directory is in (or under) the given path
# First match wins
custom_paths = {
    os.path.join(HOME, 'go', 'src', 'github.com', 'NetApp-Polaris', 'polaris', 'whelp'): 'yellow',
    os.path.join(HOME, 'go', 'src', 'github.com', 'NetApp-Polaris', 'polaris'): 'purple'
}

# Some of my custom python packages for more unique coloring when python is running them
python_packages = {
    'astra': 'blue',
    'builder': 'dark teal'
}


# Utility function to set the tab color
async def set_tab_color(session, color):
    color_values = color_names.get(color, DEFAULT_COLOR)
    change = iterm2.LocalWriteOnlyProfile()
    tab_color = iterm2.Color(*color_values)
    change.set_tab_color(tab_color)
    change.set_use_tab_color(True)
    await session.async_set_profile_properties(change)


# Logic to change the tab color based on certain conditions
async def update_tab(connection, session_id, job, cmd, env, path):
    """
    update_tab controls all the logic for deciding which color/title
    to use for the tab.  All variables are passed in from the title
    provider function.
    """

    # Get session and tab objects
    app = await iterm2.async_get_app(connection)
    session = app.get_session_by_id(session_id)
    if session is None:
        raise RuntimeError(f"Unable to find session id {session_id}")

    # Check if python is running
    if job == 'Python':
        for package_name, package_color in python_packages.items():
            if package_name in cmd:
                await set_tab_color(session, package_color)
                return f'{package_name.upper()}'
        # default python tab color
        await set_tab_color(session, 'dark red')
        if env is None:
            env_name = '?env?'
        else:
            env_name = env.rpartition('/')[2]
        return f'PYTHON {env_name}'

    if job == 'lnav':
        await set_tab_color(session, 'orange')
        if len(cmd) > 5:
            lnav_args = f': {cmd[5:]}'
        else:
            lnav_args = ''
        return f'LNAV{lnav_args}'

    if job == SHELL_JOB_NAME:
        for custom_path, custom_color in custom_paths.items():
            if path is not None and path.startswith(custom_path):
                if len(path) > len(custom_path) + 1:
                    sub_path = path[len(custom_path):]
                else:
                    sub_path = ''
                short_name = custom_path.rpartition('/')[2]
                title = f'{short_name.upper()}: {sub_path}'
                await set_tab_color(session, custom_color)
                return title

        # fall back to green for non-custom paths
        await set_tab_color(session, 'green')
        return f'{job} {path}'

    await set_tab_color(session, 'red')
    return cmd


async def main(connection):
    """main function has mostly boilerplate stuff"""

    # mod_title, decorated as a title provider, calls the update_tab function to handle the logic.
    # All needed variables should be added as parameters to mod_title and iTerm will handle
    # populating them.  Note that the reference starting with user. is a user defined variable
    # and requires additional handling to feed the value into it. Those variables are in turn
    # passed to the update_tab function.
    @iterm2.TitleProviderRPC
    async def mod_title(
        session_id=iterm2.Reference("id?"),
        path=iterm2.Reference("path?"),
        job_name=iterm2.Reference("jobName?"),
        cmd=iterm2.Reference("commandLine?"),
        virtual_env=iterm2.Reference("user.virtualEnv?")
    ):

        return await update_tab(
            connection=connection,
            session_id=session_id,
            job=job_name,
            cmd=cmd,
            env=virtual_env,
            path=path
            )

    # Register the title provider function so it can be available in the profile "Title" dropdown
    # display_name and unique_identifier need to be unique.  The display_name is what will show
    # up in the profile Title dropdown.
    await mod_title.async_register(
        connection,
        display_name="Set Tab Titles And Color",
        unique_identifier="com.iterm2.example.color-tabs")


# This instructs the script to run the "main" coroutine and to keep running even after it returns.
iterm2.run_forever(main)
