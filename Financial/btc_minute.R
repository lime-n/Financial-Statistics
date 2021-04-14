library(tidyverse)
library(lubridate)
library(ranger)
btc <-read_csv("BTC_min.csv")
btc <- data.frame(btc)
btc <- btc %>%
  separate(date, into = c('date', 'time'), sep=" ")
btc <- btc[, -3]
btc$date <- dmy(btc$date)
btc$time <- hm(btc$time)
btc$day <- day(btc$date)
btc$week <- week(btc$date)
btc$minute <- minute(btc$time)
btc$hour <- hour(btc$time)
btc <- btc %>% arrange(date, time)
btc <- btc[btc$date > "2020-12-30",]
btc$diff.closed <- c(0, diff(btc$close, lag=1))
btc$diff.open <- c(0, diff(btc$open, lag=1))
btc$diff.low <- c(0, diff(btc$low, lag=1))
btc$diff.high <- c(0, diff(btc$high, lag=1))
btc <- rowid_to_column(btc)

#10 ranges
#ranges <- function(x, y){
#  st=(max(x)-min(y))/10
#  seq(min(y), max(y), st)
#}

#ranges(btc$diff.open.closed, btc$diff.open.closed)

#closed range
myIntervals <- c("-1700.000 + -1410.162","-1410.162 + -120.324","-120.324 + -830.486","-830.486 + -540.648","-540.648 + -250.810","-250.810 + 39.028","39.028 + 328.866","328.866 + 618.704","618.704 + 908.542","908.542 + 1198.380")
btc$closed.range<- myIntervals[findInterval(btc$diff.closed, c(-1700, -1410.162, -1120.324, -830.486, -540.648, -250.810, 39.028, 328.866, 618.704, 908.542, 1199))]

#open range
myIntervals <- c("-1921.980  + -1607.239","-1607.239  + -1292.498","-1292.498 + -977.757","-977.757 + -663.016","-663.016 + -348.275","-348.275 + -33.534","-33.534 + 281.207","281.207 + 595.948","595.948 + 910.689","910.689 + 1225.430")
btc$open.range<- myIntervals[findInterval(btc$diff.open, c(-1922,-1607.239,-1292.498,-977.757,-663.016,-348.275,-33.534, 281.207, 595.948, 910.689, 1225.43))]

#difference between open and closed changes
btc$open.closed <- btc$open - btc$close
btc$diff.open.closed<- c(0, diff(btc$open.closed, lag=1))


myIntervals <- c("-781.700 + -2326.728 ","-2326.728  + -1871.756","-1871.756 + -1416.784","-1416.784 + -961.812","-961.812 + -506.840","-506.840 + -51.868","-51.868 + 403.104","403.104 + 858.076","858.076 + 1313.048","1313.048 + 1768.020")
btc$open.closed.range<- myIntervals[findInterval(btc$diff.open.closed, c(-2782, -2326.728, -1871.756, -1416.784, -961.812, -506.840, -51.868, 403.104, 858.076, 1313.048, 1769))]




#test <- btc %>% count(open.range, day) %>% group_by(day)
#test <- btc %>% count(closed.range,open.range, day) %>% group_by(day)




# split 80/20

test <- btc %>% 
  # select only the columns to be used in the model
  select(open.closed.range, diff.open.closed, diff.open, diff.closed, day, week, minute, hour)%>% 
  drop_na()


#detection_freq <- mean(test_split$train$n)
#test_split$train$n <- factor(test_split$train$n)
#test_split$train$open.closed.range <- as.factor(test_split$train$open.closed.range)

test$open.closed.range <- as.factor(test$open.closed.range)

#test$open.closed.range2 <- factor(test$open.closed.range, levels=levels(test$open.closed.range)[order(as.numeric(gsub("( +.*)", "", levels(test$open.closed.range))))])
#test <- test[order(test$open.closed.range2), ]
#test$open.closed.range <- NULL



test_split <- test %>% 
  split(if_else(runif(nrow(.)) <= 0.8, "train", "test"))
map_int(test_split, nrow)

rf <- ranger(formula =  open.closed.range ~ ., 
             data = test_split$train,
             importance = "impurity",
             probability = TRUE,
             replace = TRUE)

predict_rf <- predict(rf, data = test, type = "response")

