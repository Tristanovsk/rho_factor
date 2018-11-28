
source( '/DATA/R/ggplot2_perso.R')

dir = "/DATA/OBS2CO/app/rho_factor/"

files=c(paste0(dir,"rho_values/surface_reflectance_factor_rho_fine_aerosol_rg0.06_sig0.46.csv"),
        paste0(dir,"rho_values/surface_reflectance_factor_rho_coarse_aerosol_rg0.60_sig0.60.csv"))

wl_palette <- c( "blue", "springgreen","springgreen", "orange","orange", "red3","gray")
Palette = colorRampPalette(wl_palette)

label_parseall <- function(variable, value) {
  plyr::llply(value, function(x) parse(text = paste(variable, 
                                                    x, sep = "==")))
}

for(file in files){
  filename = sub('.*/','',sub('.csv$', '', file))
  df<-read.csv(file)
  
  
  ggplot(df[df$vza>39 & df$vza<41 & df$azi==90 & df$aot %in% c(0.0001,0.1,0.5,1.0) & df$sza %in% c(0,20,40,60,80),],aes(x=wl,y=rho,color=aot,group=aot))+
    theme_perso(base_size = 15)+geom_line()+geom_point()+#geom_line(aes(y=rho_g),linetype=2)+
    facet_grid(wind~sza,labeller = label_parseall)+scale_colour_gradientn(colors=Palette(30),limits=c(0, 1),name="AOT")+
    ylab(expression("Surface reflectance factor "*italic(rho)))+xlab(expression("Wavelength (nm)"))+ggtitle(paste0(filename,", vza=40°, azi=90°"))
  ggsave(paste0(dir,"fig/",filename,'.png'),width = 18,height = 10)
}