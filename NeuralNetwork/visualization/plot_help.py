import seaborn as sns
import matplotlib as mpl
import matplotlib.font_manager


# Font Montserrat
montserrat = [xx for xx in matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf') 
              if "Montserrat" in xx]


# Corporative Palette
colors = ["#ffd13fff", "#00a082ff", "#434343ff", "#d9d9d9ff"]

# Extra large palette for plotting multiple colors (courtesy of: https://coolors.co/)
colors_extra = ["#ffd13fff", "#00a082ff", "#434343ff", "#d9d9d9ff",
                
                "#084C61","#DB504A","#E3B505","#4F6D7A","#56A3A6",
                "#524948","#57467B","#7CB4B8","#70F8BA","#CAFE48","#CCD7C5","#EFD2CB","#C7A27C",
                "#D65780","#EE9480","#82FF9E","#935FA7","#153243","#B4B8AB","#F4F9E9","#EEF0EB",
                "#586F7C","#F4F4F9","#9AD1D4","#003249","#A09ABC","#D5CFE1","#E1DEE9","#D4BEBE",
                "#646E78","#8D98A7","#DCCCBB","#EAB464","#A7754D","#413620","#9C6615","#9F7833",
                "#FFD791","#F5EFFF","#A594F9","#7371FC","#9A7197","#886176","#EFF1C5","#035E7B",
                "#002E2C","#CBD081","#918868","#FF1053","#6C6EA0","#66C7F4","#C1CAD6","#403233",
                "#6A706E","#B8B8FF","#FFEEDD","#FFD8BE","#0B0033","#370031","#832232","#CE8964","#EAF27C"
                ]

# Plot colors
#sns.palplot(colors_extra)

# Set the stype referencing rcParams (all changes to rcParams should be done AFTER THAT)
sns.set(rc = mpl.rcParams, font = "Montserrat", palette=sns.color_palette(colors))

# Style and Fonts
mpl.rcParams["font.family"] = "Montserrat"
mpl.rcParams["font.weight"] = "semibold"

#Grid
mpl.rcParams["axes.grid"] = True
mpl.rcParams["grid.linestyle"] = "--"
mpl.rcParams["grid.linewidth"] = 1.5
mpl.rcParams["grid.alpha"] = 0.8

# Axes
mpl.rcParams["axes.edgecolor"] =  colors[2]

# Colors
mpl.rcParams["grid.color"] =  colors[3]
mpl.rcParams["axes.facecolor"] =  "white"

# Size of font
mpl.rcParams["font.size"] = 15
mpl.rcParams["axes.labelsize"] = 15
mpl.rcParams["axes.titlesize"] = 15

#Ticks
mpl.rcParams["xtick.labelsize"] = 13
mpl.rcParams["ytick.labelsize"] = 13


# Font weights
mpl.rcParams["axes.titleweight"] = "semibold"
mpl.rcParams["axes.labelweight"] = "semibold"

# Legend
mpl.rcParams["legend.fontsize"] = 14
mpl.rcParams["legend.title_fontsize"] = 20
mpl.rcParams["patch.edgecolor"] = colors[2]

