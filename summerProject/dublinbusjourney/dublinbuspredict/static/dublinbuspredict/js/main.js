window.onload = function(){
    openNav();
    closeNav();
    googleTranslateElementInit();
    clickForms();
};

// functions for opening and closing navbar
function openNav() {
        if (document.getElementById("mySidenav").style.width === '0px') {
            document.getElementById("mySidenav").style.width = "250px";
        } else {
            document.getElementById("mySidenav").style.width = "0px"; 
        }
}

function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
}


//functions to load in google language bar
function googleTranslateElementInit() {
    new google.translate.TranslateElement({pageLanguage: 'en', 
    includedLanguages: 'en,es,fr,it,ja,ko,pt,ru',
    layout: google.translate.TranslateElement.InlineLayout.SIMPLE}, 
    'google_translate_element');
			}

// function for loading in twitter data from python script for AA roadwatch. 
// The last 9 tweets displayed from the account.
function loadTwitter(){
	   var text = $.getJSON("http://127.0.0.1:8000/dublinbuspredict/getTwitterText", null, function(d) {
	   for (i = 0; i < 10; i++){
	       var twitterText = d['text'][i];
	       if (typeof twitterText !== 'undefined'){
	           if (twitterText.includes("http")){
	           var https_find = twitterText.indexOf("http")
	           twitterText=twitterText.substring(0,https_find)
	           if(twitterText.lastIndexOf(".") !==-1)
	               twitterText=twitterText.substring(0,twitterText.lastIndexOf(".")+1)
	            var twitterTime=d['create_time'][i]
	           var length = twitterTime.length
	            twitterTime=twitterTime.substring(0,length-10)
	            document.getElementById('tweet'+(i+1)).innerHTML = "<b><i class='fa fa-twitter fa-fw'></i>&nbsp;Update:&nbsp;</b>" 
	                +twitterTime+"<br><br>"+twitterText;
	           }
	           else{
	               twitterText=twitterText.substring(0,twitterText.lastIndexOf(".")+1)
	               var twitterTime=d['create_time'][i]
	               var length = twitterTime.length
	               twitterTime=twitterTime.substring(0,length-10)
	               document.getElementById('tweet'+(i+1)).innerHTML = "<b><i class='fa fa-twitter fa-fw'></i>&nbsp;Update:&nbsp;</b>"
	                   +twitterTime+"<br><br>"+twitterText;
	           }
	       }            
	   }
	   }
	 )};
