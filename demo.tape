# Renders demo.gif for README.md. Requires: vhs, tmux, fzf, python3.
# Run from the repo root: vhs demo.tape

Output demo.gif

Require tmux
Require fzf
Require python3

Set Shell "bash"
Set FontSize 15
Set Width 1500
Set Height 800
Set Theme "Dracula"
Set Padding 20
Set TypingSpeed 60ms

Hide
Type "tmux -L vhsdemo -f /dev/null new-session -d -s demo -x 150 -y 40"
Enter
Type "tmux -L vhsdemo run-shell $PWD/main.tmux"
Enter
Type "clear && tmux -L vhsdemo attach -t demo"
Enter
Sleep 1s
Show

# prefix + A opens the source picker in a popup
Ctrl+B
Type "A"
Sleep 1500ms

# Choose the Claude Code library source
Type "claude"
Sleep 1000ms
Enter
Sleep 1000ms

# Filter to one prompt and preview it
Type "review your changes"
Sleep 1200ms
Enter
Sleep 1500ms

# Choose Paste
Type "paste"
Sleep 800ms
Enter
Sleep 2s

Hide
Type "tmux -L vhsdemo kill-server"
Enter
Show
