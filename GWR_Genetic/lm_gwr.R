library(ggplot2)
#library(rsq)
library(rlist)
library(spgwr)

#Following Guide:
#https://rstudio-pubs-static.s3.amazonaws.com/44975_0342ec49f925426fa16ebcdc28210118.html

args = commandArgs(trailingOnly=TRUE)
print("Running GWR on the following variables: ")
clean_args = c()
for(i in 1:length(args)){
	clean_args <- c(clean_args,gsub("c","",args[i]))
}
print(clean_args)
vec = c()
for(i in 1:length(args)){
	vec <- c(vec, args[i])
}
variables <- paste(vec, collapse = "+")
formula <- as.formula(paste0("Calls ~ ",variables, sep=""))
setwd("./")
Sample <- read.csv("temp.csv")

attach(Sample)

#Calculates the linear model
model1 <- lm(formula, data = Sample)
cat("Linear Model (OLS) R-squared: ",summary(model1)$adj.r.squared, '\n')

#Writes the R2 value from linear model to lm.txt
#sink("lm.txt")
#print(summary(model1))
#sink()

#Calculates teh GWR bandwidth
GWRbandwidth <- gwr.sel(formula, data=Sample, coords=cbind(x,y),adapt=T) #This create the bandwith
#Calculates the GWR model
gwr.model = gwr(formula, data=Sample, coords=cbind(x,y), adapt=GWRbandwidth, hatmatrix=TRUE, se.fit=TRUE)
#Saves the model to res to be written to csv later
res <- as.data.frame(gwr.model$SDF)

#Writes the result of GWR to a txt file
#sink("gwr.txt")
#print(gwr.model)
#sink()

#Writes the model to a csv for future calculations
write.csv(res, file="GWRmodel.csv")

#Calculating quasi global R2 value
qGlobalR2 <- (1 - (gwr.model$results$rss/gwr.model$gTSS))

#Writing to a file
write.csv(qGlobalR2, file = "qGlobalR2.csv")
