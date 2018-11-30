require("grid")
library("ggplot2")
library("scales")
theme_perso<-function (base_size = 12, base_family = "serif") 
{
   theme(axis.line = element_blank(), 
                 axis.text.x = element_text(family = base_family, size = base_size, lineheight = 0.9, vjust = 1,colour = "black"), 
                 axis.text.y = element_text(family = base_family, size = base_size, lineheight = 0.9, hjust = 1,colour = "black"),
                 axis.ticks = element_line(colour = "black", size = 0.8),
                 axis.title.x = element_text(family = base_family, size = base_size*1.1, vjust = 0),
                 axis.title.y = element_text(family = base_family, size = base_size*1.1, angle = 90, vjust = 0.3),
                 axis.ticks.length = unit(0.3,"lines"), 
                 axis.ticks.margin = unit(0.5, "lines"), 
                 legend.background = element_rect(colour = NA),
                 legend.key = element_rect(colour = "grey80"), 
                 legend.key.size = unit(1.6, "lines"), 
                 legend.key.height = NULL, 
                 legend.key.width = NULL,
                 legend.text = element_text(family = base_family, size = base_size ),
                 legend.text.align = NULL, 
                 legend.title = element_text(family = base_family, size = base_size, face = "bold", hjust = 0,vjust=0.3),
                 legend.title.align = NULL, 
                 legend.position = "right", 
                 legend.direction = "vertical", 
                 legend.box = NULL, 
                 panel.background = element_rect(fill = "white", colour = NA),
                 panel.border = element_rect(fill = NA, colour = "black",size=1.5),
                 panel.grid.major = element_line(colour = "grey90", size = 0.2),
                 panel.grid.minor = element_line(colour = "grey98", size = 0.5),
                 panel.margin = unit(1.25, "lines"), 
                 strip.background = element_rect(fill = "white", colour = "black"), 
                 strip.text.x = element_text(family = base_family, size = base_size ),
                 strip.text.y = element_text(family = base_family, size = base_size , angle = -90), 
                 plot.background = element_rect(colour = NA), 
                 plot.title = element_text(family = base_family, size = base_size * 1.2, face="bold"),
                 plot.margin = unit(c(1, 1, 0.5, 0.5), "lines"),
                 strip.text = element_text(face = "italic") #comment if not italic
                 )
}
