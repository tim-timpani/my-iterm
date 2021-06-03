# My iTerm2
iTerm2 features and customizations I use daily. I use this repo
for introducing people to iTerm and provide some examples of how
I implement it.  This is only scratching the surface. For more
information refer to the documentation https://iterm2.com/documentation.html

## Table of Contents
* [Installation](#installation)
* [Shell Integration](#shell-integration)
* [Status Bar](#status-bar)
* [Custom Profiles](#custom-profiles)
* [Python Scripts](#python-scripts)
* [User Variables](#user-variables)
* [Fix Forward/Back Word](#fix-forwardback-word)
* [Keyboard Shortcuts](#keyboard-shortcuts)

## Installation
Install iTerm2 by going to https://iterm2.com/downloads.html
	
## Shell Integration
Many features such as current working directory, command history,
etc require shell integration. Instructions are here: https://iterm2.com/documentation-shell-integration.html
The following should be added in your ~/.bashrc or ~/.zshrc file accordingly
```
test -e "${HOME}/.iterm2_shell_integration.zsh" && source "${HOME}/.iterm2_shell_integration.zsh"
```
	
## Status Bar
All my window profiles use these items in the status bar.
* Snippets - so I can quickly paste in a command
* Full path current directory
* git branch (if applicable)
* Tools - shows/hides the "Toolbelt" (side panel) 

The status bar can be configured for each profile
* Go to preferences and click on the profiles tab
* Select the desired profile
* Under Miscellaneous, enable and configure the status bar
* Drag the desired status bar items down to Active Components.

## Custom Profiles
Custom Profiles allow task-specific customizations.
For example, when dealing with different K8s cloud providers,
different environment variables, aliases, search path, 
tools, and K8s versions may be needed.  To accomplish this,
I created bash scripts to customize the environment
(such as KUBECONFIG variable) for each iTerm profile.
See my GKE example scripts/example_gke_env.
* Create a new profile in preferences, profiles
* Click on the + to create a profile
* Set a useful Name
* Set the Title--I use Profile (Job)
* In "Send text at start" enter a command to source the bash script
followed by \n
* Optionally set the directory to where it should start
* Optionally click on the Colors tab and set a unique color
  which helps find the tab quickly

New tabs with the configured profile can be created using
keyboard shortcuts, the "Profiles" add on to the Tool belt,
or the Profiles menu.

## Python Scripts
iTerm2 supports automation through Python scripts that run externally
or internal into iTerm that can customize iTerm in real time.
For details, refer to the documentation https://iterm2.com/documentation-scripting-fundamentals.html
* Internal scripts can be managed through the scripts menu within
  iTerm. See example scripts/color_tabs.py.
* External scripts are run outside of iTerm but can still 
  interact with it. See example scripts/iterm_window.py.

## User Variables
iTerm has many built-in variables (https://iterm2.com/documentation-variables.html),
but user variables can also be added via the ~/.bashrc or
~/.zshrc file. For example:
```
iterm2_print_user_vars() {
  iterm2_set_user_var virtualEnv $VIRTUAL_ENV
  iterm2_set_user_var gitBranch $((git branch 2> /dev/null) | grep \* | cut -c3-)
  iterm2_set_user_var home $(echo -n "$HOME")
}
```
These variables can then be referenced by Python scripts loaded into iTerm
for example, to access the virtualEnv variable above, the script would use
```
virtual_env = iterm2.Reference("user.virtualEnv?")
```

## Fix Forward/Back Word
In the Apple Terminal app, you can move forward and back by words
using Option/Arrow keys.  This is especially helpful when pasting
a complex command and then changing some arguments.
By default, iTerm does not support this feature. To enable it:
* Go to preferences and click on the profiles tab
* Select the desired profile
* Under Keys, click the Presets dropdown and select Terminal.app
Compatibility.
  
## Keyboard Shortcuts
Keyboard shortcuts can be added to all profiles which can be
programmed for navigation but also can send text to the current
window.  This is accessed through preferences, keys.  I use the
"Send Text" to change to the polaris and whelp folders.
* Go to preferences and click on the Keys tab
* Click on the + to add a keybaord shortcut
* Use the Click to Set and then press the shortcut combination.
* Set the Action to "Send Text"
* Enter the value to send (remember to add \n if desired)
* Click on Ok

*IMPORTANT NOTE*:  The Mac has many built-in keyboard shortcuts
which may conflict with user defined shortcuts.
The Ctrl-Cmd sequence seems to have the least conflict