data <- as.data.frame(predict_rf$predictions)
#colnames(data)<- c("-1000 + -500","-1500 + -1000","-2000 + -1500","-2500 + -2000","-3000 + -2500","-3500 + -3000","-4000 + -3500","-4500 + -4000","-500 + 0","-5000 + -4500","-5500 + -5000","-6000 + -5500","-7000 + -6500","-7500 + -7000","0 + 500","1000 + 1500","1500 + 2000","2000 + 2500","2500 + 3000","3000 + 3500","3500 + 4000","4000 + 4500","500 + 1000","5000 + 5500","5500 + 6000")
#cat(paste(names(data), 1:length(names(data))),sep="\n")
#data <- data[, c(14, 13, 12, 11, 10, 8, 7, 6, 5, 4, 3, 2, 1, 9, 15, 23, 16, 17, 18, 19, 20, 21, 22, 24, 25)]
#data <- data.frame(data)
#colnames(data)<- c("-7500 + -7000","-7000 + -6500","-6000 + -5500","-5500 + -5000","-5000 + -4500","-4500 + -4000","-4000 + -3500","-3500 + -3000","-3000 + -2500","-2500 + -2000","-2000 + -1500","-1500 + -1000","-1000 + -500","-500 + 0","0 + 500","500 + 1000","1000 + 1500","1500 + 2000","2000 + 2500","2500 + 3000","3000 + 3500","3500 + 4000","4500 + 5000","5000 + 5500","5500 + 6000")

#colnames(data) <- c("-x7500","-x7000","-x6000","-x5500","-x5000","-x4500","-x4000","-x3500","-x3000","-x2500","-x2000","-x1500","-x1000","-x500","x0","x500","x1000","x1500","x2000","x2500","x3000","x3500","x4500","x5000","x5500")

test.data <- cbind(test, data)
#test.data$date <- ymd(test.data$date)
test.data$date <- btc$date
test.data <- test.data %>% pivot_longer(-c(1:8, 18))
test.data$name <- as.factor(test.data$name)
str(test.data)
#test.name <- tibble(name=1:25,
#test.range=c("-7500 + -7000","-7000 + -6500","-6000 + -5500","-5500 + -5000","-5000 + -4500","-4500 + -4000","-4000 + -3500","-3500 + -3000","-3000 + -2500","-2500 + -2000","-2000 + -1500","-1500 + -1000","-1000 + -500","-500 + 0","0 + 500","500 + 1000","1000 + 1500","1500 + 2000","2000 + 2500","2500 + 3000","3000 + 3500","3500 + 4000","4500 + 5000","5000 + 5500","5500 + 6000"))

#test.data$name <- as.numeric(as.factor(test.data$name))
#test.data <- test.data %>% 
#  inner_join(test.name, by = "name") %>% 
#  arrange(open.closed.range) %>% 
#  select(-name)

#test.data$test.range2 <- factor(test.data$test.range, levels=levels(test.data$test.range)[order(as.numeric(gsub("( +.*)", "", levels(test.data$test.range))))])
#test.data <- test.data[order(test.data$test.range2), ]
#test.data$test.range2 <- NULL


brks <- seq(0, 1, 0.11)
cols <- colorRampPalette(c("red4","orange","gold","gray95","lightskyblue","dodgerblue","blue3"))(length(brks)-1) #this is the colour ramp - change the colours as you like, bu make sure they are symetrical around the "gray95", which represents the zero point!

#levels(test.data$name) <- c("-x7500","-x7000","-x6000","-x5500","-x5000","-x4500","-x4000","-x3500","-x3000","-x2500","-x2000","-x1500","-x1000","-x500","x0","x500","x1000","x1500","x2000","x2500","x3000","x3500","x4500","x5000","x5500")
#levels(test.data$name)<- c("-7500 + -7000","-7000 + -6500","-6000 + -5500","-5500 + -5000","-5000 + -4500","-4500 + -4000","-4000 + -3500","-3500 + -3000","-3000 + -2500","-2500 + -2000","-2000 + -1500","-1500 + -1000","-1000 + -500","-500 + 0","0 + 500","500 + 1000","1000 + 1500","1500 + 2000","2000 + 2500","2500 + 3000","3000 + 3500","3500 + 4000","4500 + 5000","5000 + 5500","5500 + 6000")

