#!/usr/bin/env python3

# ========== LIBRARIES ========== #
from prettytable import PrettyTable



# ========== FUNCTIONS ========== #
def colorize(c,t):
    colors = {
        "PURPLE": '\033[95m',
        "BLUE": '\033[94m',
        "CYAN": '\033[96m',
        "GREEN": '\033[92m',
        "YELLOW": '\033[93m',
        "RED": '\033[91m',
        "BOLD": '\033[1m',
        "UNDERLINE": '\033[4m'
    }

    if c not in colors:
        return t
    else:
        return (colors[c] + str(t) + '\033[0m')


# ========== MAIN ========== #
if __name__ == '__main__':
    tbl = PrettyTable([colorize("BOLD",colorize("PURPLE",'Command')), colorize("BOLD",colorize("PURPLE",'Description'))])
    tbl.align[colorize("BOLD",colorize("PURPLE",'Description'))] = "l"
    tbl.align[colorize("BOLD",colorize("PURPLE",'Command'))] = "r"
    tbl.add_row([colorize("PURPLE",'kw-sensor'),'Runs the KegWatch sensor in the background'])
    tbl.add_row([colorize("PURPLE",'kw-sensor-f'),'Runs the KegWatch sensor in the foreground'])
    tbl.add_row([colorize("PURPLE",'kw-cal'),'Calibration utility to calculate flow rate'])
    tbl.add_row([colorize("PURPLE",'kw-keg'),'Keg management utility to view & add kegs'])
    tbl.add_row([colorize("PURPLE",'kw-swtst'), 'Switch test utility that will display switch state'])
    tbl.add_row([colorize("PURPLE",'kw-users'),'User management utility to add, modify, or delete users'])
    
    print(colorize("BOLD","\nKegWatch Command List"))
    print(tbl)
    print()