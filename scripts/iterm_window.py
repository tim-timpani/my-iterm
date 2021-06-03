import re
import iterm2
import AppKit
import time
import asyncio
import logging

logger = logging.getLogger("iterm_window")


def open_iterm_session(session_name: str, window_title: str, command='/bin/sh', send_text=None, width=700, height=300,
                       wait_for_regex='', regex_occurances=1, timeout=300,  poll_delay=1, warn=False):
    """
    Open an iTerm window to run a command: requires iTerm2 to be installed
    :param session_name: Name of the session
    :param window_title: Window title
    :param command: Command to run (defaults to /bin/sh)
    :param send_text: (Optional) text to send to the session
    :param width: Width in pixels for the window
    :param height: Height in pixels for the window
    :param wait_for_regex: (Optional) wait for regex to match before returning
    :param regex_occurances: Number of regex matches needed before returning
    :param timeout: Wait timer in seconds, a TimeoutError exception will be thrown if regex not found
    :param warn: bool Determines if timeout is just a warning, otherwise exception
    :param poll_delay: Polling delay in seconds for checking for regex
    :return:
    """

    # Launch the app
    AppKit.NSWorkspace.sharedWorkspace().launchApplication_("iTerm2")

    async def iterm_main(connection):
        app = await iterm2.async_get_app(connection)

        # Foreground the app
        await app.async_activate()
        myterm = await iterm2.Window.async_create(connection, command=command)

        # Set the frame size
        myframe = await myterm.async_get_frame()
        myframe.size.width = int(width)
        myframe.size.height = int(height)
        await myterm.async_set_frame(myframe)

        await myterm.async_activate()

        # Wait for profiles to be applied before changing color so this will overrirde tab color
        # that might be set by the profile
        await asyncio.sleep(1)

        # Set tab color, window size, and title
        tab = myterm.current_tab
        session = tab.current_session
        change = iterm2.LocalWriteOnlyProfile()
        tab_color = iterm2.Color(0x00, 0x6e, 0x24)
        change.set_tab_color(tab_color)
        change.set_use_tab_color(True)
        change.set_name(session_name)
        await session.async_set_profile_properties(change)
        await tab.window.async_set_title(window_title)

        # Send additional text if provided
        if send_text is not None:
            await session.async_send_text(send_text)

        # Function to search for text so we can easily just return out of it
        async def search_content_for_regex():
            print(f"waiting for content '{wait_for_regex}'")
            start_time = time.time()
            regex_available = re.compile(wait_for_regex)
            while (time.time() - start_time) < timeout:

                # Crazy iTerm line buffer variables to check the output.
                line_info = await session.async_get_line_info()
                (window_height, history, overflow, first) = (
                    line_info.mutable_area_height,
                    line_info.scrollback_buffer_height,
                    line_info.overflow,
                    line_info.first_visible_line_number)
                line_count = window_height + history
                lines = await session.async_get_contents(0, line_count)

                # Search lines for the regex
                occurances_found = 0
                for line in lines:
                    if regex_available.search(line.string):
                        print(f'found content: {wait_for_regex}')
                        occurances_found += 1
                        if occurances_found >= regex_occurances:
                            return
                await asyncio.sleep(poll_delay)

            message = f"Timeout waiting for {window_title }content: {wait_for_regex}"
            if warn:
                logger.warning(message)
                return
            raise TimeoutError(message)

        # Wait for the requested regex to match
        if wait_for_regex != '':
            await search_content_for_regex()

    # Passing True for the second parameter means keep trying to
    # connect until the app launches.
    iterm2.run_until_complete(iterm_main, True)

    return
