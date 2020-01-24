# https://github.com/pushshift/api#search-parameters-for-submissions

# 'parameter' : ['description', 'default value', 'accepted values']

pushshift_api_parameters = {

	# Comment Search Parameters
	'comment': {
		'q': ['Search term.', 'N/A', 'String / Quoted String for phrases'],
		'ids': ['Get specific comments via their ids', 'N/A', 'Comma-delimited base36 ids'],
		'size': ['Number of results to return', '25', 'Integer <= 500'],
		'fields': ['One return specific fields (comma delimited)', 'All Fields Returned', 'string or comma-delimited string'],
		'sort': ['Sort results in a specific order', 'desc', 'asc, "desc"'],
		'sort_type': ['Sort by a specific attribute', 'created_utc', 'score, "num_comments", "created_utc"'],
		'aggs': ['Return aggregation summary', 'N/A', '["author", "link_id", "created_utc", "subreddit"]'],
		'author': ['Restrict to a specific author', 'N/A', 'String'],
		'subreddit': ['Restrict to a specific subreddit', 'N/A', 'String'],
		'after': ['Return results after this date', 'N/A', 'Epoch value or Integer + "s,m,h,d" (i.e. 30d for 30 days)'],
		'before': ['Return results before this date', 'N/A', 'Epoch value or Integer + "s,m,h,d" (i.e. 30d for 30 days)'],
		'frequency': ['Used with the aggs parameter when set to created_utc', 'N/A', 'second, "minute", "hour", "day"'],
		'metadata': ['display metadata about the query', 'false', 'true, "false"']
	},

	# Submission Search Parameters
	'submission': {
		'ids': ['Get specific submissions via their ids', 'N/A', 'Comma-delimited base36 ids'],
		'q': ['Search term. Will search ALL possible fields', 'N/A', 'String / Quoted String for phrases'],
		'q:not': ['Exclude search term. Will exclude these terms', 'N/A', 'String / Quoted String for phrases'],
		'title': ['Searches the title field only', 'N/A', 'String / Quoted String for phrases'],
		'title:not': ['Exclude search term from title. Will exclude these terms', 'N/A', 'String / Quoted String for phrases'],
		'selftext': ['Searches the selftext field only', 'N/A', 'String / Quoted String for phrases'],
		'selftext:not': ['Exclude search term from selftext. Will exclude these terms', 'N/A', 'String / Quoted String for phrases'],
		'size': ['Number of results to return', '25', 'Integer <= 500'],
		'fields': ['One return specific fields (comma delimited)', 'All Fields', 'String or comma-delimited string (Multiple values allowed)'],
		'sort': ['Sort results in a specific order', 'desc', 'asc, "desc"'],
		'sort_type': ['Sort by a specific attribute', 'created_utc', 'score, "num_comments", "created_utc"'],
		'aggs': ['Return aggregation summary', 'N/A', '["author", "link_id", "created_utc", "subreddit"]'],
		'author': ['Restrict to a specific author', 'N/A', 'String or comma-delimited string (Multiple values allowed)'],
		'subreddit': ['Restrict to a specific subreddit', 'N/A', 'String or comma-delimited string (Multiple values allowed)'],
		'after': ['Return results after this date', 'N/A', 'Epoch value or Integer + "s,m,h,d" (i.e. 30d for 30 days)'],
		'before': ['Return results before this date', 'N/A', 'Epoch value or Integer + "s,m,h,d" (i.e. 30d for 30 days)'],
		'score': ['Restrict results based on score', 'N/A', 'Integer or > x or < x (i.e. score=>100 or score=<25)'],
		'num_comments': ['Restrict results based on number of comments', 'N/A', 'Integer or > x or < x (i.e. num_comments=>100)'],
		'over_18': ['Restrict to nsfw or sfw content', 'both allowed', 'true or "false"'],
		'is_video': ['Restrict to video content', 'both allowed', 'true or "false"'],
		'locked': ['Return locked or unlocked threads only', 'both allowed', 'true or "false"'],
		'stickied': ['Return stickied or unstickied content only', 'both allowed', 'true or "false"'],
		'spoiler': ['Exclude or include spoilers only', 'both allowed', 'true or "false"'],
		'contest_mode': ['Exclude or include content mode submissions', 'both allowed', 'true or "false"'],
		'frequency': ['Used with the aggs parameter when set to created_utc', 'N/A', 'second, "minute", "hour", "day"'],
		'metadata': ['display metadata about the query', 'false', '["true", "false"]']
	}
}