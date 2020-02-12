# Redditmends
A product recommendation engine that uses ML models on real Reddit reviews, using Microsoft Azure.

## Purpose
Redditmends bot is a reddit bot that will parse Reddit submissions, comments, and private messages for users requesting a reccomendation for a certain product and return reccomendations using ML models based on real reddit data.

## To-Do
### Reddit Manager
- [x] ~~Setup connection to PRAW~~
- [x] ~~Implement functionality for calling [pushshift.io] API~~
- [ ] RSS reading for subreddits
- [ ] Parse bot inbox for private message reccomendation requests
- [ ] Send message and comment replies with recommendations

### Database
- [x] ~~Setup database to store reddit data that is fed into ML model (Azure Storage Table)~~

### ML Model
- [x] ~~Utilize Azure Cognitive services to extract comments for keywords, sentiment analysis, and identify entities~~

### Add-Ons
- [x] ~~Implement Azure Keyvault to store and access secrets~~
- [ ] Custom logger (Azure Log Analytics)
- [ ] Custom exception handler and trace events (Azure App Insights)
- [ ] Bot stats (number of searches, accuracy, uptime, etc.)
- [ ] Requirements file to easily install package dependencies

### Web App
- [ ] Create Flask based RESTful API for Redditmends
- [ ] Create front-end UI based on Flask API
- [ ] Create Doxygen (or similar) API documentation

## Acknowledgements
Special thanks to [Watchful1's RemindMeBot](https://github.com/Watchful1/RemindMeBot) and [TylerBrockett's Alert-Bot-Reddit](https://github.com/tylerbrockett/Alert-Bot-Reddit) for the inspiration, and to [dwyl's english-words](https://github.com/dwyl/english-words) for the English dictionary json.
