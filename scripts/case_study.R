#!/usr/bin/env Rscript
myarg <- commandArgs(TRUE)
wd <- myarg[1]
csv_file <- myarg[2]

setwd(wd)

raw_df = read.csv(csv_file)
means = apply(raw_df, 2, mean)
medians = apply(raw_df, 2, median)
sds = apply(raw_df, 2, sd)

latency = raw_df[,2] - raw_df[,1]

cloud_latency = raw_df[,3] - raw_df[,2]

pdf('detours_graphs.pdf', onefile=TRUE)

par(mfrow=c(2,1))

mean_points <- barplot(means, axes=TRUE, col=c('lightblue'),
    main='Mean execution time of each strategy', xlab='Strategies',
    ylab='Execution Time in secs', cex.axis=.8, width=.1, xlim=c(0,1))

# points <- seq(from=.14, to=.62, by=.24)
# axis(1, at=mean_points, labels = FALSE)
# text(mean_points, par("usr")[1] - 3.3, labels = names(means), cex=.9, srt = 25, pos = 1, xpd = TRUE)
text(mean_points, 0, round(means, 2), cex=1, pos=3)

# dev.off()

# pdf('detours_graphs.pdf', onefile=TRUE)

median_points <- barplot(medians, axes=TRUE, col=c('yellow'),
    main='Median execution time of each strategy', xlab='Strategies',
    ylab='Execution Time in secs', cex.axis=.8, width=.1, xlim=c(0,1))

# points <- seq(from=.14, to=.86, by=.24)

text(mean_points, 0, round(medians, 2), cex=1, pos=3)

# Latency plot
par(mfrow=c(2,1))
lat <- barplot(latency,
    main='Framework latency (local - on.premise)', col=c('lightblue'), xlab='Iterations',
    ylab='Time in secs')

#text(lat, 0, round(latency, 2), cex=0.3, pos=3)

clat <- barplot(cloud_latency,
    main='Cloud latency (google.std - local)', col=c('red'), xlab='Iterations',
    ylab='Time in secs')
#text(clat, 0, round(cloud_latency, 2), cex=0.3, pos=3)

# Cloud Latency
# par(mfrow=c(1,1))
# loged = apply(raw_df, 2, log2)
# boxplot(loged, main='On.premise', boxwex=.3)
# Analysis
par(mfrow=c(2,2))
boxplot(raw_df[,1], main='On.premise', boxwex=.3)
boxplot(raw_df[,2], main='Local.std', boxwex=.3)
boxplot(raw_df[,3], main='google.opt', boxwex=.3)
boxplot(latency, main='Latency analysis (on.premise - local)',
    ylab='Time in seconds', col=c(16), boxwex=.5)

par(mfrow=c(1,1))
boxplot(cloud_latency, main='Latency analysis (google.std - local)',
    ylab='Time in seconds', col=c(16), boxwex=.5)

dev.off()





