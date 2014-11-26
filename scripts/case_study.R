#!/usr/bin/env Rscript
myarg <- commandArgs(TRUE)
wd <- myarg[1]
csv_file <- myarg[2]

setwd(wd)

raw_df = read.csv(csv_file)
means = apply(raw_df, 2, mean)
medians = apply(raw_df, 2, median)
sds = apply(raw_df, 2, sd)

latency = raw_df[,1] - raw_df[,2]

cloud_latency = raw_df[,3] - raw_df[,2]

pdf('detours_graphs.pdf', onefile=TRUE)

barplot(means, axes=TRUE, col=c('lightblue'),
    main='Mean execution time of each strategy', xlab='Strategies',
    ylab='Execution Time in secs', width=.2, xlim=c(0,1), ylim=c(0, 85))

points <- seq(from=.14, to=.62, by=.24)

text(points, 0, round(means, 2), cex=1, pos=3)

# dev.off()

# pdf('detours_graphs.pdf', onefile=TRUE)

barplot(medians, axes=TRUE, col=c('yellow'),
    main='Median execution time of each strategy', xlab='Strategies',
    ylab='Execution Time in secs', width=.2, xlim=c(0,1), ylim=c(0, 85))

# points <- seq(from=.14, to=.86, by=.24)

text(points, 0, round(medians, 2), cex=1, pos=3)

# Latency plot
par(mfrow=c(2,1))
barplot(latency,
    main='Framework latency (on.premise - local)', col=c('lightblue'), xlab='Iterations',
    ylab='Time in secs')

barplot(cloud_latency,
    main='Cloud latency (google.std - local)', col=c('red'), xlab='Iterations',
    ylab='Time in secs')

# Cloud Latency

# Analysis
par(mfrow=c(2,2))
boxplot(raw_df[,1], main='On.premise', boxwex=.3)
boxplot(raw_df[,2], main='Local.std', boxwex=.3)
boxplot(raw_df[,3], main='google.opt', boxwex=.3)
boxplot(latency, main='Latency analysis (on.premise - local)',
    ylab='Time in seconds', col=c(16), boxwex=.5, ylim=c(0.19, 0.24))

par(mfrow=c(1,1))
boxplot(cloud_latency, main='Latency analysis (google.std - local)',
    ylab='Time in seconds', col=c(16), boxwex=.5)




dev.off()

# # Mean of each execution
# png('mean_elapsed_time.png', width=640, res=100)

# # mp <- barplot(means, axes=TRUE, col=c('red', 'yellow', 'deepskyblue', 'lightblue'),
# #      main='Mean execution time of each strategy', xlab='Strategies',
# #      ylab='Execution Time in secs', ylim=c(0, 90))
# barplot(means, axes=TRUE, col=c('lightblue'),
#     main='Mean execution time of each strategy', xlab='Strategies',
#     ylab='Execution Time in secs', width=.2, xlim=c(0,1), ylim=c(0, 85))

# # mp <- barplot(means, axes=TRUE, col=c('lightblue'),
# #      main='Mean execution time of each strategy', xlab='Strategies',
# #      ylab='Execution Time in secs', width=.1, xlim=c(0,1), ylim=c(0, 90), space=2)

# points <- seq(from=.14, to=.62, by=.24)

# text(points, 0, round(means, 2), cex=1, pos=3)

# dev.off()

# png('medan_elapsed_time.png', width=640, res=100)

# barplot(medians, axes=TRUE, col=c('yellow'),
#     main='Median execution time of each strategy', xlab='Strategies',
#     ylab='Execution Time in secs', width=.2, xlim=c(0,1), ylim=c(0, 85))

# # points <- seq(from=.14, to=.86, by=.24)

# text(points, 0, round(medians, 2), cex=1, pos=3)

# dev.off()





