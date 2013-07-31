// Twitter

jQuery(document).ready(function(){
    jQuery('#tweetFeed').jTweetsAnywhere({username: 'wpbox',count: 2,
        showTweetFeed: {
            showProfileImages: false,
            showUserScreenNames: false,
            showUserFullNames: true,
            showActionReply: false,
            showActionRetweet: false,
            showActionFavorite: false
        },
        showTweetBox: {
            label: '<span style="color: #303030">Spread the word ...</span>'
        }
    });
	jQuery('#tweetSidebar').jTweetsAnywhere({
        username: 'wpbox',
        count: 2,
        showTweetFeed: {
            showProfileImages: false,
            showUserScreenNames: false,
            showUserFullNames: true,
            showActionReply: false,
            showActionRetweet: false,
            showActionFavorite: false
        }
      
    });
});


// BACK TO TOP
  
$(document).ready(function(){
	/*
        $(window).scroll(function(){
            if ($(this).scrollTop() > 100) {
                $('.scrollup').fadeIn();
            } else {
                $('.scrollup').fadeOut();
            }
        });
 
        $('.scrollup').click(function(){
            $("html, body").animate({ scrollTop: 0 }, 600);
            return false;
        });
	*/
});
