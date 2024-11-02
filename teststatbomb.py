#import packages (statsbombpy, mplsoccer & highlight_text need to be installed w/ "pip install" command)
from statsbombpy import sb
import pandas as pd
from mplsoccer import Pitch
from mplsoccer import VerticalPitch,Pitch

from highlight_text import ax_text, fig_text
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import seaborn as sns

#call statsbombpy API to get all free competitions
free_comps = sb.competitions()

#select two seasons of ligue 1 (2021/2022 and 2022/2023)
ligue1_22_23 = sb.matches(competition_id=7, season_id=235)
ligue1_21_22 = sb.matches(competition_id=7, season_id=108)

print(ligue1_21_22.axes)