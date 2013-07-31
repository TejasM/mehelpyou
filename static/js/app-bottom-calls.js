$(document).ready(function() {
    $('#twitter').jTweetsAnywhere({
        username: 'ignitethemes',
       
        count: 2,
        showTweetFeed: {
            showUserFullNames: false,
            showSource: false,
            showActionReply: false,
            showActionRetweet: false,
            showActionFavorite: false,
			showProfileImages: false,
            paging: {
                mode: 'none'
            }
        }
    });
});
	
