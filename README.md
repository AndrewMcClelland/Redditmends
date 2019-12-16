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
- [ ] Send message and comment replies with reccomendation

### Database
- [x] ~~Setup database to store reddit data that is fed into ML model (Azure Storage Table)~~

### ML Model
- [x] ~~Utilize Azure Cognitive services to extract comments for keywords, sentiment analysis, and identify entities~~

### Add-Ons
- [x] ~~Implement Azure Keyvault to store and access secrets~~
- [ ] Custom logger
- [ ] Custom exception handler
- [ ] Bot stats (number of searches, accuracy, uptime, etc.)
- [ ] Requirements file to easily install package dependencies

### Web App
- [ ] Front-end UI that uses same backend engine but offers clean website interface

## Acknowledgements
Special thanks to [Watchful1's RemindMeBot](https://github.com/Watchful1/RemindMeBot) and [TylerBrockett's Alert-Bot-Reddit](https://github.com/tylerbrockett/Alert-Bot-Reddit) for the inspiration.
