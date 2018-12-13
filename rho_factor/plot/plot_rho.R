
source( './ggplot2_perso.R')

dir = "../rho_factor/"

rho_m1999 = read.csv(paste0(dir,'data/aux/rhoTable_Mobley1999.csv'), skip=7)
rho_m2015 = read.csv(paste0(dir,'data/aux/rhoTable_Mobley2015.csv'), skip=8)

files=c(paste0(dir,"rho_values/surface_reflectance_factor_rho_fine_aerosol_rg0.06_sig0.46.csv"),
        paste0(dir,"rho_values/surface_reflectance_factor_rho_coarse_aerosol_rg0.60_sig0.60.csv"))

wl_palette <- c( "blue", "springgreen","springgreen", "orange","orange", "red3","gray")
Palette = colorRampPalette(wl_palette)

label_parseall <- function(variable, value) {
  plyr::llply(value, function(x) parse(text = paste(variable, 
                                                    x, sep = "==")))
}
sza = c(0,20,40,60,80)
sza = c(20,30,40,50,60)
rho_m1999 = rho_m1999[ rho_m1999$wind %in% c(0,2,5,10) & rho_m1999$sza %in% sza,]
rho_m2015 = rho_m2015[ rho_m2015$wind %in% c(0,2,5,10) & rho_m2015$sza %in% sza,]

for(file in files){
  filename = sub('.*/','',sub('.csv$', '', file))
  df<-read.csv(file)
  
  for(vza in c(30,40,50)){
    for(azi in c(90,135)){
      dff = df[df$vza==vza & df$azi==azi & df$aot %in% c(0.0001,0.1,0.5,1.0) & df$sza %in% sza ,]
      ggplot(dff,aes(x=wl,y=rho,color=aot,group=aot,linetype="OSOAA"))+
        theme_perso(base_size = 15)+
        geom_abline(data=rho_m1999[rho_m1999$vza==vza & rho_m1999$azi ==azi ,],aes(slope=0,intercept=rho,linetype="M1999"))+
        geom_abline(data=rho_m2015[rho_m2015$vza==vza & rho_m2015$azi ==azi ,],aes(slope=0,intercept=rho,linetype="M2015"))+
        geom_line()+geom_point()+#geom_line(aes(y=rho_g),linetype=2)+
        facet_grid(wind~sza,labeller = label_parseall)+#,scales = "free")+
        scale_colour_gradientn(colors=Palette(30),limits=c(0, 1),name="AOT")+
        ylab(expression("Surface reflectance factor "*italic(rho)))+xlab(expression("Wavelength (nm)"))+
          ggtitle(paste0(filename,", vza=",as.character(vza),"°, azi=",as.character(azi),"°"))+
        #ylim(0,ceiling(max(dff$rho)*100)/100)+
        # scale_colour_manual(name="Rho", values = c("a" = "black", "b" = "red", "c" = "blue")) +
        scale_linetype_manual(name="Rho",values=c("OSOAA"=1, "M1999"=2, "M2015"=3))
        
      ggsave(paste0(dir,"fig_henrique/rho_",filename,"_vza",as.character(vza),"_azi",as.character(azi),".png"),width = 14,height = 9)
}}}