#test.plot <- ggplot(test.data, aes(x=factor(name), y=value, group=open.closed.range, label=round(value, 1))) + 
#  geom_bar(aes(fill=open.closed.range), stat='identity') +
#  scale_colour_manual(values=cols) +
#  scale_fill_manual(values=cols)+
#  ylab("Counts of Probability values") +
#  xlab("Probability Ranges") +
#  facet_wrap(~open.closed.range, scales="free") +
#  theme_classic() +
#  scale_x_discrete(label = function(x) stringr::str_trunc(x, 12))+
#  theme(
#    axis.title.x=element_text(face="bold", size=13, family="TT Times New Roman"),
#    axis.title.y=element_text(face="bold", size=13, family="TT Times New Roman"),
#    axis.text.x=element_text(face="bold", size =10, family="TT Times New Roman", angle=90), 
#    axis.text.y=element_text(face="bold",  size =10, family="TT Times New Roman"),
#    legend.title=element_blank(),
#    legend.text=element_text(color="black", size =10, face="bold", family="TT Times New Roman"),
#    legend.justification=c(1.2,1),
#    plot.title=element_text(face="bold", size = 18, hjust=0.5, colour = "black"),
#   axis.line=element_blank(),
#  legend.key.height=unit(.1, "cm")
#)


test.april <- test.data[test.data$date >= "2021-04-01",]
#levels(test.april$name)<- c("-7500 + -7000","-7000 + -6500","-6000 + -5500","-5500 + -5000","-5000 + -4500","-4500 + -4000","-4000 + -3500","-3500 + -3000","-3000 + -2500","-2500 + -2000","-2000 + -1500","-1500 + -1000","-1000 + -500","-500 + 0","0 + 500","500 + 1000","1000 + 1500","1500 + 2000","2000 + 2500","2500 + 3000","3000 + 3500","3500 + 4000","4500 + 5000","5000 + 5500","5500 + 6000")

test.plot.bar <- ggplot(test.april, aes(x=name, y=value, group=open.closed.range, label=round(value, 1))) + 
  geom_bar(aes(colour=open.closed.range), stat='identity')+
  scale_colour_manual(values=cols) +
  scale_fill_manual(values=cols)+
  ylab("Counts of Probability values") +
  xlab("Probability Ranges") +
  facet_wrap(~open.closed.range, scales="free") +
  theme_classic() +
  theme(
    axis.title.x=element_text(face="bold", size=13, family="TT Times New Roman"),
    axis.title.y=element_text(face="bold", size=13, family="TT Times New Roman"),
    axis.text.x=element_text(face="bold", size =10, family="TT Times New Roman", angle=90), 
    axis.text.y=element_text(face="bold",  size =10, family="TT Times New Roman"),
    legend.title=element_blank(),
    legend.text=element_text(color="black", size =10, face="bold", family="TT Times New Roman"),
    legend.justification=c(1.2,1),
    plot.title=element_text(face="bold", size = 18, hjust=0.5, colour = "black"),
    axis.line=element_blank(),
    legend.key.height=unit(.1, "cm")
  )


cat(paste(names(data), 1:length(names(data))),sep="\n")

test.plot.line <- ggplot(test.april, aes(x=name, y=value, group=open.closed.range, label=round(value, 1))) + 
  geom_line(aes(colour=open.closed.range)) +
  geom_point(aes(fill=open.closed.range), shape = 21, size = 2, colour="black", stroke = 0.5) +
  scale_colour_manual(values=cols) +
  scale_fill_manual(values=cols)+
  ylab("Counts of Probability values") +
  xlab("Probability Ranges") +
  facet_wrap(~open.closed.range, scales="free") +
  theme_classic() +
  theme(
    axis.title.x=element_text(face="bold", size=13, family="TT Times New Roman"),
    axis.title.y=element_text(face="bold", size=13, family="TT Times New Roman"),
    axis.text.x=element_text(face="bold", size =10, family="TT Times New Roman", angle=90), 
    axis.text.y=element_text(face="bold",  size =10, family="TT Times New Roman"),
    legend.title=element_blank(),
    legend.text=element_text(color="black", size =10, face="bold", family="TT Times New Roman"),
    legend.justification=c(1.2,1),
    plot.title=element_text(face="bold", size = 18, hjust=0.5, colour = "black"),
    axis.line=element_blank(),
    legend.key.height=unit(.1, "cm")
  )
