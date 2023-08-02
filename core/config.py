
import os 

USERNAME = None
if not USERNAME:
    raise ValueError("You MUST set your username in core/config.py")

HOME_DIR = "/home/%s" % USERNAME
ORCA_INSTALL_FOLDER ="%s/Orca" % HOME_DIR
PCC_USPACE_INSTALL_FOLDER = '%s/PCC-Uspace' % HOME_DIR
PCC_RL_INSTALL_FOLDER = '%s/PCC-RL' % HOME_DIR

# Since the python script is run as root, you need to explicitly provide the user for 
# for user level calls






